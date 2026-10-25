"""Parser integrato per tabelle ufficiali ARERA (formato Excel .xlsx)."""
from __future__ import annotations

import io
import logging
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

_LOGGER = logging.getLogger(__name__)


def _extract_excel_rows(content: bytes) -> tuple[dict[int, dict[str, Any]], list[str]]:
    """Estrae dizionario delle righe e stringhe condivise dal file Excel .xlsx."""
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sstree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sstree:
                strings.append("".join(si.itertext()))

        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in z.namelist():
            sheet_candidates = [
                n
                for n in z.namelist()
                if n.startswith("xl/worksheets/sheet")
                and n.endswith(".xml")
                and "rels" not in n
            ]
            sheet_name = sheet_candidates[0] if sheet_candidates else None

        if not sheet_name:
            raise ValueError("Nessun foglio valido trovato nel file Excel ARERA")

        sheet_tree = ET.fromstring(z.read(sheet_name))
        rows: dict[int, dict[str, Any]] = {}
        for row in sheet_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
            r_num = int(row.attrib["r"])
            rows[r_num] = {}
            for c in row.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                cell_ref = c.attrib.get("r", "")
                col = "".join([ch for ch in cell_ref if ch.isalpha()])
                t = c.attrib.get("t")
                v_elem = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                val = v_elem.text if v_elem is not None else None
                if t == "s" and val is not None:
                    try:
                        val = strings[int(val)]
                    except (IndexError, ValueError):
                        pass
                rows[r_num][col] = val

    return rows, strings


def parse_arera_smt_xlsx(content: bytes) -> dict[str, Any]:
    """Estrae la componente DISPbt dal file Excel ufficiale ARERA SMT (es. E2026-smt.xlsx scaricato dalla rete)."""
    rows, _ = _extract_excel_rows(content)

    dispbt_col = None
    for r in range(15, 20):
        for col, val in rows.get(r, {}).items():
            if val and "dispbt" in str(val).lower():
                dispbt_col = col
                break
        if dispbt_col:
            break

    dispbt_val = None
    if dispbt_col:
        for r in range(18, 25):
            label = str(rows.get(r, {}).get("B", "")).lower()
            if "quota fissa" in label:
                raw = rows.get(r, {}).get(dispbt_col)
                if raw and raw not in ("-", "- ", "", "None"):
                    try:
                        dispbt_val = float(raw)
                    except (ValueError, TypeError):
                        pass
                break

    if dispbt_val is not None:
        _LOGGER.info("Componente DispBT ARERA estratta con successo dalla tabella ufficiale: %s €/anno", dispbt_val)
        return {"dispbt": round(dispbt_val, 4)}

    _LOGGER.warning("Colonna o valore DispBT non trovato nel file SMT ARERA")
    return {}


def parse_arera_xlsx(content: bytes) -> dict[str, Any]:
    """Estrae le tariffe regolate ARERA dal file Excel ufficiale stg_domesticiNonVulnerabili.xlsx o SMT."""
    rows, strings = _extract_excel_rows(content)

    def get_num(r_num: int, col: str, default: float = 0.0) -> float:
        val = rows.get(r_num, {}).get(col)
        if val is None or val in ("-", "- ", "", "None"):
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    # Rilevamento automatico se il file passato contiene la tabella SMT con DISPbt
    for val in rows.get(17, {}).values():
        if val and "dispbt" in str(val).lower():
            return parse_arera_smt_xlsx(content)

    # Parsing tabella STG per clienti residenti
    period = rows.get(19, {}).get("B", "")
    if not period or not isinstance(period, str):
        period = "ARERA Ufficiale"

    data = {
        "today": period.strip(),
        "s1": round(get_num(22, "O", 23.04), 4),
        "s2": round(get_num(23, "P", 23.52), 4),
        "s3": round(get_num(21, "Q", 0.0119), 6),
        "uc3": round(get_num(21, "R", 0.00276), 6),
        "uc6qe": round(get_num(21, "S", 0.00007), 6),
        "uc6qp": round(get_num(23, "S", 0.1988), 4),
        "asos": round(get_num(21, "U", 0.028657), 6),
        "arim": round(get_num(21, "V", 0.001638), 6),
        "cdispd": round(get_num(21, "G", 0.019902), 6),
        "csed": round(get_num(21, "H", 0.00056), 6),
        "cpstgd": round(get_num(21, "I", 0.00214), 6),
        "parametrolamda": round(get_num(22, "J", -73.1637), 4),
    }

    _LOGGER.info("Tariffe ARERA STG estratte con successo per il periodo: %s", period)
    return data
