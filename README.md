# ARERA Tariffe Luce - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/Arera?color=blue&style=flat-square)](https://github.com/evlas/Arera/releases)
[![Hassfest](https://github.com/evlas/Arera/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/Arera/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *English | [Versione in italiano](README.it.md)*

Professional **Home Assistant** integration to monitor and acquire regulated Italian electricity tariffs set by **ARERA** (Regulatory Authority for Energy, Networks and Environment), including transmission, distribution, metering, system charges (ASOS, ARIM), and dispatching components for low-voltage domestic customers.

---

## 🚀 Key Features

- **Automated Data Retrieval**: Periodically fetches updated tariff parameters from a local or remote JSON endpoint (e.g. `http://192.168.70.50/arera/arera.json` or online GitHub/Gist).
- **Official Built-in Fallbacks**: Ships with current official ARERA low-voltage domestic tariff defaults. If your endpoint is temporarily unreachable or not set, the integration never fails and smoothly falls back to verified values.
- **100% WebUI Configuration (Config Flow & Options Flow)**: Setup endpoint URL and polling interval (in hours) directly from *Settings -> Devices & Services*.
- **Fine-Grained Parameter Overrides**: Override any individual regulated component (e.g. $\sigma_1$, $\sigma_2$, $\sigma_3$, ASOS, ARIM) anytime via the **Options** flow.
- **Dedicated Device Organization**: Automatically groups all regulated tariff components cleanly under a single device: **ARERA Tariffe Regolate**.
- **Designed for Companion Integrations**: Works seamlessly with the companion [Bolletta Elettrica](https://github.com/evlas/Bolletta) integration to calculate complete electricity bills.

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
   - **JSON URL (Local or Remote)**: Enter the URL of your endpoint (default: `http://192.168.70.50/arera/arera.json`) and the polling interval (default: `24` hours).
   - **Manual / Official Defaults**: Use built-in official ARERA values and customize them whenever you want via Options.

---

## 📑 Entities Created

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
| `sensor.arera_ultimo_aggiornamento` | Timestamp of last tariff update | - | - |

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
    name: Componente DispBT
  - entity: sensor.arera_ultimo_aggiornamento
    name: Ultimo Aggiornamento
```

---

## 📄 JSON Schema Example

If hosting your own endpoint on an internal web server or cloud storage, refer to [`arera_sample.json`](arera_sample.json):

```json
{
  "today": "2024-10-01",
  "cdispd": 0.0018,
  "csed": 0.0010,
  "cpstgd": 0.0000,
  "parametrolamda": 0.0,
  "dispbt": 1.107,
  "s1": 24.40,
  "s2": 23.50,
  "s3": 0.0135,
  "uc3": 0.0016,
  "uc6qe": 0.0001,
  "uc6qp": 0.0000,
  "asos": 0.0345,
  "arim": 0.0090
}
```

---

## 🛠️ Companion Integration

To compute the final bill and dynamic energy cost with your supplier:
- 🔗 **[Bolletta Elettrica](https://github.com/evlas/Bolletta)**

---

## 📄 License

Distributed under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for details.
