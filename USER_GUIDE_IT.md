# Universal Notifier - Guida Utente

Questa guida copre l'installazione, la configurazione attraverso l'interfaccia web di Home Assistant e l'utilizzo iniziale di Universal Notifier 

---

## 🚀 Installazione e Configurazione Iniziale

### Step 1: Aggiungi Integrazione
```
1. Settings → Devices & Services
2. Click su "+ ADD INTEGRATION"
3. Cerca "Universal Notifier"
4. Click sull'integrazione
```

### Step 2: Completa il Wizard

#### 📝 Step 2/1: Impostazioni Globali
**Campi disponibili:**

| Campo | Default | Descrizione |
|-------|---------|-------------|
| Nome Assistente | *(vuoto)* | Nome dell'assistente (es. "Home Assistant") |
| Formato Data/Ora | `%H:%M:%S` | Formato per i timestamp nelle notifiche |
| Includi Orario | ✓ | Aggiunge l'orario al messaggio |
| Prefisso Grassetto | ✓ | Formatta il prefisso in grassetto |
| Ignora Titolo Vocale | ✗ | Se attivo, i titoli vocali vengono ignorati |
| Volume Priorità | 0.9 (90%) | Volume usato quando `priority=True` |
| Entità Person | *(vuoto)* | Entità `person.*` da associare |
| Giorni Weekend | Sab, Dom | Giorni considerati weekend (Lun=0 ... Dom=6) |

#### 📝 Step 2/2: Do Not Distrurb DND
**Campi disponibili:**

| Campo | Default Feriale | Default Weekend |
|-------|----------------|-----------------|
| Inizio DND | 23:00 | 00:00 |
| Fine DND | 06:00 | 08:00 |

> **Nota:** Il DND è configurato separatamente per feriali e weekend.

Click **SUBMIT**

#### 📝 Step 2/3: Fasce Orarie

Configura le fasce orarie per **feriali** e **weekend** indipendentemente. Per ogni fascia definisci l'**orario di inizio** e il **volume** (0.0 - 1.0).

**Feriali (Weekday):**

| Fascia | Orario Default | Volume Default |
|--------|---------------|----------------|
| Mattino (`morning`) | 07:00 | 0.35 (35%) |
| Pomeriggio (`afternoon`) | 12:00 | 0.40 (40%) |
| Sera (`evening`) | 19:00 | 0.30 (30%) |
| Notte (`night`) | 21:30 | 0.10 (10%) |

**Weekend:**

| Fascia | Orario Default | Volume Default |
|--------|---------------|----------------|
| Mattino (`morning`) | 08:00 | 0.30 (30%) |
| Pomeriggio (`afternoon`) | 14:00 | 0.40 (40%) |
| Sera (`evening`) | 19:00 | 0.30 (30%) |
| Notte (`night`) | 22:30 | 0.10 (10%) |

Click **SUBMIT**


#### 📝 Step 2/4: Saluti

Definisci i saluti da usare nelle notifiche vocali per ogni fascia oraria. Inserisci **un saluto per riga** nel campo multilinea.

**Default:**

| Fascia | Saluti |
|--------|--------|
| Mattino | Buongiorno, Ben alzato, Salve, Buondì |
| Pomeriggio | Buon pomeriggio, Ciao, Ben ritrovato |
| Sera | Buonasera, Buona serata, Ben tornato a casa |
| Notte | Buonanotte, Sogni d'oro, È tardi |

> **Nota:** Un saluto casuale viene scelto da ogni lista per ogni notifica.

Click **SUBMIT**

---

#### 📝 Step 2/5: Menu Canali
```
Canali configurati:
(nessuno ancora)

Action: [Aggiungi nuovo canale]
```
Click **SUBMIT**


#### 📝 Step 2/6: Aggiungi Canale (Ripeti per ogni canale)

