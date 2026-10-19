#!/usr/bin/env python3
"""Genera MP3 de prueba con frame GEOB 'Serato BeatGrid' (solo lectura en app).

Uso: gen_tagged_mp3.py salida.mp3
Crea 8 s de tono 440 Hz a 128 kbps (ffmpeg) y antepone un tag ID3v2.3 con un
payload BeatGrid v1 conocido: markers cada 0.5 s (btn=1), terminal 2.0 s @120.
"""
import struct
import subprocess
import sys


def payload() -> bytes:
    body = b"".join(
        struct.pack(">fI", t, 1) for t in (0.0, 0.5, 1.0, 1.5)
    )
    body += struct.pack(">ff", 2.0, 120.0)
    return b"\x01\x00" + struct.pack(">I", 5) + body


def geob_frame(obj: bytes) -> bytes:
    content = (
        b"\x00" + b"application/octet-stream\x00" + b"\x00"
        + b"Serato BeatGrid\x00" + obj
    )
    return b"GEOB" + struct.pack(">I", len(content)) + b"\x00\x00" + content


def main() -> None:
    out = sys.argv[1]
    tmp = out + ".raw.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "sine=frequency=440:duration=60", "-codec:a", "libmp3lame",
         "-b:a", "128k", tmp],
        check=True,
    )
    with open(tmp, "rb") as f:
        audio = f.read()
    # Quitar tag ID3 previo de ffmpeg si existe (empezar limpio).
    if audio[:3] == b"ID3":
        size = 0
        for b in audio[6:10]:
            size = (size << 7) | (b & 0x7F)
        audio = audio[10 + size :]
    frame = geob_frame(payload())
    size = len(frame)
    sync = bytes([(size >> 21) & 127, (size >> 14) & 127,
                  (size >> 7) & 127, size & 127])
    tag = b"ID3\x03\x00\x00" + sync + frame
    with open(out, "wb") as f:
        f.write(tag + audio)
    print("escrito", out, "payload markers=4+terminal bpm=120")


if __name__ == "__main__":
    main()
