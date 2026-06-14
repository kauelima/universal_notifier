# 📢 Universal Notifier
Un nuovo rilascio di un'appdaemon app di @caiosweet e @jumping2000

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/jumping2000/universal_notifier?style=for-the-badge)
![GitHub Release Date](https://img.shields.io/github/release-date/jumping2000/universal_notifier?style=for-the-badge)
![GitHub stars](https://img.shields.io/github/stars/jumping2000/universal_notifier?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/jumping2000/universal_notifier?style=for-the-badge)
![License](https://img.shields.io/github/license/jumping2000/universal_notifier?style=for-the-badge)
![HA integration](https://img.shields.io/badge/Home%20Assistant-Integration-blue?style=for-the-badge)

> **🆕 Ultima versione (v0.8.0):** DND separato feriali/festivi, supporto multi-target con valori separati da virgola. Guarda il [Changelog](CHANGELOG.md) per i dettagli.
>
> [Guida utente alla configurazione](USER_GUIDE_IT.md)
>
> 🇬🇧 [English Version](README.md)

### Offrimi un caffè e dammi una stella ✨!
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jumping)

___

**Universal Notifier** è un componente custom per Home Assistant che centralizza e potenzia la gestione delle notifiche.

Trasforma semplici automazioni in un sistema di comunicazione "Smart Home" che conosce l'ora del giorno, rispetta il tuo sonno (DND), saluta in modo naturale e gestisce automaticamente il volume degli assistenti vocali.

## 🚀 Caratteristiche Principali 🇮🇹

* **Piattaforma Unificata:** Un solo servizio (`universal_notifier.send`) per Telegram, App Mobile, Alexa, Google Home, ecc.
* **Notifiche personalizzate** a più destinatari (ad esempio, notifica di allarme sia a Telegram che ad Alexa)
* **Voce vs Testo:** Distingue automaticamente tra messaggi da leggere (con prefissi `[Jarvis - 12:30]`) e messaggi da pronunciare (solo testo pulito).
* **Time Slots & Volume Smart:** Imposta volumi diversi per Mattina, Pomeriggio, Sera e Notte. Il componente regola il volume *prima* di parlare.
* **Do Not Disturb (DND):** Definisci un orario di silenzio per gli assistenti vocali. Le notifiche critiche (`priority: true`) passano comunque.
* **Saluti Casuali:** "Buongiorno", "Buon pomeriggio", ecc., scelti casualmente da liste personalizzabili.
* **Gestione Comandi:** Supporto nativo per comandi Companion App (es. `TTS`, `command_volume_level`) inviati in modalità "RAW".
* **Coda Intelligente (FIFO):** Le notifiche vocali vengono gestite da un worker in background tramite asyncio.Queue. Questo impedisce la sovrapposizione audio riproducendo i messaggi in sequenza.
* **Snapshot e Ripristino:** Il sistema salva lo stato (volume, traccia e app) dei lettori multimediali prima di una notifica e tenta di ripristinarlo dopo che l'intera coda è stata svuotata.

### 📊 Monitoraggio & Diagnostica - Entità

| Entità | Tipo | Descrizione |
|:---|:---|:---|
| **Volume** | Sensor | Mostra in tempo reale la percentuale di volume che verrà usata per la prossima notifica, calcolata automaticamente in base alla fascia oraria attiva. Icona dinamica in base al livello. Attributi extra: `current_slot`, `raw_volume`. |
| **Family** | Sensor | Traccia lo stato di presenza della famiglia (`home` / `not_home`) in base alle entità `person` configurate. |
| **DND** | Binary Sensor | Indica se la modalità "Non Disturbare" è attualmente attiva o inattiva. |
| **Voice Buffer** | Number | Tempo di buffer regolabile (0.5–10.0 s, step 0.5) per la riproduzione TTS, per garantire la consegna completa del messaggio. Default: 1.5 s. |
| **Priority Volume** | Select | Imposta il livello di volume per le notifiche prioritarie. Opzioni: da 0.1 a 1.0. |
| **Text Format** | Select | Seleziona il formato di testo per le notifiche: `html` o `markdown`. |
| **Notification Mode** | Select | Controlla l'instradamento delle notifiche in base alla presenza: `Normal` (tutte passano), `Voice home` (voce solo se in casa), `Text home` (solo testo, niente voce). |
| **Default Media Players** | Sensor | Mostra i media player predefiniti configurati per i canali vocali. Stato: numero di canali con un default. Attributi: mappa `{alias_canale: media_player.xxx}`. |
| **DND Override** | Switch | Forza la modalità "Non Disturbare" indipendentemente dall'orario programmato. Utile per attivare manualmente la modalità silenziosa in qualsiasi momento. |
| **Last Message Sent** | Text | Memorizza il testo dell'ultima notifica inviata (max 255 caratteri). Aggiornato automaticamente ad ogni chiamata a `universal_notifier.send`. |

___

## 🛠️ Installazione

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jumping2000&repository=universal_notifier&category=Integration)

<details>
<summary>Clicca per mostrare le istruzioni di installazione</summary>
<ol>
<li>Installare i file:</li>
<ul>
<li><u>Tramite HACS:</u><br>
Nel pannello HACS, cerca 'Universal Notifier', apri il repository e clicca 'Download'.</li>
<li><u>Manualmente:</u><br>
Scarica l'<a href="https://github.com/jumping2000/universal_notifier/releases">ultima release</a> come file zip ed estraila nella cartella `custom_components` della tua installazione HA.</li>
</ul>
<li>Riavvia HA per caricare l'integrazione.</li>
<li>Vai in Impostazioni -> Dispositivi e servizi e clicca 'AGGIUNGI INTEGRAZIONE'. Cerca Universal Notifier e clicca per aggiungerlo.</li>
<li>L'integrazione Universal Notifier è pronta per la configurazione YAML.</li>
</ol>
</details>

## 🔗 Prerequisiti
<details>
  <summary>Clicca per espandere</summary>

Prima di configurare Universal Notifier, assicurati di aver installato e configurato le integrazioni di notifica sottostanti che intendi utilizzare:
* **Google Home / TTS**: Installa l'integrazione Google Translate [Text-to-Speech (TTS)](https://www.home-assistant.io/integrations/tts) per abilitare gli annunci vocali sui dispositivi Google Assistant.
* **Alexa / Echo Devices**: Installa l'[Alexa Media Player Custom Component](https://github.com/alandtse/alexa_media_player) (tramite HACS) per consentire a Home Assistant di inviare annunci e impostare il volume sui dispositivi Echo.
* **Telegram**: Configura e installa l'integrazione [Telegram Bot](https://www.home-assistant.io/integrations/telegram_bot/) per inviare messaggi visivi.
* **Mobile App**: Assicurati che l'integrazione [Mobile App](https://companion.home-assistant.io/) sia attiva e configurata per i tuoi dispositivi (solitamente si configura automaticamente quando accedi tramite l'app).

Questo componente funge da "router"; i servizi di destinazione devono essere disponibili per funzionare correttamente.
</details>

## ⚙️ Configurazione (UI)

Universal Notifier è completamente configurabile dall'interfaccia utente di Home Assistant. Non è necessaria alcuna configurazione YAML.

<details>
  <summary>Clicca per espandere</summary>

### Configurazione Iniziale

Dopo aver installato l'integrazione, vai in **Impostazioni > Dispositivi e servizi > Aggiungi integrazione** e cerca **Universal Notifier**. La procedura guidata ti accompagnerà nei seguenti passaggi:

#### Passaggio 1 — Impostazioni Globali & Do Not Disturb
| Impostazione | Descrizione | Default |
|:---|:---|:---|
| Nome Assistente | Nome visualizzato nei prefissi dei messaggi di testo (es. `[Jarvis - 12:30]`) | `Jarvis` |
| Formato Ora | Formato strftime per il prefisso temporale | `%H:%M` |
| Includi Ora nel Prefisso | Se mostrare l'ora nelle notifiche di testo | `true` |
| Prefisso in Grassetto | Se mettere in grassetto il nome dell'assistente e l'ora | `true` |
| Volume Prioritario | Volume usato con `priority: true` (0.0 – 1.0) | `0.9` |
| Entità Person | Entità person opzionali per il rilevamento presenza | — |
| Inizio DND | Orario di inizio "Non Disturbare" (HH:MM) | `23:00` |
| Fine DND | Orario di fine "Non Disturbare" (HH:MM) | `06:00` |

#### Passaggio 2 — Time Slots
Imposta l'orario di inizio e il volume TTS predefinito per ogni periodo della giornata.

| Fascia Oraria | Inizio Predefinito | Volume Predefinito |
|:---|:---|:---|
| Mattina | 07:00 | 0.35 |
| Pomeriggio | 12:00 | 0.4 |
| Sera | 19:00 | 0.3 |
| Notte | 22:00 | 0.1 |

#### Passaggio 3 — Saluti
Inserisci un saluto per riga per ogni fascia oraria. Un saluto casuale verrà scelto ogni volta che viene inviata una notifica.

#### Passaggio 4 — Primo Canale (obbligatorio)
Devi aggiungere almeno un canale di notifica per completare la configurazione. Ogni canale richiede:

| Campo | Descrizione |
|:---|:---|
| Alias | Un nome univoco per il canale (es. `alexa_soggiorno`) |
| Service | Il servizio HA da chiamare in formato `dominio.servizio` (es. `notify.mobile_app_pixel`) |
| Target | entity_id di destinazione (opzionale, separato da virgola per più destinazioni) |
| Canale Vocale | Abilita per dispositivi TTS (applica volume, DND e logica dei saluti) |
| Servizi Alternativi | Dizionario JSON opzionale per servizi alternativi (es. foto/video Telegram) |

### Modifica della Configurazione

Dopo la configurazione iniziale, vai in **Impostazioni > Dispositivi e servizi > Universal Notifier > Configura** per accedere al menu delle opzioni:

- **Impostazioni Globali** — Modifica nome assistente, formato ora, opzioni prefisso e volume prioritario
- **Do Not Disturb** — Modifica orari di inizio/fine DND
- **Time Slots** — Regola orari di inizio e volumi per ogni periodo
- **Saluti** — Personalizza i saluti per ogni fascia oraria
- **Canali** — Aggiungi o rimuovi canali di notifica

### Piccoli consigli
- se dimentichi i canali configurati, vai in `Integrazioni` - `Universal Notifier` - `Configura` - `Canali` - `Rimuovi canale`
- per foto e video Telegram aggiungi nella configurazione del canale:
```
{
  "photo": {"service": "telegram_bot.send_photo"},
  "video": {"service": "telegram_bot.send_video"}
}
```

</details>

## 🎯 Riferimento Campi del Servizio
<details>
  <summary>Clicca per espandere</summary>

|Campo|Tipo|Obbligatorio|Descrizione|
|:---|:---|:---|:---|
|message|string|Sì|Il testo principale della notifica.|
|targets|list|Sì|Lista degli alias dei canali definiti in configuration.yaml.|
|title|string|No|Titolo della notifica (supportato da Notify e Mobile App).|
|data|dict|No|Dati extra generici applicati a TUTTI i servizi sottostanti.|
|target_data|dict|No|Dizionario {alias_target: {dati_specifici}} per override mirati.|
|priority|bool|No|Se true, ignora il DND e imposta volume alto (default 0.9).|
|skip_greeting|bool|No|Se true, non aggiunge il saluto basato sull'ora (es. Buongiorno).|
|include_time|bool|No|Sovrascrive la configurazione per includere/escludere l'ora nel prefisso visivo.|
|ignore_title_voice|bool|No|Se true, ignora il titolo per le notifiche vocali (TTS/canali voice).|
|bold_prefix|bool|No|Sovrascrive la configurazione per mettere in grassetto nome assistente e ora.|
|assistant_name|string|No|Sovrascrive il nome globale dell'assistente.|
|override_greetings|dict|No|Sovrascrive i saluti predefiniti.|

</details>

## 📝 Esempi di Utilizzo
<details>
  <summary>Clicca per espandere</summary>

#### 1. Notifica Standard (Volume Automatico)
Se inviata alle 15:00, userà il volume del pomeriggio (0.60). Se inviata alle 02:00 (DND attivo), Alexa verrà saltato, ma Telegram riceverà il messaggio.

```yaml
action: universal_notifier.send
data:
  message: "Il bucato è finito."
  targets:
    - alexa_soggiorno
    - telegram_admin
```

#### 2. Notifica Prioritaria (Ignora DND e imposta Volume al 90%)
Usa il flag priority per avvisi critici.

```yaml
action: universal_notifier.send
data:
  title: "ALLARME CRITICO"
  message: "Rilevata perdita d'acqua, valvola chiusa!"
  priority: true        # <--- FORZA INVIO E VOLUME MASSIMO (0.9)
  skip_greeting: true   # <--- Evita saluti come "Buonanotte" durante un allarme
  targets:
    - alexa_soggiorno
    - telegram_bob
```

#### 3. Comandi Companion App (Messaggi RAW)
Se il messaggio è un comando riconosciuto (come "TTS") o inizia con *command_*, saluti e prefissi vengono rimossi automaticamente.

```yaml
action: universal_notifier.send
data:
  message: "TTS" # Il componente invia "TTS" RAW, senza prefissi.
  targets:
    - my_android
  target_data:
    my_android:
      tts_text: "Il postino è alla porta."
      media_stream: alarm_stream_max
      clickAction: /lovelace/main
```

#### 4. Multi destinazione
Come inviare a più destinazioni.

```yaml
action: universal_notifier.send
data:
  message: La lavatrice ha terminato il ciclo.
  title: Avviso Lavatrice
  priority: true
  targets:
    - google_home
    - telegram_bob
    - mobile_bob
  target_data:
    google_home:
      entity_id: media_player.cucina
      volume: 0.3
    mobile_bob:
      image: "https://www.home-assistant.io/images/default-social.png"
      color: red
      channel: "lavatrice-alert"
    telegram_bob:
      type: photo
      url: "https://www.home-assistant.io/images/default-social.png"
```

</details>

## 🪲 Risoluzione Problemi
<details>
  <summary>Clicca per espandere</summary>
  
Per il debug, aggiungi in *configuration.yaml*:

```yaml
logger:
  default: info
  logs:
    custom_components.universal_notifier: debug
```

</details>
