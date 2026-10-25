# ARERA Tariffe Luce - Integrazione Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/Arera?color=blue&style=flat-square)](https://github.com/evlas/Arera/releases)
[![Hassfest](https://github.com/evlas/Arera/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/Arera/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *[English version](README.md) | Versione in italiano*

Integrazione professionale per **Home Assistant** per monitorare e acquisire le tariffe regolate stabilite da **ARERA** (Autorità di Regolazione per Energia Reti e Ambiente) per il settore elettrico (servizi di trasmissione, distribuzione, misura, oneri generali di sistema ASOS e ARIM, e corrispettivi di dispacciamento per clienti domestici in bassa tensione).

---

## 🚀 Caratteristiche Principali

- **Acquisizione Automatica dei Dati**: Interroga periodicamente un endpoint JSON locale (es. `http://192.168.70.50/arera/arera.json`) o un URL remoto (es. GitHub o Gist).
- **Valori Ufficiali Integrati (Fallback)**: Fornita con i valori ufficiali ARERA predefiniti aggiornati. Se l'endpoint non è raggiungibile o non viene fornito un URL, l'integrazione non va mai in errore e garantisce continuità di funzionamento.
- **Configurazione 100% da WebUI (Config Flow & Options Flow)**: Impostazione guidata dell'URL dell'endpoint e della frequenza di aggiornamento (in ore) da *Impostazioni -> Dispositivi e Servizi*.
- **Personalizzazione e Override nelle Opzioni**: Possibilità di modificare in qualsiasi momento singoli valori delle componenti regolate (es. $\sigma_1$, $\sigma_2$, $\sigma_3$, ASOS, ARIM).
- **Organizzazione Pulita del Dispositivo**: Tutte le componenti tariffarie sono raggruppate sotto un unico dispositivo nativo: **ARERA Tariffe Regolate**.
- **Progettata per l'Integrazione Compagna**: Perfettamente integrabile con [Bolletta Elettrica](https://github.com/evlas/Bolletta) per il calcolo trasparente e completo della bolletta con il proprio fornitore.

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
4. Seleziona la modalità:
   - **URL JSON (Locale o Remoto)**: Inserisci l'URL dell'endpoint (predefinito: `http://192.168.70.50/arera/arera.json`) e la frequenza di aggiornamento (default: `24` ore).
   - **Manuale / Valori Ufficiali Predefiniti**: Utilizza i valori ARERA ufficiali integrati e modificali a piacimento tramite le Opzioni.

---

## 📑 Entità Create

| Entità | Descrizione | Unità | Componente ARERA |
| :--- | :--- | :--- | :--- |
| `sensor.arera_quota_fissa` | Quota Fissa Trasporto e Misura | EUR/anno | $\sigma_1$ |
| `sensor.arera_quota_potenza` | Quota Potenza Trasporto e Misura | EUR/kW/anno | $\sigma_2$ |
| `sensor.arera_quota_energia` | Quota Energia Trasporto e Misura | EUR/kWh | $\sigma_3$ |
| `sensor.arera_uc3` | Perequazione Costi di Trasporto | EUR/kWh | $\text{UC}_3$ |
| `sensor.arera_uc6_qe` | Recuperi Qualità Servizio - Quota Energia | EUR/kWh | $\text{UC}_{6\text{qe}}$ |
| `sensor.arera_uc6_qp` | Recuperi Qualità Servizio - Quota Potenza | EUR/kW/anno | $\text{UC}_{6\text{qp}}$ |
| `sensor.arera_asos` | Oneri Sostegno Fonti Rinnovabili | EUR/kWh | $\text{ASOS}$ |
| `sensor.arera_arim` | Rimanenti Oneri Generali di Sistema | EUR/kWh | $\text{ARIM}$ |
| `sensor.arera_dispbt` | Componente DispBT Bassa Tensione | EUR/anno | $\text{DispBT}$ |
| `sensor.arera_cdispd` | Corrispettivo Dispacciamento Domestici | EUR/kWh | $\text{CDISPD}$ |
| `sensor.arera_csed` | Corrispettivo Sbilanciamento Efficiente | EUR/kWh | $\text{CSED}$ |
| `sensor.arera_cpstgd` | Perequazione Servizio Tutele Graduali | EUR/kWh | $\text{CPSTGD}$ |
| `sensor.arera_parametro_lamda` | Parametro Lambda | EUR/anno | $\lambda$ |
| `sensor.arera_ultimo_aggiornamento` | Data/ora dell'ultimo aggiornamento tariffe | - | - |

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
    name: Componente DispBT
  - entity: sensor.arera_ultimo_aggiornamento
    name: Ultimo Aggiornamento
```

---

## 📄 Schema JSON di Riferimento

Se utilizzi un tuo server web locale o storage remoto, fai riferimento al file d'esempio [`arera_sample.json`](arera_sample.json):

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

## 🛠️ Integrazione Compagna

Per calcolare il costo dinamico finito della bolletta con il tuo fornitore:
- 🔗 **[Bolletta Elettrica](https://github.com/evlas/Bolletta)**

---

## 📄 Licenza

Distribuito sotto licenza GNU General Public License v3.0 (GPLv3). Consulta il file [LICENSE](LICENSE) per ulteriori dettagli.
