"""Produce a short preview MP4 with wow overlays when ASD pipeline has no faces."""
import glob
import os
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from demo.visualization_wow import draw_face_overlay, draw_hud_banner

DEMO = ROOT / "demo" / "sample"
FRAMES = DEMO / "pyframes"
OUT = DEMO / "pyavi"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    flist = sorted(glob.glob(str(FRAMES / "*.jpg")))
    if not flist:
        print("No frames — run Columbia_test extract step first or place pyframes.")
        return 1

    first = cv2.imread(flist[0])
    h, w = first.shape[:2]
    vw = cv2.VideoWriter(str(OUT / "video_only.avi"), cv2.VideoWriter_fourcc(*"XVID"), 25, (w, h))

    mock = {"track": 0, "score": 0.8, "s": min(w, h) // 8, "x": w // 2, "y": h // 2}
    for fidx, fp in enumerate(flist):
        img = cv2.imread(fp)
        mock["score"] = 0.6 if (fidx // 25) % 2 else -0.4
        draw_hud_banner(img, 1)
        draw_face_overlay(img, mock, fidx)
        vw.write(img)
    vw.release()

    audio = OUT / "audio.wav"
    if not audio.is_file():
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=mono",
                "-t",
                str(len(flist) / 25),
                str(audio),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    mp4 = OUT / "video_out.mp4"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(OUT / "video_only.avi"),
            "-i",
            str(audio),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            str(mp4),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("Wrote", mp4)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())