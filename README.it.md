# ARERA Tariffe Regolate (Luce e Gas) - Integrazione Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/Arera?color=blue&style=flat-square)](https://github.com/evlas/Arera/releases)
[![Hassfest](https://github.com/evlas/Arera/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/Arera/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/Arera/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *[English version](README.md) | Versione in italiano*

Integrazione per **Home Assistant** per acquisire e monitorare automaticamente le tariffe regolate stabilite da **ARERA** (Autorità di Regolazione per Energia Reti e Ambiente) per:
1. ⚡ **Energia Elettrica (Luce)**: servizi di rete (trasporto e misura $\sigma_1, \sigma_2, \sigma_3$), oneri generali di sistema (ASOS e ARIM), perequazioni ($\text{UC}_3, \text{UC}_6$) e corrispettivi di dispacciamento (DispBT, CDISPD, CSED, CPSTGD, parametro $\lambda$).
2. 🔥 **Gas Naturale**: condizioni economiche del servizio di tutela della vulnerabilità (CMEMm, CCR, commercializzazione QVD fissa/variabile, distribuzione e misura $\tau_1, \tau_3$, trasporto QT, qualità RS, perequazione UG1, risparmio energetico RE, oneri UG2 fisso/variabile, morosità UG3).

L'utente può scegliere di configurare **solo la Luce**, **solo il Gas** oppure **entrambe le forniture**, anche aggiungendo più istanze separate per organizzare i dispositivi.

---

## 🚀 Caratteristiche Principali

- **Download Automatico Live dai Server Ufficiali ARERA (Predefinito)**:
  - **Luce**: scarica `E{anno}_stg_domesticiNonVulnerabili.xlsx` e `E{anno}-smt.xlsx` (estraendo DispBT dalla Delibera 218/2026/R/eel).
  - **Gas**: scarica `G{anno}_stv.xlsx` per il Servizio di Tutela della Vulnerabilità Gas.
  - **Fallback Annuale e Storico**: seleziona automaticamente l'anno corrente con fallback sull'anno precedente per garantire continuità nei primi giorni di gennaio.
- **Parsing Dinamico Resiliente per Intestazione**:
  - Scansione dinamica delle colonne per intestazione ($\sigma_1, \sigma_3, \text{ASOS}, \dots$), evitando disallineamenti in caso di modifiche all'impaginazione del foglio ARERA.
  - Se un valore non è reperibile o non numerico, l'integrazione solleva un errore trasparente rendendo i sensori `unavailable` anziché mostrare valori fittizi.
- **Ambiti Geografici e Scaglioni Gas Personalizzabili**:
  - Supporto completo ai 7 ambiti geografici italiani (Nord Occidentale, Nord Orientale, Centrale, Centro-Sud Orientale, Centro-Sud Occidentale, Meridionale, Sardegna).
  - Scelta dello scaglione di consumo annuo (da 0-120 Smc fino a oltre 5.000 Smc/anno) per calcolare la quota variabile esatta di distribuzione e oneri.
- **Dispositivi Nativi Separati**:
  - Organizza i sensori sotto due dispositivi dedicati e puliti: **ARERA Tariffe Luce** e **ARERA Tariffe Gas**.
- **Diagnostica e Trasparenza del Periodo**:
  - Ciascun sensore espone negli attributi il mese/periodo di riferimento (es. *«Settembre 2026»*), il nome del foglio Excel, l'URL sorgente e il timestamp di aggiornamento.

---

## 📦 Installazione

### Metodo 1: Tramite HACS (Consigliato)

1. Apri **HACS** in Home Assistant.
2. Vai su **Integrazioni** -> Menu tre puntini in alto a destra -> **Repository personalizzati**.
3. Incolla `https://github.com/evlas/Arera.git`, seleziona la categoria **Integrazione** e clicca **Aggiungi**.
4. Cerca **ARERA Tariffe Regolate** e clicca su **Scarica**.
5. Riavvia Home Assistant.

### Metodo 2: Installazione Manuale

1. Copia la cartella `custom_components/arera` nella directory `/config/custom_components/arera/` della tua installazione di Home Assistant.
2. Riavvia Home Assistant.

---

## ⚙️ Configurazione

1. In Home Assistant, vai su **Impostazioni** -> **Dispositivi e Servizi** -> **Aggiungi Integrazione**.
2. Cerca **ARERA Tariffe**.
3. Seleziona il servizio che desideri configurare:
   - **Energia Elettrica**
   - **Gas Naturale**
4. Completa la configurazione del servizio scelto:
   - Per l'**Energia Elettrica**: seleziona la sorgente dati (predefinito: *Tabelle Ufficiali ARERA Online*) e l'intervallo di aggiornamento.
   - Per il **Gas Naturale**: indica il tuo **Ambito Geografico** (es. *Nord Orientale*) e lo **Scaglione di Consumo Annuo** (predefinito: *Scaglione 3: da 481 a 1.560 Smc/anno* per riscaldamento autonomo).
5. Se desideri monitorare **entrambe le forniture**, ti basterà ripetere la procedura cliccando nuovamente su *Aggiungi Integrazione* e selezionando l'altro servizio. Home Assistant creerà due istanze pulite e dedicate con i rispettivi dispositivi e sensori.

---

## 📑 Entità Create

### ⚡ Dispositivo: ARERA Tariffe Luce

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
| `sensor.arera_dispbt` | Corrispettivo di Dispacciamento BT | EUR/anno | $\text{DispBT}$ |
| `sensor.arera_cdispd` | Dispacciamento Domestici all'Ingrosso | EUR/kWh | $\text{CDISPD}$ |
| `sensor.arera_csed` | Sbilanciamento Efficiente | EUR/kWh | $\text{CSED}$ |
| `sensor.arera_cpstgd` | Perequazione Servizio Tutele Graduali | EUR/kWh | $\text{CPSTGD}$ |
| `sensor.arera_parametro_lamda` | Parametro Lambda Tutele Graduali | EUR/anno | $\lambda$ |
| `sensor.arera_ultimo_aggiornamento` | Periodo di riferimento tariffe luce | - | es. «Settembre 2026» |

### 🔥 Dispositivo: ARERA Tariffe Gas

| Entità | Descrizione | Unità | Componente ARERA |
| :--- | :--- | :--- | :--- |
| `sensor.arera_gas_cmemm` | Prezzo Materia Prima Gas all'Ingrosso | EUR/Smc | $\text{CMEM}_m$ |
| `sensor.arera_gas_ccr` | Corrispettivo Approvvigionamento | EUR/Smc | $\text{CCR}$ |
| `sensor.arera_gas_qvd_variabile` | Vendita al Dettaglio Quota Variabile | EUR/Smc | $\text{QVD}_v$ |
| `sensor.arera_gas_tau3` | Distribuzione e Misura Quota Variabile | EUR/Smc | $\tau_3$ |
| `sensor.arera_gas_qt` | Quota Trasporto Gas | EUR/Smc | $\text{QT}$ |
| `sensor.arera_gas_rs` | Recupero Qualità del Servizio Gas | EUR/Smc | $\text{RS}$ |
| `sensor.arera_gas_ug1` | Perequazione Costi Distribuzione | EUR/Smc | $\text{UG}_1$ |
| `sensor.arera_gas_re` | Risparmio Energetico Gas | EUR/Smc | $\text{RE}$ |
| `sensor.arera_gas_ug2_variabile` | Oneri Commercializzazione Variabile | EUR/Smc | $\text{UG}_{2v}$ |
| `sensor.arera_gas_ug3` | Recupero Morosità Clienti Vulnerabili | EUR/Smc | $\text{UG}_3$ |
| `sensor.arera_gas_totale_variabile` | **Totale Spesa Variabile Gas** | EUR/Smc | Somma quote variabili |
| `sensor.arera_gas_qvd_fissa` | Vendita al Dettaglio Quota Fissa | EUR/anno | $\text{QVD}_f$ |
| `sensor.arera_gas_tau1` | Distribuzione e Misura Quota Fissa (G6) | EUR/anno | $\tau_1$ |
| `sensor.arera_gas_ug2_fissa` | Oneri Commercializzazione Quota Fissa | EUR/anno | $\text{UG}_{2f}$ |
| `sensor.arera_gas_totale_fissa` | **Totale Spesa Fissa Annua Gas** | EUR/anno | Somma quote fisse |
| `sensor.arera_gas_periodo` | Periodo di riferimento tariffe gas | - | es. «Settembre 2026» |

---

## 🎛️ Esempio Scheda Lovelace

```yaml
type: vertical-stack
cards:
  - type: entities
    title: ⚡ ARERA Tariffe Luce
    show_header_toggle: false
    entities:
      - entity: sensor.arera_ultimo_aggiornamento
        name: Periodo di Riferimento
      - entity: sensor.arera_quota_fissa
        name: Quota Fissa Rete (s1)
      - entity: sensor.arera_quota_potenza
        name: Quota Potenza Rete (s2)
      - entity: sensor.arera_quota_energia
        name: Quota Energia Rete (s3)
      - entity: sensor.arera_asos
        name: Oneri Rinnovabili (ASOS)
      - entity: sensor.arera_arim
        name: Altri Oneri (ARIM)
      - entity: sensor.arera_dispbt
        name: DispBT (Dispacciamento)

  - type: entities
    title: 🔥 ARERA Tariffe Gas Naturale
    show_header_toggle: false
    entities:
      - entity: sensor.arera_gas_periodo
        name: Periodo di Riferimento
      - entity: sensor.arera_gas_totale_fissa
        name: Spesa Fissa Annua (G6)
      - entity: sensor.arera_gas_totale_variabile
        name: Spesa Variabile al Metro Cubo
      - type: divider
      - entity: sensor.arera_gas_cmemm
        name: Materia Prima (CMEMm)
      - entity: sensor.arera_gas_tau1
        name: Quota Fissa Distribuzione (tau1)
      - entity: sensor.arera_gas_tau3
        name: Quota Variabile Distribuzione (tau3)
      - entity: sensor.arera_gas_qt
        name: Trasporto (QT)
```

---

## 📄 Licenza

Rilasciato sotto licenza [GNU General Public License v3.0](LICENSE).