| Campo | Obbligatorio | Descrizione |
|-------|-------------|-------------|
| Alias | ✓ | Nome univoco del canale (es. `alexa_salotto`) |
| Servizio | ✓ | Servizio HA completo (es. `notify.alexa_media_echo_dot`) |
| Target | ✗ | Target del servizio (lascia vuoto se non necessario) |
| È Vocale | ✗ | Se il canale è vocale (TTS) |
| Servizi Alternativi | ✗ | JSON con servizi alternativi `{"fallback": "notify.xxx"}` |
| Media Player Default | ✗ | Selettore entity `media_player.*` per output audio |

**Esempio Alexa:**
```
Nome Canale: alexa_salotto
Servizio: notify.alexa_media_echo_dot
Target: (lascia vuoto)
Entity ID: (lascia vuoto)
È Vocale: ✓
```
Click **SUBMIT** → Torna al menu canali

**Esempio Google Home:**
```
Nome Canale: gh_cucina
Servizio: tts.google_translate_say
Target: tts.google_translate_it_it
Entity ID: media_player.cucina
È Vocale: ✓
```
Click **SUBMIT** → Torna al menu canali

**Esempio Mobile App:**
```
Nome Canale: mobile_app_user
Servizio: notify.mobile_app_phone
Target: (lascia vuoto)
Entity ID: (lascia vuoto)
È Vocale: ✗
```
Click **SUBMIT** → Torna al menu canali

Dopo aver aggiunto tutti i canali:
```
Action: [Termina configurazione]
```
Click **SUBMIT**

#### 📝 Step 2/7: Fine
Il wizard termina e l'integrazione è configurata!

---

## 🎯 Verifica Installazione

### 1. Verifica Integrazione
```
Settings → Devices & Services

Dovresti vedere:
┌─────────────────────────────────┐
│ Universal Notifier (Home Ass... │
│ 10 entities                     │
│ 1 service                       │
└─────────────────────────────────┘
```

### 2. Verifica Entità
```
Developer Tools → States

Cerca:
✓ binary_sensor.universal_notifier_dnd
✓ sensor.universal_notifier_volume
✓ sensor.universal_notifier_family
✓ sensor.universal_notifier_default_player
✓ select.universal_notifier_priority_volume
✓ select.universal_notifier_text_format
✓ select.universal_notifier_notification_mode
✓ number.universal_notifier_voice_buffer
✓ text.universal_notifier_last_message_sent
✓ switch.universal_notifier_dnd_override

```

### 3. Verifica Servizio
```
Developer Tools → Services

Cerca:
✓ universal_notifier.send
```

### 4. Test Notifica
```yaml
# Developer Tools → Services
service: universal_notifier.send
data:
  message: "Test notifica da UI!"
  targets:
    - alexa_salotto
    - mobile_app_user
```

Click **CALL SERVICE**

Se ricevi la notifica → **✅ Installazione completata!**

---

## 🔧 Modifica Configurazione Post-Setup

### Accesso Options Flow
```
Settings → Devices & Services
→ Universal Notifier
→ CONFIGURE
```

### Menu Disponibili
```
○ Impostazioni globali
  - Nome assistente
  - Formato data
  - Include time
  - Bold prefix
  - Ignora titolo
  - Priority volume
  - Entita' persona
  - Giorni weekend

○ Non distrurbare
  - DND Feriale Inizio
  - DND Feriale Fine
  - DND Weekend Inizio
  - DND Weekend Fine

○ Fasce Orarie 
  - Tutti gli orari e volumi

○ Saluti
  - Saluti mattina
  - Saluti pomeriggio
  - Saluti sera
  - Saluti notte

○ Canali di Notifica
  - Aggiungi nuovo canale
  - Rimuovi canali esistenti
  - Modifica canali esistenti
```

---

## 📊 Entità Create

### 1. binary_sensor.universal_notifier_dnd
```yaml
State: on/off
Icon: mdi:bell-off (on) / mdi:bell-ring (off)
Attributes:
  dnd_start: "23:00"
  dnd_end: "07:00"
```

**Uso in Automazione:**
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.universal_notifier_dnd
    to: "off"
action:
  - service: universal_notifier.send
    data:
      message: "DND terminato, buongiorno!"
      targets: [alexa_salotto]
