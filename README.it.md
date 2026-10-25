# ARERA Tariffe Luce - Integrazione Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/Arera?color=blue&style=flat-square)](https://github.com/evlas/Arera/releases)
[![Hassfest](https://github.com/evlas/Arera/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/Arera/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *[English version](README.md) | Versione in italiano*

Integrazione professionale per **Home Assistant** per acquisire e monitorare automaticamente le tariffe regolate stabilite da **ARERA** (Autorità di Regolazione per Energia Reti e Ambiente) per il settore elettrico italiano (servizi di trasmissione, distribuzione, misura contatore, oneri generali di sistema ASOS e ARIM, e corrispettivi di dispacciamento ed equalizzazione per clienti domestici in bassa tensione).

---

## 🚀 Caratteristiche Principali

- **Download Automatico Live dai Server Ufficiali ARERA (Predefinito)**:
  - Scarica e analizza periodicamente i file Excel ufficiali pubblicati su `arera.it`:
    1. **`stg_domesticiNonVulnerabili.xlsx`**: per le tariffe di rete, trasmissione, distribuzione, misura, perequazione ($\sigma_1, \sigma_2, \sigma_3, \text{UC}_3, \text{UC}_6$) e oneri generali di sistema (ASOS, ARIM).
    2. **`E{anno}-smt.xlsx`**: per i corrispettivi del servizio di tutela e dispacciamento, estraendo dinamicamente in tempo reale la componente **DispBT** (Delibera ARERA 218/2026/R/eel).
- **Valori Ufficiali Integrati (Fallback Robusto)**:
  - Include i valori ufficiali ARERA predefiniti. Se i server ARERA o la connessione di rete sono temporaneamente non disponibili, l'integrazione non va mai in errore e garantisce continuità assoluta ai calcoli della bolletta.
- **Configurazione 100% da WebUI (Config Flow & Options Flow)**:
  - Configurazione guidata tramite interfaccia grafica: scegli la modalità (Tabelle Ufficiali ARERA, URL Personalizzato, oppure Valori Manuali) e imposta l'intervallo di aggiornamento (default: 24 ore).
- **Personalizzazione e Override nelle Opzioni**:
  - Puoi modificare in qualunque momento qualunque singola componente regolata tramite il menu **Opzioni** dell'integrazione senza riavviare Home Assistant.
- **Organizzazione Pulita del Dispositivo**:
  - Tutte le 14 componenti tariffarie e diagnostiche sono organizzate sotto un unico dispositivo nativo: **ARERA Tariffe Regolate**.
- **Progettata per l'Integrazione Compagna Bolletta**:
  - Fornisce automaticamente a [Bolletta Elettrica](https://github.com/evlas/Bolletta) tutte le quote fisse e variabili aggiornate (incluso `sensor.arera_dispbt`) per il calcolo trasparente e preciso del costo finito dell'energia.

---

## 📦 Installazione

### Metodo 1: Tramite HACS (Consigliato)

1. Apri **HACS** in Home Assistant.
2. Vai su **Integrazioni** -> Menu tre puntini in alto a destra -> **Repository personalizzati**.
3. Incolla `https://github.com/evlas/Arera.git`, seleziona la categoria **Integrazione** e clicca **Aggiungi**.
4. Cerca **ARERA Tariffe Luce** e clicca su **Scarica**.
5. Riavvia Home Assistant.

### Metodo 2: Installazione Manuale

1. Scarica la cartella `custom_components/arera`.
2. Copiala nella directory `custom_components/` della tua installazione di Home Assistant:
   ```
   /config/custom_components/arera/
   ```
3. Riavvia Home Assistant.

---

## ⚙️ Configurazione

1. Nella WebUI di Home Assistant, vai su **Impostazioni** -> **Dispositivi e Servizi**.
2. Clicca su **Aggiungi Integrazione** in basso a destra.
3. Cerca **ARERA Tariffe Luce**.
4. Seleziona la sorgente dei dati:
   - **Tabelle Ufficiali ARERA (XLSX online)** *(Consigliato / Predefinito)*: Scarica automaticamente via rete sia `stg_domesticiNonVulnerabili.xlsx` che `E{anno}-smt.xlsx` direttamente dal portale ufficiale ARERA.
   - **URL Personalizzato (JSON o XLSX)**: Inserisci l'URL di un tuo server web locale o endpoint cloud (es. `http://192.168.1.100/arera.json` o file Excel).
   - **Manuale / Valori Ufficiali Predefiniti**: Utilizza i valori predefiniti integrati e modificali a piacimento tramite il menu Opzioni.
5. Imposta la frequenza di aggiornamento desiderata (default: `24` ore).

---

## 📑 Entità Create

| Entità | Descrizione | Unità | Fonte / Componente ARERA |
| :--- | :--- | :--- | :--- |
| `sensor.arera_quota_fissa` | Quota Fissa Trasporto e Misura | EUR/anno | $\sigma_1$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_quota_potenza` | Quota Potenza Trasporto e Misura | EUR/kW/anno | $\sigma_2$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_quota_energia` | Quota Energia Trasporto e Misura | EUR/kWh | $\sigma_3$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_uc3` | Perequazione Costi di Trasporto | EUR/kWh | $\text{UC}_3$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_uc6_qe` | Recuperi Qualità Servizio - Quota Energia | EUR/kWh | $\text{UC}_{6\text{qe}}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_uc6_qp` | Recuperi Qualità Servizio - Quota Potenza | EUR/kW/anno | $\text{UC}_{6\text{qp}}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_asos` | Oneri Sostegno Fonti Rinnovabili | EUR/kWh | $\text{ASOS}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_arim` | Rimanenti Oneri Generali di Sistema | EUR/kWh | $\text{ARIM}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_dispbt` | Corrispettivo di Dispacciamento BT | EUR/anno | $\text{DispBT}$ (estratto live da `E{anno}-smt.xlsx`) |
| `sensor.arera_cdispd` | Corrispettivo Dispacciamento Domestici | EUR/kWh | $\text{CDISPD}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_csed` | Corrispettivo Sbilanciamento Efficiente | EUR/kWh | $\text{CSED}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_cpstgd` | Perequazione Servizio Tutele Graduali | EUR/kWh | $\text{CPSTGD}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_parametro_lamda` | Parametro Lambda Servizio Tutele Graduali | EUR/anno | $\lambda$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_ultimo_aggiornamento` | Data e ora dell'ultimo aggiornamento eseguito | - | Timestamp locale |

---

## 🎛️ Esempio Scheda Lovelace

```yaml
type: entities
title: ARERA Tariffe Regolate
show_header_toggle: false
entities:
  - entity: sensor.arera_quota_fissa
    name: Quota Fissa Trasporto (s1)
  - entity: sensor.arera_quota_potenza
    name: Quota Potenza Trasporto (s2)
  - entity: sensor.arera_quota_energia
    name: Quota Energia Trasporto (s3)
  - entity: sensor.arera_asos
    name: Oneri Rinnovabili (ASOS)
  - entity: sensor.arera_arim
    name: Altri Oneri di Sistema (ARIM)
  - entity: sensor.arera_uc3
    name: Perequazione UC3
  - entity: sensor.arera_dispbt
    name: Componente DispBT (E*-smt)
  - entity: sensor.arera_ultimo_aggiornamento
    name: Ultimo Aggiornamento
```

---

## 📄 Schema JSON Personalizzato (Opzionale)

Se scegli la modalità ad endpoint JSON locale o remoto, fai riferimento allo schema d'esempio [`arera_sample.json`](arera_sample.json):

```json
{
  "today": "2026-10-01",
  "cdispd": 0.019902,
  "csed": 0.00056,
  "cpstgd": 0.00214,
  "parametrolamda": -73.1637,
  "dispbt": 1.107,
  "s1": 23.04,
  "s2": 23.52,
  "s3": 0.0119,
  "uc3": 0.00276,
  "uc6qe": 0.00007,
  "uc6qp": 0.1988,
  "asos": 0.028657,
  "arim": 0.001638
}
```

---

## 🛠️ Integrazione Compagna

Per calcolare il costo dinamico finito della bolletta elettrica con il tuo fornitore:
- 🔗 **[Bolletta Elettrica](https://github.com/evlas/Bolletta)**

---

## 📄 Licenza

Distribuito sotto licenza GNU General Public License v3.0 (GPLv3). Consulta il file [LICENSE](LICENSE) per ulteriori dettagli.
