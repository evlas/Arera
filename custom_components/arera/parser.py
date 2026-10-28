"""Parser integrato per tabelle ufficiali ARERA (formato Excel .xlsx)."""
from __future__ import annotations

import io
import logging
from typing import Any
import xml.etree.ElementTree as ET
import zipfile

_LOGGER = logging.getLogger(__name__)


def _extract_excel_rows(content: bytes) -> tuple[dict[int, dict[str, Any]], list[str], str]:
    """Estrae dizionario delle righe, stringhe condivise e nome del primo foglio dal file Excel .xlsx."""
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        strings: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            sstree = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sstree:
                strings.append("".join(si.itertext()))

        sheet_name = "Foglio 1"
        target_path = "xl/worksheets/sheet1.xml"

        # Leggi workbook.xml e le relative relazioni per identificare il primo foglio attivo
        if "xl/workbook.xml" in z.namelist() and "xl/_rels/workbook.xml.rels" in z.namelist():
            try:
                wb_tree = ET.fromstring(z.read("xl/workbook.xml"))
                rels_tree = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
                rel_map = {r.attrib.get("Id"): r.attrib.get("Target") for r in rels_tree}

                sheets = list(wb_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"))
                if sheets:
                    first_sheet = sheets[0]
                    sheet_name = first_sheet.attrib.get("name", "Foglio 1")
                    r_id = first_sheet.attrib.get(
                        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                    )
                    target = rel_map.get(r_id)
                    if target:
                        if not target.startswith("xl/"):
                            target = "xl/" + target.lstrip("/")
                        target_path = target
            except Exception as err:
                _LOGGER.debug("Errore durante la lettura di workbook.xml: %s, fallback a sheet1.xml", err)

        if target_path not in z.namelist():
            sheet_candidates = [
                n
                for n in z.namelist()
                if n.startswith("xl/worksheets/sheet")
                and n.endswith(".xml")
                and "rels" not in n
            ]
            if not sheet_candidates:
                raise ValueError("Nessun foglio valido trovato nel file Excel ARERA")
            target_path = sheet_candidates[0]

        sheet_tree = ET.fromstring(z.read(target_path))
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

    return rows, strings, sheet_name


def _parse_num(val: Any, component_name: str) -> float:
    """Estrae un numero in virgola mobile sollevando eccezione se mancante o non valido."""
    if val is None or str(val).strip() in ("-", "- ", "", "None"):
        raise ValueError(f"Valore mancante o vuoto per la componente '{component_name}'")
    try:
        return float(val)
    except (ValueError, TypeError) as err:
        raise ValueError(
            f"Valore non numerico per la componente '{component_name}': {val}"
        ) from err


def parse_arera_smt_xlsx(content: bytes) -> dict[str, Any]:
    """Estrae la componente DISPbt dal file Excel ufficiale ARERA SMT (es. E2026-smt.xlsx scaricato dalla rete)."""
    rows, _, sheet_name = _extract_excel_rows(content)

    dispbt_col = None
    for r in range(14, 22):
        for col, val in rows.get(r, {}).items():
            if val and "dispbt" in str(val).lower():
                dispbt_col = col
                break
        if dispbt_col:
            break

    dispbt_val = None
    if dispbt_col:
        for r in range(18, 26):
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
        _LOGGER.info(
            "Componente DispBT ARERA estratta con successo (%s): %s €/anno",
            sheet_name,
            dispbt_val,
        )
        return {"dispbt": round(dispbt_val, 4), "smt_sheet": sheet_name}

    raise ValueError(f"Componente DispBT non trovata nel file SMT ARERA (foglio: {sheet_name})")


def parse_arera_xlsx(content: bytes) -> dict[str, Any]:
    """Estrae le tariffe regolate ARERA dal file Excel ufficiale STG o SMT cercando dinamicamente le intestazioni."""
    rows, strings, sheet_name = _extract_excel_rows(content)

    # Rilevamento automatico se il file passato contiene la tabella SMT con DISPbt
    for val in rows.get(17, {}).values():
        if val and "dispbt" in str(val).lower():
            return parse_arera_smt_xlsx(content)

    # 1. Trova riga di inizio sezione residenti ("Abitazioni di residenza anagrafica")
    res_start_row = None
    for r, cols in sorted(rows.items()):
        for val in cols.values():
            if val and "residenza anagrafica" in str(val).lower() and "diverse" not in str(val).lower():
                res_start_row = r
                break
        if res_start_row:
            break

    if not res_start_row:
        res_start_row = 17

    # 2. Cerca dinamicamente la riga di intestazione delle colonne (σ1, σ3, ASOS, ARIM...)
    header_row = None
    col_map: dict[str, str] = {}
    for r in range(res_start_row, res_start_row + 6):
        row_vals = {c: str(v).strip() for c, v in rows.get(r, {}).items() if v}
        row_text = " ".join(row_vals.values()).lower()
        if "asos" in row_text and "arim" in row_text:
            header_row = r
            for c, v in row_vals.items():
                vl = v.lower()
                if "cdispd" in vl:
                    col_map["cdispd"] = c
                elif "csed" in vl:
                    col_map["csed"] = c
                elif "cpstgd" in vl:
                    col_map["cpstgd"] = c
                elif any(k in vl for k in ["parametro", "gamma", "γ", "lambda"]):
                    col_map["parametro"] = c
                elif any(k in vl for k in ["σ1", "s1", "sigma1", "sigma 1"]):
                    col_map["s1"] = c
                elif any(k in vl for k in ["σ2", "s2", "sigma2", "sigma 2"]):
                    col_map["s2"] = c
                elif any(k in vl for k in ["σ3", "s3", "sigma3", "sigma 3"]):
                    col_map["s3"] = c
                elif "uc3" in vl:
                    col_map["uc3"] = c
                elif "uc6" in vl:
                    col_map["uc6"] = c
                elif "asos" in vl:
                    col_map["asos"] = c
                elif "arim" in vl:
                    col_map["arim"] = c
            break

    if not header_row:
        raise ValueError("Riga di intestazione colonne (σ1, σ3, ASOS, ARIM...) non trovata nel file ARERA")

    required_cols = [
        "cdispd", "csed", "cpstgd", "parametro",
        "s1", "s2", "s3", "uc3", "uc6", "asos", "arim"
    ]
    missing_cols = [c for c in required_cols if c not in col_map]
    if missing_cols:
        raise ValueError(f"Colonne tariffarie mancanti nell'intestazione ARERA: {missing_cols}")

    # 3. Cerca righe delle quote e periodo di riferimento
    r_energia = None
    r_fissa = None
    r_potenza = None
    period = None

    for r in range(header_row, header_row + 8):
        b_val = str(rows.get(r, {}).get("B", "")).strip()
        b_lower = b_val.lower()
        if "quota energia" in b_lower:
            r_energia = r
        elif "quota fissa" in b_lower:
            r_fissa = r
        elif "quota potenza" in b_lower:
            r_potenza = r
        elif any(
            m in b_lower
            for m in [
                "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
                "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
                "trimestre"
            ]
        ):
            period = b_val

    if not r_energia or not r_fissa or not r_potenza:
        raise ValueError(
            f"Righe delle quote tariffarie non trovate (energia: {r_energia}, fissa: {r_fissa}, potenza: {r_potenza})"
        )

    final_period = period or sheet_name

    # 4. Estrazione rigida con sollevamento eccezione in caso di valori nulli o non numerici
    data = {
        "period": final_period,
        "sheet_name": sheet_name,
        "today": final_period,
        "s1": round(_parse_num(rows[r_fissa].get(col_map["s1"]), "s1"), 4),
        "s2": round(_parse_num(rows[r_potenza].get(col_map["s2"]), "s2"), 4),
        "s3": round(_parse_num(rows[r_energia].get(col_map["s3"]), "s3"), 6),
        "uc3": round(_parse_num(rows[r_energia].get(col_map["uc3"]), "uc3"), 6),
        "uc6qe": round(_parse_num(rows[r_energia].get(col_map["uc6"]), "uc6qe"), 6),
        "uc6qp": round(_parse_num(rows[r_potenza].get(col_map["uc6"]), "uc6qp"), 4),
        "asos": round(_parse_num(rows[r_energia].get(col_map["asos"]), "asos"), 6),
        "arim": round(_parse_num(rows[r_energia].get(col_map["arim"]), "arim"), 6),
        "cdispd": round(_parse_num(rows[r_energia].get(col_map["cdispd"]), "cdispd"), 6),
        "csed": round(_parse_num(rows[r_energia].get(col_map["csed"]), "csed"), 6),
        "cpstgd": round(_parse_num(rows[r_energia].get(col_map["cpstgd"]), "cpstgd"), 6),
        "parametrolamda": round(
            _parse_num(rows[r_fissa].get(col_map["parametro"]), "parametrolamda"), 4
        ),
    }

    _LOGGER.info(
        "Tariffe ARERA STG estratte con successo per il periodo '%s' (foglio: '%s')",
        final_period,
        sheet_name,
    )
    return data