```

### 2. sensor.universal_notifier_volume
```yaml
State: 35 (%)
Icon: mdi:volume-off/low/medium/high (dinamico)
Attributes:
  current_slot: "morning"
  raw_volume: 0.35
  time_slots: {...}
```

**Uso in Automazione:**
```yaml
trigger:
  - platform: state
    entity_id: sensor.universal_notifier_volume
action:
  - service: notify.persistent_notification
    data:
      message: "Volume cambiato a {{ states('sensor.universal_notifier_volume') }}%"
```

### 3. select.universal_notifier_priority_volume
```yaml
State: "0.9"
Icon: mdi:volume-high
Attributes:
  decimal_value: 0.9
  percentage: "90%"
  description: "Volume usato quando priority=True"
Options:
  - "0.1" (10%)
  - "0.2" (20%)
  - ...
  - "1.0" (100%)
```

**Uso in Automazione:**
```yaml
# Imposta volume massimo di notte
trigger:
  - platform: time
    at: "23:00:00"
action:
  - service: select.select_option
    target:
      entity_id: select.universal_notifier_priority_volume
    data:
      option: "1.0"
```

**Uso in Notifica:**
```yaml
service: universal_notifier.send
data:
  message: "EMERGENZA!"
  targets: [alexa_salotto]
  priority: true  # Userà il volume del select (1.0)
```

---

## 🎨 Dashboard Example

```yaml
type: vertical-stack
cards:
  # Card Status
  - type: entities
    title: Universal Notifier
    entities:
      - entity: binary_sensor.universal_notifier_dnd
        name: Non Disturbare
      - entity: sensor.universal_notifier_volume
        name: Volume Corrente
      - entity: select.universal_notifier_priority_volume
        name: Volume Priorità
  
  # Card Gauge Volume
  - type: gauge
    entity: sensor.universal_notifier_volume
    name: Volume
    needle: true
    min: 0
    max: 100
    severity:
      green: 0
      yellow: 34
      orange: 67
      red: 90
  
  # Card Test
  - type: button
    name: Test Notifica
    icon: mdi:bell-ring
    tap_action:
      action: call-service
      service: universal_notifier.send
      service_data:
        message: Test dalla dashboard!
        targets:
          - alexa_salotto
```

---

## 🐛 Troubleshooting

### Problema: Integrazione non appare

**Soluzione:**
```bash
# 1. Verifica manifest.json
cat /config/custom_components/universal_notifier/manifest.json | grep config_flow
# Output atteso: "config_flow": true

# 2. Controlla log
tail -f /config/home-assistant.log | grep universal_notifier

# 3. Riavvia HA
# Settings → System → Restart
```

### Problema: Entità non appaiono

**Soluzione:**
```bash
# Verifica che i file siano presenti
ls -la /config/custom_components/universal_notifier/ | grep -E "(binary_sensor|sensor|select).py"

# Output atteso:
# binary_sensor.py
# sensor.py
# select.py

# Controlla log per errori
grep -i "universal_notifier" /config/home-assistant.log | grep -i error
```

### Problema: Servizio non funziona

**Soluzione:**
```yaml
# 1. Verifica canali configurati
# Settings → Devices & Services → Universal Notifier → CONFIGURE

# 2. Test semplice
service: universal_notifier.send
data:
  message: "Test"
  targets: [nome_canale_configurato]

# 3. Controlla log
tail -f /config/home-assistant.log | grep UniNotifier
```

### Problema: Select non aggiorna

**Soluzione:**
```yaml
# Developer Tools → Services
service: homeassistant.reload_config_entry
target:
  entity_id: select.universal_notifier_priority_volume
```

---

## ✅ Checklist Finale

### Installazione
- [ ] Integrazione aggiunta da UI
- [ ] Wizard completato
- [ ] Almeno 1 canale configurato
- [ ] 10 entità visibili
- [ ] Servizio disponibile

### Test
- [ ] Notifica test inviata
- [ ] Entità DND funzionante
- [ ] Entità Volume funzionante
- [ ] Select Priority Volume funzionante
- [ ] Options Flow accessibile

---

## 🎉 Completato!

Hai installato  con successo Universal Notifier! 

Buon utilizzo! 🚀
