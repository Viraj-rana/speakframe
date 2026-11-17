# SpeakFrame

Web app for active speaker detection (overlays + browser preview).

## Setup

```powershell
cd Light-ASD-main
pip install -r requirements.txt
# FFmpeg must be on PATH (winget install Gyan.FFmpeg)
```

Face detector weights download automatically on first run (`sfd_face.pth`).

## Run sample analysis (CLI)

```powershell
# Place or download demo\sample.mp4, then:
python Columbia_test.py --videoName sample --videoFolder demo --pretrainModel weight/finetuning_TalkSet.model --duration 10
```

Output: `demo/sample/pyavi/video_out.mp4` (wow HUD + glow) and `video_out.avi`.

## Web preview

```powershell
python scripts/run_bundled_demo.py   # optional: sample run + register job
python -m uvicorn demo_server:app --host 127.0.0.1 --port 8765
```

Open **http://127.0.0.1:8765/** — upload a short clip or watch the latest bundled result.

**CPU note:** face detection is slow without CUDA; use `--duration 5`–`15` for demos.