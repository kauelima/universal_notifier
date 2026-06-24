# Universal Notifier - User Guide

This guide walks you through installing, configuring, and getting started with Universal Notifier via the Home Assistant web interface.

---

## 🚀 Installation & Initial Setup

### Step 1: Add the Integration
```
1. Settings → Devices & Services
2. Click "+ ADD INTEGRATION"
3. Search for "Universal Notifier"
4. Click the integration
```

### Step 2: Complete the Wizard

#### 📝 Step 2/1: General Settings
**Available fields:**

| Field | Default | Description |
|-------|---------|-------------|
| Assistant Name | *(empty)* | Name of the assistant (e.g. "Home Assistant") |
| Date/Time Format | `%H:%M:%S` | Timestamp format used in notifications |
| Include Time | ✓ | Appends the current time to messages |
| Bold Prefix | ✓ | Renders the message prefix in bold |
| Ignore Voice Title | ✗ | When enabled, voice titles are skipped |
| Priority Volume | 0.9 (90%) | Volume level used when `priority=True` |
| Person Entity | *(empty)* | `person.*` entity to link to this integration |
| Weekend Days | Sat, Sun | Days treated as weekend (Mon=0 ... Sun=6) |

#### 📝 Step 2/2: Do Not Disturb (DND)
**Available fields:**

| Field | Weekday Default | Weekend Default |
|-------|----------------|-----------------|
| DND Start | 23:00 | 00:00 |
| DND End | 06:00 | 08:00 |

> **Note:** DND schedules are configured independently for weekdays and weekends.

Click **SUBMIT**

#### 📝 Step 2/3: Time Slots

Set up time slots for **weekdays** and **weekends** separately. For each slot, specify a **start time** and a **volume** level (0.0 – 1.0).

**Weekdays:**

| Slot | Default Time | Default Volume |
|------|-------------|----------------|
| Morning (`morning`) | 07:00 | 0.35 (35%) |
| Afternoon (`afternoon`) | 12:00 | 0.40 (40%) |
| Evening (`evening`) | 19:00 | 0.30 (30%) |
| Night (`night`) | 21:30 | 0.10 (10%) |

**Weekend:**

| Slot | Default Time | Default Volume |
|------|-------------|----------------|
| Morning (`morning`) | 08:00 | 0.30 (30%) |
| Afternoon (`afternoon`) | 14:00 | 0.40 (40%) |
| Evening (`evening`) | 19:00 | 0.30 (30%) |
| Night (`night`) | 22:30 | 0.10 (10%) |

Click **SUBMIT**


#### 📝 Step 2/4: Greetings

Define the greetings used in voice notifications for each time slot. Enter **one greeting per line** in the text area.

**Defaults:**

| Slot | Greetings |
|------|-----------|
| Morning | Good morning, Rise and shine, Hello, Good day |
| Afternoon | Good afternoon, Hi, Welcome back |
| Evening | Good evening, Good night, Welcome home |
| Night | Goodnight, Sweet dreams, It's late |

> **Note:** A random greeting is picked from the corresponding list each time a notification is sent.

Click **SUBMIT**

---

#### 📝 Step 2/5: Channel Menu
```
Configured channels:
(none yet)

Action: [Add new channel]
```
Click **SUBMIT**


#### 📝 Step 2/6: Add a Channel (repeat for each channel)

| Field | Required | Description |
|-------|----------|-------------|
| Alias | ✓ | A unique name for the channel (e.g. `alexa_living_room`) |
| Service | ✓ | Full Home Assistant service name (e.g. `notify.alexa_media_echo_dot`) |
| Target | ✗ | Service target (leave blank if not needed) |
| Is Voice | ✗ | Whether the channel uses voice / TTS |
| Fallback Services | ✗ | JSON object with fallback services, e.g. `{"fallback": "notify.xxx"}` |
| Default Media Player | ✗ | `media_player.*` entity selector for audio output |

**Alexa example:**
```
Channel name: alexa_living_room
Service: notify.alexa_media_echo_dot
Target: (leave blank)
Entity ID: (leave blank)
Is Voice: ✓
```
Click **SUBMIT** → Returns to the channel menu

**Google Home example:**
```
Channel name: gh_kitchen
Service: tts.google_translate_say
Target: tts.google_translate_it_it
Entity ID: media_player.kitchen
Is Voice: ✓
```
Click **SUBMIT** → Returns to the channel menu

**Mobile App example:**
```
Channel name: mobile_app_user
Service: notify.mobile_app_phone
Target: (leave blank)
Entity ID: (leave blank)
Is Voice: ✗
```
Click **SUBMIT** → Returns to the channel menu

Once all channels have been added:
```
Action: [Finish setup]
```
Click **SUBMIT**

#### 📝 Step 2/7: Done
The wizard closes and the integration is ready to use!

---

## 🎯 Verifying the Installation

### 1. Check the Integration
```
Settings → Devices & Services

You should see:
┌─────────────────────────────────┐
│ Universal Notifier (Home Ass... │
│ 10 entities                     │
│ 1 service                       │
└─────────────────────────────────┘
```

### 2. Check the Entities
```
Developer Tools → States

Search for:
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

### 3. Check the Service
```
Developer Tools → Services

