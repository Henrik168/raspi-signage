# Rapsi Signage — Raspberry Pi digital signage

Kurze Anleitung, um dieses kleine Signage-Projekt auf einem Raspberry Pi zu betreiben.

1) Systemabhängigkeiten (Raspbian / Debian):

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip mpv libsdl2-2.0-0
```

1.1) Entwicklungsumgebung
python -m pip install flask
python -m pip install PySide6 PySide6-QtAds-stubs python-vlc flask

2) Python-Umgebung:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3) Player starten:

```bash
python run_player.py
```

4) Web UI starten (Upload / toggle):

```bash
python run_web.py
# öffnet auf Port 8000 (0.0.0.0:8000)
```

5) systemd (optional):

Die Unit-Files in `systemd/` sind Beispiele. Passe `WorkingDirectory` an (z.B. `/home/pi/rapsi-signage`) und kopiere die Dateien nach `/etc/systemd/system/`.

sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable signage.service
sudo systemctl enable kiosk.service
sudo systemctl start signage.service
sudo systemctl start kiosk.service


6) Hinweise
- `mpv` ist erforderlich für Video-Wiedergabe.
- SDL-Video-Treiber auf dem Pi können variieren (kmsdrm/fbcon). Das Image-Player-Modul probiert einige Optionen.
