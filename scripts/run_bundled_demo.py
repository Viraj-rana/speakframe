"""Download a short sample, run SpeakFrame pipeline, register result for demo_server preview."""
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
SAMPLE = DEMO / "sample.mp4"
URL = "https://download.samplelib.com/mp4/sample-5s.mp4"


def main() -> int:
    DEMO.mkdir(exist_ok=True)
    if not SAMPLE.is_file() or SAMPLE.stat().st_size < 100_000:
        print("Downloading sample clip…")
        urllib.request.urlretrieve(URL, SAMPLE)

    cmd = [
        sys.executable,
        str(ROOT / "Columbia_test.py"),
        "--videoName",
        "sample",
        "--videoFolder",
        str(DEMO),
        "--pretrainModel",
        str(ROOT / "weight" / "finetuning_TalkSet.model"),
        "--duration",
        "8",
    ]
    print("Running:", " ".join(cmd))
    code = subprocess.call(cmd, cwd=str(ROOT))
    if code != 0:
        return code

    out_mp4 = DEMO / "sample" / "pyavi" / "video_out.mp4"
    if not out_mp4.is_file():
        out_mp4 = DEMO / "sample" / "pyavi" / "video_out.avi"
    if not out_mp4.is_file():
        print("No output video found.")
        return 1

    sys.path.insert(0, str(ROOT))
    from demo_server import register_completed_run

    job_id = "sample"
    register_completed_run(job_id, out_mp4)
    print(f"Registered preview job '{job_id}' → {out_mp4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())