Search for:
✓ universal_notifier.send
```

### 4. Send a Test Notification
```yaml
# Developer Tools → Services
service: universal_notifier.send
data:
  message: "Test notification from the UI!"
  targets:
    - alexa_living_room
    - mobile_app_user
```

Click **CALL SERVICE**

If the notification arrives → **✅ Installation complete!**

---

## 🔧 Changing Configuration After Setup

### Opening the Options Flow
```
Settings → Devices & Services
→ Universal Notifier
→ CONFIGURE
```

### Available Sections
```
○ General settings
  - Assistant name
  - Date format
  - Include time
  - Bold prefix
  - Ignore title
  - Priority volume
  - Person entity
  - Weekend days

○ Do Not Disturb
  - Weekday DND start
  - Weekday DND end
  - Weekend DND start
  - Weekend DND end

○ Time Slots
  - All schedules and volume levels

○ Greetings
  - Morning greetings
  - Afternoon greetings
  - Evening greetings
  - Night greetings

○ Notification Channels
  - Add a new channel
  - Remove existing channels
  - Edit existing channels
```

---

## 📊 Entities Created

### 1. binary_sensor.universal_notifier_dnd
```yaml
State: on/off
Icon: mdi:bell-off (on) / mdi:bell-ring (off)
Attributes:
  dnd_start: "23:00"
  dnd_end: "07:00"
```

**Example automation:**
```yaml
trigger:
  - platform: state
    entity_id: binary_sensor.universal_notifier_dnd
    to: "off"
action:
  - service: universal_notifier.send
    data:
      message: "DND ended — good morning!"
      targets: [alexa_living_room]
```

### 2. sensor.universal_notifier_volume
```yaml
State: 35 (%)
Icon: mdi:volume-off/low/medium/high (dynamic)
Attributes:
  current_slot: "morning"
  raw_volume: 0.35
  time_slots: {...}
```

**Example automation:**
```yaml
trigger:
  - platform: state
    entity_id: sensor.universal_notifier_volume
action:
  - service: notify.persistent_notification
    data:
      message: "Volume changed to {{ states('sensor.universal_notifier_volume') }}%"
```

### 3. select.universal_notifier_priority_volume
```yaml
State: "0.9"
Icon: mdi:volume-high
Attributes:
  decimal_value: 0.9
  percentage: "90%"
  description: "Volume used when priority=True"
Options:
  - "0.1" (10%)
  - "0.2" (20%)
  - ...
  - "1.0" (100%)
```

**Example automation:**
```yaml
# Set volume to maximum at night
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

**Example notification call:**
```yaml
service: universal_notifier.send
data:
  message: "EMERGENCY!"
  targets: [alexa_living_room]
  priority: true  # Uses the priority volume from the select entity (1.0)
```

---

## 🎨 Dashboard Example

```yaml
type: vertical-stack
cards:
  # Status card
  - type: entities
    title: Universal Notifier
    entities:
      - entity: binary_sensor.universal_notifier_dnd
        name: Do Not Disturb
      - entity: sensor.universal_notifier_volume
        name: Current Volume
      - entity: select.universal_notifier_priority_volume
        name: Priority Volume
  
  # Volume gauge
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
  
  # Test button
  - type: button
    name: Test Notification
    icon: mdi:bell-ring
    tap_action:
      action: call-service
      service: universal_notifier.send
      service_data:
        message: Test from the dashboard!
        targets:
          - alexa_living_room
```

---

## 🐛 Troubleshooting

### The integration doesn't appear

**Fix:**
```bash
# 1. Verify manifest.json
cat /config/custom_components/universal_notifier/manifest.json | grep config_flow
# Expected output: "config_flow": true

# 2. Check the logs
tail -f /config/home-assistant.log | grep universal_notifier

# 3. Restart Home Assistant
# Settings → System → Restart
```

### Entities are missing

**Fix:**
```bash
# Confirm the files are in place
ls -la /config/custom_components/universal_notifier/ | grep -E "(binary_sensor|sensor|select).py"

# Expected output:
# binary_sensor.py
# sensor.py
# select.py

# Check the logs for errors
grep -i "universal_notifier" /config/home-assistant.log | grep -i error
```

### Service calls fail

**Fix:**
```yaml
# 1. Make sure at least one channel is configured
# Settings → Devices & Services → Universal Notifier → CONFIGURE

# 2. Try a simple test
service: universal_notifier.send
data:
  message: "Test"
  targets: [configured_channel_name]

# 3. Check the logs
tail -f /config/home-assistant.log | grep UniNotifier
```

### Select entity won't update

**Fix:**
```yaml
# Developer Tools → Services
service: homeassistant.reload_config_entry
target:
  entity_id: select.universal_notifier_priority_volume
```

---

## ✅ Final Checklist

### Installation
- [ ] Integration added from the UI
- [ ] Wizard completed
- [ ] At least one channel configured
- [ ] 10 entities visible
- [ ] Service available

### Testing
- [ ] Test notification sent successfully
- [ ] DND entity working
- [ ] Volume entity working
- [ ] Priority Volume select working
- [ ] Options Flow accessible

---

## 🎉 All Done!

Universal Notifier is installed and ready to go!

Enjoy! 🚀
