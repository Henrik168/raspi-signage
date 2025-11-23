from pathlib import Path
import subprocess


def create_thumbnail_ffmpeg(
    video_path: Path,
    output_path: Path,
    t: float = 1.0,     # Zeitpunkt in Sekunden
    width: int | None = 320
):

    cmd = [
        "ffmpeg",
        "-y",                   # überschreiben ohne nachzufragen
        "-ss", str(t),          # zu Zeitpunkt springen
        "-i", str(video_path),  # Input-Video
        "-vframes", "1",        # nur 1 Frame
    ]

    if width is not None:
        # Höhe wird automatisch angepasst, Seitenverhältnis bleibt
        cmd += ["-vf", f"scale={width}:-1"]

    cmd.append(str(output_path))

    subprocess.run(cmd, check=True)
