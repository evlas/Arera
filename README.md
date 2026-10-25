# ARERA Tariffe Luce per Home Assistant

Integrazione personalizzata (compatibile **HACS**) per il monitoraggio e l'acquisizione delle tariffe regolate **ARERA** per l'energia elettrica (servizi di rete, oneri generali di sistema, dispacciamento e perequazione).

---

## ⚡ Caratteristiche
- **Acquisizione Automatica**: interroga periodicamente un endpoint JSON locale (es. `http://192.168.70.50/arera/arera.json`) o un URL online.
- **Valori Ufficiali Integrati (Fallback)**: se l'endpoint non è raggiungibile o non viene fornito un URL, l'integrazione utilizza i valori ufficiali ARERA predefiniti senza mai andare in errore.
- **Configurazione da UI (Config Flow)**: imposta e modifica l'URL e l'intervallo di polling direttamente da *Impostazioni -> Dispositivi e Servizi*.
- **Override Parametri nelle Opzioni**: possibilità di impostare manualmente singoli valori delle tariffe.
- **Dispositivo Dedicato**: tutte le componenti tariffarie sono raggruppate sotto il dispositivo **ARERA Tariffe Regolate**.

---

## 📦 Struttura del Repository
```
Arera/
├── custom_components/
│   └── arera/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── coordinator.py
│       ├── config_flow.py
│       ├── sensor.py
│       └── translations/
│           ├── it.json
│           └── en.json
├── hacs.json
├── arera_sample.json
└── README.md
```

---

## 📊 Entità Create

| Sensore | Descrizione | Unità |
| :--- | :--- | :--- |
| `sensor.arera_quota_fissa` | Quota Fissa Trasporto e Gestione Contatore ($\sigma_1$) | €/anno |
| `sensor.arera_quota_potenza` | Quota Potenza Trasporto e Gestione Contatore ($\sigma_2$) | €/kW/anno |
| `sensor.arera_quota_energia` | Quota Energia Trasporto e Gestione Contatore ($\sigma_3$) | €/kWh |
| `sensor.arera_uc3` | Perequazione Costi di Trasporto (UC3) | €/kWh |
| `sensor.arera_uc6_qe` | Recuperi Qualità Servizio - Quota Energia (UC6) | €/kWh |
| `sensor.arera_uc6_qp` | Recuperi Qualità Servizio - Quota Potenza (UC6) | €/kW/anno |
| `sensor.arera_asos` | Oneri Generali Sostegno Energie Rinnovabili (ASOS) | €/kWh |
| `sensor.arera_arim` | Rimanenti Oneri Generali di Sistema (ARIM) | €/kWh |
| `sensor.arera_dispbt` | Componente di Dispacciamento Bassa Tensione (DispBT) | €/anno |
| `sensor.arera_cdispd` | Corrispettivo di Dispacciamento Domestici (CDISPD) | €/kWh |
| `sensor.arera_csed` | Corrispettivo di Sbilanciamento Efficiente Domestici (CSED) | €/kWh |
| `sensor.arera_cpstgd` | Perequazione Servizio a Tutele Graduali (CPSTGD) | €/kWh |
| `sensor.arera_parametro_lamda` | Parametro Lambda | €/anno |
| `sensor.arera_ultimo_aggiornamento` | Data/ora dell'ultimo aggiornamento tariffe | - |

---

## 🚀 Installazione

### Tramite HACS
1. In HACS -> *Integrazioni* -> *Repository personalizzati*.
2. Aggiungi questo repository come categoria **Integrazione**.
3. Clicca su **Scarica** e riavvia Home Assistant.
4. Vai su **Impostazioni** -> **Dispositivi e Servizi** -> **Aggiungi Integrazione** -> Cerca **ARERA Tariffe Luce**.
