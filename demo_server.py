"""
SpeakFrame demo: upload a clip, run Columbia_test pipeline, preview in browser.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
DEMO_DIR = ROOT / "demo"
RUNS_DIR = ROOT / "demo_runs"
WEB_DIR = DEMO_DIR / "web"

app = FastAPI(title="SpeakFrame")
JOBS: dict[str, dict] = {}
LATEST_RESULT: dict[str, str] = {"mp4": "", "job_id": ""}

RUNS_DIR.mkdir(parents=True, exist_ok=True)
(DEMO_DIR / "uploads").mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


def _run_pipeline(job_id: str, video_path: Path, duration: int) -> None:
    job = JOBS[job_id]
    stem = video_path.stem
    work_name = f"job_{job_id}_{stem}"
    upload_copy = DEMO_DIR / "uploads" / f"{work_name}.mp4"
    shutil.copy2(video_path, upload_copy)

    cmd = [
        sys.executable,
        str(ROOT / "Columbia_test.py"),
        "--videoName",
        work_name,
        "--videoFolder",
        str(DEMO_DIR / "uploads"),
        "--pretrainModel",
        str(ROOT / "weight" / "finetuning_TalkSet.model"),
        "--duration",
        str(duration),
    ]
    job["status"] = "running"
    job["stage"] = "pipeline"
    job["message"] = "Extracting video, detecting faces, running SpeakFrame…"

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if proc.returncode != 0:
            job["status"] = "error"
            tail = (proc.stderr or proc.stdout or "")[-2000:]
            job["message"] = f"Pipeline failed.\n{tail}"
            return

        out_mp4 = DEMO_DIR / "uploads" / work_name / "pyavi" / "video_out.mp4"
        if not out_mp4.is_file():
            out_avi = DEMO_DIR / "uploads" / work_name / "pyavi" / "video_out.avi"
            if not out_avi.is_file():
                job["status"] = "error"
                job["message"] = "No output video produced."
                return
            out_mp4 = out_avi

        dest = RUNS_DIR / f"{job_id}.mp4"
        shutil.copy2(out_mp4, dest)
        job["status"] = "done"
        job["stage"] = "complete"
        job["message"] = "Analysis complete."
        job["result_url"] = f"/api/result/{job_id}"
        LATEST_RESULT["mp4"] = str(dest)
        LATEST_RESULT["job_id"] = job_id
    except Exception as exc:  # BLE001
        job["status"] = "error"
        job["message"] = str(exc)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health() -> JSONResponse:
    import torch

    return JSONResponse(
        {
            "ok": True,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "latest_job": LATEST_RESULT.get("job_id") or None,
        }
    )


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    duration: int = 12,
) -> JSONResponse:
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    duration = max(3, min(duration, 60))
    job_id = uuid.uuid4().hex[:12]
    upload_path = RUNS_DIR / f"{job_id}_in.mp4"
    content = await file.read()
    upload_path.write_bytes(content)

    JOBS[job_id] = {
        "status": "queued",
        "stage": "queued",
        "message": "Queued…",
        "result_url": None,
    }
    threading.Thread(
        target=_run_pipeline,
        args=(job_id, upload_path, duration),
        daemon=True,
    ).start()
    return JSONResponse({"job_id": job_id, "duration": duration})


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str) -> JSONResponse:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Unknown job")
    return JSONResponse(job)


@app.get("/api/result/{job_id}")
def result(job_id: str) -> FileResponse:
    path = RUNS_DIR / f"{job_id}.mp4"
    if not path.is_file():
        raise HTTPException(404, "Result not ready")
    return FileResponse(path, media_type="video/mp4", filename=f"speakframe-{job_id}.mp4")


@app.get("/api/preview/latest")
def preview_latest() -> JSONResponse:
    meta = RUNS_DIR / "latest.json"
    if meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        job_id = data.get("job_id", "sample")
        path = Path(data.get("path", ""))
        if path.is_file():
            return JSONResponse(
                {"ready": True, "job_id": job_id, "url": f"/api/result/{job_id}"}
            )

    p = LATEST_RESULT.get("mp4") or ""
    if p and Path(p).is_file():
        job_id = LATEST_RESULT.get("job_id") or "sample"
        return JSONResponse(
            {"ready": True, "job_id": job_id, "url": f"/api/result/{job_id}"}
        )

    fallback = ROOT / "demo" / "sample" / "pyavi" / "video_out.mp4"
    if fallback.is_file():
        return JSONResponse(
            {"ready": True, "job_id": "sample", "url": "/api/result/sample"}
        )
    return JSONResponse({"ready": False})


def register_completed_run(job_id: str, mp4_path: Path) -> None:
    """Call after a manual Columbia_test run to expose preview."""
    dest = RUNS_DIR / f"{job_id}.mp4"
    shutil.copy2(mp4_path, dest)
    LATEST_RESULT["mp4"] = str(dest)
    LATEST_RESULT["job_id"] = job_id
    JOBS[job_id] = {
        "status": "done",
        "stage": "complete",
        "message": "Bundled sample run.",
        "result_url": f"/api/result/{job_id}",
    }
    meta = RUNS_DIR / "latest.json"
    meta.write_text(
        json.dumps({"job_id": job_id, "path": str(dest)}, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("demo_server:app", host="127.0.0.1", port=8765, reload=False)
