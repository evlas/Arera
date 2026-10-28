# ARERA Regulated Tariffs (Electricity & Gas) - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/Arera?color=blue&style=flat-square)](https://github.com/evlas/Arera/releases)
[![Hassfest](https://github.com/evlas/Arera/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/Arera/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *English version | [Versione in italiano](README.it.md)*

Home Assistant custom integration to automatically acquire and monitor official regulated tariffs set by **ARERA** (Italian Regulatory Authority for Energy, Networks and Environment) for:
1. ⚡ **Electricity**: grid tariffs ($\sigma_1, \sigma_2, \sigma_3$), general system charges (ASOS, ARIM), equalizations ($\text{UC}_3, \text{UC}_6$), and dispatching compensation fees (DispBT, CDISPD, CSED, CPSTGD, $\lambda$ parameter).
2. 🔥 **Natural Gas**: vulnerability protection service tariffs (CMEMm raw gas commodity, CCR procurement, QVD retail commercialization fixed and variable, $\tau_1, \tau_3$ distribution and metering, QT transport, RS service quality, UG1 equalization, RE energy savings, UG2 retail compensation, UG3 bad debt recovery).

Users can configure **Electricity only**, **Natural Gas only**, or **Both (Dual Fuel)**, with full multi-instance support to organize devices cleanly.

---

## 🚀 Key Features

- **Direct Live Download from Official ARERA Servers**:
  - **Electricity**: downloads `E{year}_stg_domesticiNonVulnerabili.xlsx` and `E{year}-smt.xlsx` (extracting DispBT live).
  - **Natural Gas**: downloads `G{year}_stv.xlsx` for the Vulnerability Protection Gas Service.
  - **Automatic Yearly Fallback**: uses current year and falls back to previous year seamlessly in early January.
- **Resilient Dynamic Header Matching**:
  - Scans table columns dynamically by header text ($\sigma_1, \sigma_3, \text{ASOS}, \dots$), avoiding broken coordinates if layout changes.
  - Raises explicit errors and marks sensors `unavailable` if data is missing or invalid, preventing silently displaying fake default numbers.
- **Geographic Area & Consumption Brackets for Gas**:
  - Full support for all 7 Italian gas zones (Nord Occidentale, Nord Orientale, Centrale, Centro-Sud Orientale, Centro-Sud Occidentale, Meridionale, Sardegna).
  - Configurable annual consumption brackets (from 0-120 Smc to over 5,000 Smc/year).
- **Two Distinct Clean Native Devices**:
  - Groups entities under **ARERA Tariffe Luce** and **ARERA Tariffe Gas**.
- **Transparency & Diagnostics**:
  - All sensors expose the reference period (e.g. *«Settembre 2026»*), Excel sheet name, source URL, and update timestamp as attributes.

---

## 📦 Installation via HACS

1. Open **HACS** in Home Assistant.
2. Go to **Integrations** -> Top right menu -> **Custom repositories**.
3. Add `https://github.com/evlas/Arera.git` as **Integration**.
4. Download **ARERA Tariffe Regolate** and restart Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings** -> **Devices & Services** -> **Add Integration**.
2. Search for **ARERA Tariffe**.
3. Select the utility supply to configure:
   - **Electricity**
   - **Natural Gas**
4. Complete the configuration:
   - For **Electricity**: select data source (default: *Official ARERA Online Tables*) and scan interval.
   - For **Natural Gas**: select your **Geographic Area** and **Annual Consumption Bracket**.
5. To monitor **both supplies**, simply repeat the process and add a second integration entry for the other utility. Home Assistant will create two clean and dedicated devices with their respective sensors.

---

## 📑 Entities

### ⚡ Electricity Sensors

| Entity | Description | Unit | ARERA Component |
| :--- | :--- | :--- | :--- |
| `sensor.arera_quota_fissa` | Fixed transport and metering fee | EUR/year | $\sigma_1$ |
| `sensor.arera_quota_potenza` | Power capacity transport fee | EUR/kW/year | $\sigma_2$ |
| `sensor.arera_quota_energia` | Energy volume transport fee | EUR/kWh | $\sigma_3$ |
| `sensor.arera_uc3` | Transport equalization component | EUR/kWh | $\text{UC}_3$ |
| `sensor.arera_uc6_qe` | Service quality recovery - Energy rate | EUR/kWh | $\text{UC}_{6\text{qe}}$ |
| `sensor.arera_uc6_qp` | Service quality recovery - Capacity rate | EUR/kW/year | $\text{UC}_{6\text{qp}}$ |
| `sensor.arera_asos` | Renewable energy support system charge | EUR/kWh | $\text{ASOS}$ |
| `sensor.arera_arim` | Remaining general system charges | EUR/kWh | $\text{ARIM}$ |
| `sensor.arera_dispbt` | Low-voltage dispatch compensation | EUR/year | $\text{DispBT}$ |
| `sensor.arera_cdispd` | Domestic wholesale dispatching component | EUR/kWh | $\text{CDISPD}$ |
| `sensor.arera_csed` | Efficient balancing component | EUR/kWh | $\text{CSED}$ |
| `sensor.arera_cpstgd` | Gradual protections equalization | EUR/kWh | $\text{CPSTGD}$ |
| `sensor.arera_parametro_lamda` | Lambda parameter | EUR/year | $\lambda$ |
| `sensor.arera_ultimo_aggiornamento` | Electricity reference period | - | e.g. «Settembre 2026» |

### 🔥 Natural Gas Sensors

| Entity | Description | Unit | ARERA Component |
| :--- | :--- | :--- | :--- |
| `sensor.arera_gas_cmemm` | Raw gas wholesale commodity price | EUR/Smc | $\text{CMEM}_m$ |
| `sensor.arera_gas_ccr` | Gas wholesale procurement fee | EUR/Smc | $\text{CCR}$ |
| `sensor.arera_gas_qvd_variabile` | Retail commercialization variable fee | EUR/Smc | $\text{QVD}_v$ |
| `sensor.arera_gas_tau3` | Distribution and metering variable fee | EUR/Smc | $\tau_3$ |
| `sensor.arera_gas_qt` | Gas transport component | EUR/Smc | $\text{QT}$ |
| `sensor.arera_gas_rs` | Service quality recovery | EUR/Smc | $\text{RS}$ |
| `sensor.arera_gas_ug1` | Equalization charge | EUR/Smc | $\text{UG}_1$ |
| `sensor.arera_gas_re` | Energy efficiency charge | EUR/Smc | $\text{RE}$ |
| `sensor.arera_gas_ug2_variabile` | Retail compensation variable fee | EUR/Smc | $\text{UG}_{2v}$ |
| `sensor.arera_gas_ug3` | Vulnerable customer bad debt recovery | EUR/Smc | $\text{UG}_3$ |
| `sensor.arera_gas_totale_variabile` | **Total Gas Variable Rate** | EUR/Smc | Sum of variable fees |
| `sensor.arera_gas_qvd_fissa` | Retail commercialization fixed fee | EUR/year | $\text{QVD}_f$ |
| `sensor.arera_gas_tau1` | Distribution and metering fixed fee (G6) | EUR/year | $\tau_1$ |
| `sensor.arera_gas_ug2_fissa` | Retail compensation fixed fee | EUR/year | $\text{UG}_{2f}$ |
| `sensor.arera_gas_totale_fissa` | **Total Gas Annual Fixed Fee** | EUR/year | Sum of fixed fees |
| `sensor.arera_gas_periodo` | Gas reference period | - | e.g. «Settembre 2026» |

---

## 📄 License

Released under [GNU General Public License v3.0](LICENSE).
