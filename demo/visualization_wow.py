"""Neon-style active speaker overlays for demo videos (BGR OpenCV)."""
import cv2
import numpy as np


def _draw_glow_rect(
    image: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    speaking: bool,
    pulse: float,
) -> None:
    if speaking:
        outer = (int(40 * pulse), int(220 * pulse), int(120 * pulse))
        mid = (int(80 * pulse), int(255 * pulse), int(200 * pulse))
        inner = (0, 255, 0)
        for color, thickness, pad in ((outer, 14, 18), (mid, 8, 10), (inner, 3, 0)):
            cv2.rectangle(
                image,
                (x1 - pad, y1 - pad),
                (x2 + pad, y2 + pad),
                color,
                thickness,
                lineType=cv2.LINE_AA,
            )
    else:
        cv2.rectangle(image, (x1, y1), (x2, y2), (80, 80, 255), 4, lineType=cv2.LINE_AA)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 2, lineType=cv2.LINE_AA)


def draw_face_overlay(image: np.ndarray, face: dict, frame_idx: int) -> None:
    score = float(face["score"])
    speaking = score >= 0.0
    pulse = 0.75 + 0.25 * np.sin(frame_idx * 0.35 + face.get("track", 0))

    x, y, s = int(face["x"]), int(face["y"]), int(face["s"])
    x1, y1, x2, y2 = x - s, y - s, x + s, y + s
    _draw_glow_rect(image, x1, y1, x2, y2, speaking, pulse)

    label = "SPEAKING" if speaking else "LISTENING"
    tag = f"#{face.get('track', 0)} {label}  {score:+.1f}"
    ty = max(y1 - 12, 28)
    accent = (0, 255, 150) if speaking else (120, 120, 255)

    (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
    cv2.rectangle(
        image,
        (x1, ty - th - 10),
        (x1 + tw + 14, ty + 6),
        (20, 24, 32),
        -1,
    )
    cv2.putText(
        image,
        tag,
        (x1 + 7, ty),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        accent,
        2,
        cv2.LINE_AA,
    )


def draw_hud_banner(image: np.ndarray, num_faces: int) -> None:
    h, w = image.shape[:2]
    cv2.rectangle(image, (0, 0), (w, 42), (16, 18, 24), -1)
    title = "SpeakFrame  |  Active Speaker Detection"
    cv2.putText(
        image,
        title,
        (16, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 220, 100),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        image,
        f"tracks: {num_faces}",
        (w - 180, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (180, 255, 220),
        1,
        cv2.LINE_AA,
    )