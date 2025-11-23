## Zweck

Kurze, projekt-spezifische Hinweise für GitHub Copilot / AI-Agents, damit sie schnell und sicher im Code arbeiten können.

## Architektur-Überblick (Big Picture)

- Entrypoints:
  - `run_player.py` — Haupt-Player-Loop. Lädt `data/playlist.json`, überwacht Änderungszeitstempel und spielt Items sequenziell ab (Images via `pygame`, Videos via `mpv`).
  - `run_web.py` — Minimaler Flask-Webserver für Uploads und Aktiv/Deaktiv-Schalter der Playlist.
- Daten & Medien:
  - Playlist: `data/playlist.json` (JSON-Liste von Objekten mit `id`, `type`, `filename`, `enabled`, `duration`).
  - Medienordner: `media/images/` und `media/videos/`.
- Player-Implementierung:
  - `app/player/image_player.py` — initialisiert Display (`pygame`), skaliert Bilder auf Bildschirmgröße und zeigt sie für `duration` Sekunden.
  - `app/player/video_player.py` — ruft `mpv` per `subprocess.run` auf; setzt empfehlenswerte Flags (`--hwdec=auto`, `--fs`).

## Wichtige Dateien (Schnellreferenz)

- `run_player.py` — Orchestriert das Abspielen, prüft `mtime` von `data/playlist.json`.
- `run_web.py` — Flask App: Upload-Handler schreibt Dateien nach `media/*` und hängt Einträge an `data/playlist.json` via `app/playlist.py`.
- `app/playlist.py` — `load_playlist()` / `save_playlist()`; nutzt `Path('data/playlist.json')`.
- `app/player/image_player.py` — `init_display(fullscreen=True)` und `show_image(screen, path, duration)`.
- `app/player/video_player.py` — `play_video(path)` (Systemabhängige Abhängigkeit: `mpv`).
- `systemd/` — enthält `signage-player.service` und `signage-web.service` unit files für Deployment.

## Konkrete Hinweise für Änderungen & Erweiterungen

- Wenn du Medien hochlädst, nutze die vorhandenen Ordner (`media/images`, `media/videos`) — `run_web.py` setzt `filename` in Playlist auf `str(target)` (voller Pfad relativ zum Repo-Arbeitsverzeichnis).
- Änderungen an Playlist-Feldnamen: `run_player.py` filtert nach `item['type']` und nutzt `item.get('duration', 8)` für Bilder — ändere beide Stellen zusammen.
- Video-Wiedergabe wird via `mpv` gestartet; Hardware-Decoding-Flags sind in `video_player.py` gesetzt. Bei Problemen mit rpi/arm prüfe `mpv`-Build und Flags.

## Laufzeit- / Entwickler-Workflows

- Player lokal starten: Python-Interpreter in Repo-Root: `python run_player.py` (liefert Loop, hängt an `data/playlist.json`).
- Web-UI starten: `python run_web.py` (Flask liefert Upload/Toggle UI auf Port 8000 standardmäßig).
- Deployment: systemd unit files in `systemd/` zeigen how-to for background services.

## Abhängigkeiten & Systemanforderungen

- Python-Abhängigkeiten: `pygame`, `flask` (keine requirements.txt im Repo — installiere manuell in venv).
- System: `mpv` empfohlen/erforderlich für Videos; auf Embedded-Geräten ggf. hardware-decoding-optimiertes `mpv`.

### Raspberry Pi Hinweise

- SDL-Video-Treiber auf dem Pi können variieren (kmsdrm / fbcon / x11). Die Image-Player-Initialisierung probiert einige Treiber und fällt back zu einer best-effort Initialisierung.
- Stelle sicher, dass `mpv` systemweit installiert ist (`sudo apt install mpv`) — Videos werden per `mpv` gestartet.

## Konventionen & Patterns

- Pfade sind repository-relative (einfache Path-Objekte verwenden, z.B. `Path('data/playlist.json')`).
- Playlist-Einträge sind vollständige JSON-Objekte; Agenten sollten bestehende Einträge mit `app.playlist.load_playlist()`/`save_playlist()` bearbeiten.
- Fehlerbehandlung ist bewusst minimal: `run_player.py` fängt Exceptions, loggt und schläft 2s; vermeide invasive Änderungen ohne Tests.

## Beispiele (aus dem Repo)

- Playlist-Item (Beispiel aus `data/playlist.json`):

  {"id": "1", "type": "image", "filename": "media/images/urlaub1.jpg", "enabled": true, "duration": 8}

- Image-Flow: `run_web.py` speichert Upload → `media/images/<uuid>.<ext>` → `app.playlist.save_playlist()` hängt Eintrag an `data/playlist.json` → `run_player.py` lädt beim next mtime-change.

## Was AI-Agents vermeiden sollten

- Harte Annahmen über Bildschirmauflösung; nutze `screen.get_size()` wie `image_player.py`.
- Direktes Editieren der Playlist-JSON ohne `app.playlist`-APIs — verwende die helper-Funktionen.
- Ändern von systemd-Units ohne Tests auf Zielgerät.

## Fragen & Feedback

Wenn etwas unklar ist oder ein Abschnitt ergänzt werden soll (z. B. requirements.txt oder Test-Workflow), bitte Rückmeldung geben — ich passe die Anleitung an.
