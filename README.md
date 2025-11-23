# Raspi Signage — Digital Signage für Raspberry Pi

Eine Flask-basierte Digital Signage Lösung für Bilder und Videos mit Web-basiertem Admin-Interface und automatischem Player.

## Features

- 📤 **Web-Admin**: Upload, Aktivierung/Deaktivierung, Reihenfolge ändern, Anzeigedauer einstellen
- 🎬 **Video & Bild Support**: Automatisches Abspielen von Images (jpg/png/gif) und Videos (mp4/mov/mkv)
- 🔄 **Live-Updates**: Playlist-Änderungen werden automatisch vom Player erkannt (kein Neustart nötig)
- 🎨 **Smooth Transitions**: Fade-Effekte zwischen allen Medien
- 🔐 **Authentifizierung**: Optionales Login-System für Admin-Bereich
- 📱 **Responsive**: Admin-UI funktioniert auf Desktop und Mobile
- 🎯 **Kiosk-Mode**: Automatisches Öffnen im Vollbildmodus (Raspberry Pi mit Chromium)

## Schnellstart

### 1. Systemabhängigkeiten installieren

**Raspberry Pi / Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install git -y
```
**Ordner erstellen (falls er noch nicht existiert)**
```bash
sudo mkdir -p /home/pi/.config/lxsession/LXDE-pi
```

**Datei „autostart“ erstellen/öffnen**
```bash
sudo nano /home/pi/.config/lxsession/LXDE-pi/autostart
```

**4. Inhalt eintragen**
```css
@chromium --kiosk --incognito http://localhost:8000
```

**neustart**
```bash
sudo reboot
```

### 2. Python-Umgebung einrichten

```bash
# Repository klonen
git clone https://github.com/Henrik168/raspi-signage.git
cd raspi-signage

# Virtual Environment erstellen und aktivieren
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder: .venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 3. Starten

**Entwicklung (mit Auto-Browser-Öffnung):**
```bash
python signage.py
# Öffnet automatisch Browser mit Player und Admin-UI
# Player: http://127.0.0.1:8000/
# Admin:  http://127.0.0.1:8000/admin
```

 signage.py
```

## Verzeichnisstruktur

```
raspi-signage/
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── config.py            # Zentrale Konfiguration
│   ├── playlist.py          # Playlist-Verwaltung
│   ├── web/
│   │   ├── routes.py        # Admin-Routen (Upload, Toggle, etc.)
│   │   ├── auth.py          # Login/Logout System
│   │   ├── signage_server.py # Player-Server & Media-Serving
│   │   └── templates/       # Jinja2 Templates
│   └── player/              # Player-spezifische Module
├── data/                    # Playlist & User-Daten (nicht im Git)
│   ├── playlist.json        # Playlist-Einträge
│   └── users.json           # Benutzer mit Hashed Passwords
├── media/                   # Hochgeladene Medien (nicht im Git)
│   ├── images/              # Bilder & Video-Thumbnails
│   └── videos/              # Videos
├── log/                     # Log-Dateien
├── systemd/                 # Systemd Unit-Files
├── signage.py               # Haupt-Entrypoint (mit Browser-Öffnung)
├── run_web.py               # Web-Server Entrypoint
└── requirements.txt         # Python Dependencies


## Benutzerverwaltung

Beim ersten Start (ohne `data/users.json`) sind alle Admin-Routen **ohne Login** zugänglich. Für Produktion solltest du einen Admin-User anlegen:

```bash
# User erstellen mit Hashed Password
python scripts/add_user.py
# Folge den Anweisungen: Username, Password, Role (admin)
```

Um das automatische Login-freie Verhalten zu deaktivieren, erstelle mindestens einen User. Ab dann ist Login erforderlich.

## Konfiguration

### Umgebungsvariablen

