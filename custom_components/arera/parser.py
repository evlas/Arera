"""Parser integrato per tabelle ufficiali ARERA (formato Excel .xlsx)."""
from __future__ import annotations

import io
import logging
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

_LOGGER = logging.getLogger(__name__)


def parse_arera_xlsx(content: bytes) -> dict[str, Any]:
    """Estrae le tariffe regolate ARERA dal file Excel ufficiale stg_domesticiNonVulnerabili.xlsx."""
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sstree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sstree:
                strings.append("".join(si.itertext()))

        # Legge il foglio più recente (sheet1.xml corrisponde all'ultimo mese inserito da ARERA)
        sheet_name = "xl/worksheets/sheet1.xml"
        if sheet_name not in z.namelist():
            sheet_candidates = [n for n in z.namelist() if n.startswith("xl/worksheets/sheet") and n.endswith(".xml") and "rels" not in n]
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

    def get_num(r_num: int, col: str, default: float = 0.0) -> float:
        val = rows.get(r_num, {}).get(col)
        if val is None or val in ("-", "- ", "", "None"):
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    # Individua il periodo (es. Giugno 2026) da riga 19 col B
    period = rows.get(19, {}).get("B", "")
    if not period or not isinstance(period, str):
        period = "ARERA Ufficiale"

    # Mappatura colonne tabella "Abitazioni di residenza anagrafica":
    # Riga 21: Quota energia
    # Riga 22: Quota fissa
    # Riga 23: Quota potenza
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
        "dispbt": -10.77,
        "cdispd": round(get_num(21, "G", 0.019902), 6),
        "csed": round(get_num(21, "H", 0.00056), 6),
        "cpstgd": round(get_num(21, "I", 0.00214), 6),
        "parametrolamda": round(get_num(22, "J", -73.1637), 4),
    }

    _LOGGER.info("Tariffe ARERA estratte con successo per il periodo: %s", period)
    return data
