"""Parser integrato per tabelle ufficiali ARERA (formato Excel .xlsx per Luce e Gas)."""
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

        # Leggi workbook.xml e le relative relazioni per identificare il primo foglio attivo (il più recente in ARERA)
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
        # Se la componente è per sua natura pari a 0 nel tabellare
        return 0.0
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


def parse_arera_gas_xlsx(
    content: bytes,
    ambito_key: str = "nord_orientale",
    scaglione_key: str = "scaglione_3",
) -> dict[str, Any]:
    """Estrae le tariffe ufficiali ARERA Gas Naturale (file G{anno}_stv.xlsx) per l'ambito e scaglione indicati."""
    rows, strings, sheet_name = _extract_excel_rows(content)

    ambiti_names: dict[str, str] = {
        "nord_occidentale": "nord occidentale",
        "nord_orientale": "nord orientale",
        "centrale": "centrale",
        "centro_sud_orientale": "centro-sud orientale",
        "centro_sud_occidentale": "centro-sud occidentale",
        "meridionale": "meridionale",
        "sardegna": "sardegna",
    }
    target_name = ambiti_names.get(ambito_key, "nord orientale")

    # 1. Trova l'inizio dell'ambito geografico
    ambito_row: int | None = None
    for r, cols in sorted(rows.items()):
        b_val = str(cols.get("B", "")).lower()
        if "ambito" in b_val and target_name in b_val:
            ambito_row = r
            break

    if not ambito_row:
        raise ValueError(f"Ambito gas '{target_name}' non trovato nel file Excel ARERA")

    header_row = ambito_row + 1
    period = rows.get(header_row, {}).get("B") or sheet_name

    # 2. Determina la riga dello scaglione di consumo richiesto
    scaglione_patterns: dict[str, str] = {
        "scaglione_1": "0 a 120",
        "scaglione_2": "121 a 480",
        "scaglione_3": "481 a 1.560",
        "scaglione_4": "1.561 a 5.000",
    }
    pattern_to_find = scaglione_patterns.get(scaglione_key, "481 a 1.560")

    r_energia_target: int | None = None
    r_fissa_g6: int | None = None

    for r in range(ambito_row, ambito_row + 18):
        b = str(rows.get(r, {}).get("B", "")).lower()
        if pattern_to_find in b:
            r_energia_target = r
        elif "classe fino a g6" in b and "utenze" not in b:
            r_fissa_g6 = r

    # Fallback se non trova lo scaglione specifico: usa lo scaglione 1
    if not r_energia_target:
        for r in range(ambito_row, ambito_row + 18):
            b = str(rows.get(r, {}).get("B", "")).lower()
            if "0 a 120" in b:
                r_energia_target = r
                break

    if not r_energia_target or not r_fissa_g6:
        raise ValueError(
            f"Righe quote gas non trovate per l'ambito '{target_name}' (energia: {r_energia_target}, fissa: {r_fissa_g6})"
        )

    r_e = rows[r_energia_target]
    r_f = rows[r_fissa_g6]

    data: dict[str, Any] = {
        "gas_periodo": period,
        "gas_sheet_name": sheet_name,
        "gas_ambito": target_name,
        "gas_scaglione": scaglione_key,
        # Quote variabili al metro cubo (€/Smc)
        "gas_cmemm": round(_parse_num(r_e.get("C"), "gas_cmemm"), 6),
        "gas_ccr": round(_parse_num(r_e.get("D"), "gas_ccr"), 6),
        "gas_qvd_variabile": round(_parse_num(r_e.get("E"), "gas_qvd_variabile"), 6),
        "gas_tau3": round(_parse_num(r_e.get("H"), "gas_tau3"), 6),
        "gas_qt": round(_parse_num(r_e.get("I"), "gas_qt"), 6),
        "gas_rs": round(_parse_num(r_e.get("J"), "gas_rs"), 6),
        "gas_ug1": round(_parse_num(r_e.get("K"), "gas_ug1"), 6),
        "gas_re": round(_parse_num(r_e.get("P"), "gas_re"), 6),
        "gas_ug2_variabile": round(_parse_num(r_e.get("Q"), "gas_ug2_variabile"), 6),
        "gas_ug3": round(_parse_num(r_e.get("R"), "gas_ug3"), 6),
        "gas_totale_variabile": round(_parse_num(r_e.get("T"), "gas_totale_variabile"), 6),
        # Quote fisse annue (€/anno) contatore domestico G6
        "gas_qvd_fissa": round(_parse_num(r_f.get("E"), "gas_qvd_fissa"), 4),
        "gas_tau1": round(_parse_num(r_f.get("G"), "gas_tau1"), 4),
        "gas_ug2_fissa": round(_parse_num(r_f.get("Q"), "gas_ug2_fissa"), 4),
        "gas_totale_fissa": round(_parse_num(r_f.get("T"), "gas_totale_fissa"), 4),
    }

    _LOGGER.info(
        "Tariffe ARERA Gas estratte con successo per l'ambito '%s' (Periodo: %s, Scaglione: %s)",
        target_name,
        period,
        scaglione_key,
    )
    return data
