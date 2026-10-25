# ARERA Tariffe Energia Elettrica - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/Arera?color=blue&style=flat-square)](https://github.com/evlas/Arera/releases)
[![Hassfest](https://github.com/evlas/Arera/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/Arera/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *English | [Versione in italiano](README.it.md)*

Professional **Home Assistant** integration to automatically acquire and monitor Italian regulated tariffs established by **ARERA** (Regulatory Authority for Energy, Networks and Environment) specifically for the **Electricity Sector** (*Energia Elettrica*), including transmission, distribution, metering, general system charges (ASOS, ARIM), and low-voltage domestic dispatching/equalization fees.

> [!IMPORTANT]
> **Scope: Electricity Sector Only (Energia Elettrica)**
> This integration is dedicated exclusively to the **Italian Electricity Sector** for domestic low-voltage customers. It provides all regulated components required for electricity bill calculations in real time. It does not cover natural gas, water, or other ARERA-regulated public services.

---

## 🚀 Key Features

- **Direct Live Download from Official ARERA Servers (Default)**:
  - Periodically downloads and parses official Excel tables published on `arera.it`:
    1. **`stg_domesticiNonVulnerabili.xlsx`**: for grid tariffs, transmission, distribution, metering, equalization ($\sigma_1, \sigma_2, \sigma_3, \text{UC}_3, \text{UC}_6$), and general system charges (ASOS, ARIM).
    2. **`E{year}-smt.xlsx`**: for regulated standard offer fees, extracting the **DispBT** component live in real-time (ARERA Resolution 218/2026/R/eel).
- **Official Built-in Fallbacks**:
  - Preloaded with verified official ARERA values. If ARERA servers or network connections are temporarily unreachable, the integration never fails and maintains continuous bill calculation.
- **100% WebUI Configuration (Config Flow & Options Flow)**:
  - Guided setup via graphical UI: choose your data source (Official ARERA Tables, Custom URL, or Manual Values) and polling interval (default: 24 hours).
- **Fine-Grained Parameter Overrides**:
  - Override any individual regulated component anytime via the **Options** menu without restarting Home Assistant.
- **Clean Dedicated Device Organization**:
  - All 14 tariff and diagnostic entities are cleanly grouped under a single native device: **ARERA Tariffe Regolate**.
- **Designed for Companion Integrations**:
  - Automatically supplies [Bolletta Elettrica](https://github.com/evlas/Bolletta) with all updated fixed and variable charges (including `sensor.arera_dispbt`) for transparent, exact bill calculations.

---

## 📦 Installation

### Method 1: Via HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Go to **Integrations** -> Click the three dots menu in the top right corner -> **Custom repositories**.
3. Paste `https://github.com/evlas/Arera.git`, select the category **Integration**, and click **Add**.
4. Search for **ARERA Tariffe Luce** and click **Download**.
5. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the `custom_components/arera` directory.
2. Copy it into your Home Assistant installation:
   ```
   /config/custom_components/arera/
   ```
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. In the Home Assistant WebUI, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **ARERA Tariffe Luce**.
4. Choose your acquisition mode:
   - **Official ARERA Tables (XLSX online)** *(Recommended / Default)*: Downloads both `stg_domesticiNonVulnerabili.xlsx` and `E{year}-smt.xlsx` directly from the official ARERA portal.
   - **Custom URL (JSON or XLSX)**: Specify a custom URL from a local web server or cloud endpoint (e.g. `http://192.168.1.100/arera.json` or Excel file).
   - **Manual / Official Defaults**: Use built-in default values and customize them whenever you want via Options.
5. Set the polling interval (default: `24` hours).

---

## 📑 Entities Created

| Entity | Description | Unit | ARERA Component / Source |
| :--- | :--- | :--- | :--- |
| `sensor.arera_quota_fissa` | Fixed transport and metering fee | EUR/year | $\sigma_1$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_quota_potenza` | Power capacity transport fee | EUR/kW/year | $\sigma_2$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_quota_energia` | Energy volume transport fee | EUR/kWh | $\sigma_3$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_uc3` | Transport equalization component | EUR/kWh | $\text{UC}_3$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_uc6_qe` | Service quality recovery - Energy rate | EUR/kWh | $\text{UC}_{6\text{qe}}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_uc6_qp` | Service quality recovery - Capacity rate | EUR/kW/year | $\text{UC}_{6\text{qp}}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_asos` | Renewable energy support system charge | EUR/kWh | $\text{ASOS}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_arim` | Remaining general system charges | EUR/kWh | $\text{ARIM}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_dispbt` | Low-voltage dispatch compensation | EUR/year | $\text{DispBT}$ (extracted live from `E{year}-smt.xlsx`) |
| `sensor.arera_cdispd` | Domestic wholesale dispatching component | EUR/kWh | $\text{CDISPD}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_csed` | Efficient balancing component | EUR/kWh | $\text{CSED}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_cpstgd` | Gradual protections equalization | EUR/kWh | $\text{CPSTGD}$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_parametro_lamda` | Lambda parameter | EUR/year | $\lambda$ (`stg_domesticiNonVulnerabili.xlsx`) |
| `sensor.arera_ultimo_aggiornamento` | Timestamp of last tariff update | - | Local timestamp |

---

## 🎛️ Lovelace Card Example

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

## 📄 Custom JSON Schema (Optional)

If hosting your own endpoint on an internal web server or cloud storage, refer to [`arera_sample.json`](arera_sample.json):

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

## 🛠️ Companion Integration

To compute the final bill and dynamic energy cost with your supplier:
- 🔗 **[Bolletta Elettrica](https://github.com/evlas/Bolletta)**

---

## 📄 License

Distributed under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for details.