- `SIGNAGE_SECRET`: Secret Key für Flask Sessions (Production)
- `SIGNAGE_OPEN_BROWSER`: `0` = kein automatisches Browser-Öffnen, `1` = öffnen (Standard)
- `SIGNAGE_HEARTBEAT`: `1` = aktiviere Debug-Heartbeat-Logging (alle 5s)
- `SIGNAGE_IGNORE_SIGNALS`: `1` = ignoriere SIGINT/SIGTERM (nur Debug)

### Playlist-Format (`data/playlist.json`)

```json
[
  {
    "uuid": "unique-id",
    "media_type": "image",
    "file_name": "images/abc123.jpg",
    "enabled": true,
    "duration": 8,
    "poster": null
  },
  {
    "uuid": "unique-id-2",
    "media_type": "video",
    "file_name": "videos/xyz456.mp4",
    "enabled": true,
    "duration": null,
    "poster": "images/xyz456_thumb.jpg"
  }
]
```

- `duration`: Anzeigedauer in Sekunden (nur für Bilder; Videos spielen bis zum Ende)
- `poster`: Thumbnail-Pfad für Videos (automatisch via ffmpeg erstellt)

## Deployment (Raspberry Pi)

### Systemd Services

1. Passe die Unit-Files in `systemd/` an (WorkingDirectory, User):

```bash
# Beispiel: signage-web.service
[Service]
WorkingDirectory=/home/pi/raspi-signage
User=pi
ExecStart=/home/pi/raspi-signage/.venv/bin/python /home/pi/raspi-signage/run_web.py
```

2. Installiere und aktiviere Services:

```bash
sudo cp systemd/signage-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable signage-web.service
sudo systemctl start signage-web.service
```

3. Status prüfen:

```bash
sudo systemctl status signage-web.service
journalctl -u signage-web.service -f  # Live-Logs
```

### Kiosk-Mode (Auto-Start im Vollbild)

Für automatisches Öffnen des Players im Vollbild-Browser beim Boot:

```bash
# Chromium im Kiosk-Mode starten
chromium-browser --kiosk --noerrdialogs --disable-infobars --incognito http://localhost:8000/
```

Füge dies z.B. zu `~/.config/lxsession/LXDE-pi/autostart` oder erstelle einen systemd-Service.

## Entwicklung

### Debug-Logs aktivieren

```bash
export SIGNAGE_HEARTBEAT=1  # Aktiviert "alive"-Logs alle 5s
export SIGNAGE_IGNORE_SIGNALS=1  # Ignoriert SIGINT/SIGTERM
python signage.py
```

### Playlist normalisieren

Konvertiert absolute Pfade in `playlist.json` zu relativen Pfaden:

```bash
python scripts/normalize_playlist.py
```

## Tipps & Troubleshooting

### Player bleibt schwarz
- Öffne Browser-DevTools (F12) → Console-Tab: prüfe auf JavaScript-Fehler
- Network-Tab: prüfe, ob `/playlist.json` und `/media/...` Requests erfolgreich sind (Status 200)
- Überprüfe, dass `data/playlist.json` existiert und mindestens ein `enabled: true` Item enthält

### Videos werden nicht abgespielt
- `mpv` muss installiert sein: `which mpv`
- Überprüfe Video-Format: H.264 wird von den meisten Browsern unterstützt
- Logs prüfen: `tail -f log/$(ls -t log/ | head -1)`

### Uploads funktionieren nicht
- Prüfe Schreibrechte für `media/images` und `media/videos`
- Maximale Upload-Größe: Standard 1 GB (konfigurierbar in `app/__init__.py`)

### App beendet sich sofort beim Start
- Prüfe Logs: `tail -f log/$(ls -t log/ | head -1)`
- Deaktiviere Browser-Öffnung: `export SIGNAGE_OPEN_BROWSER=0`
- Debug-Modus: `export SIGNAGE_HEARTBEAT=1` und schaue, ob Heartbeats erscheinen

## Lizenz

Dieses Projekt ist für persönliche und kommerzielle Nutzung frei verfügbar.

## Kontakt & Beiträge

- Repository: [Henrik168/raspi-signage](https://github.com/Henrik168/raspi-signage)
- Issues & Pull Requests sind willkommen!
