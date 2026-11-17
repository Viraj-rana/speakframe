const $ = (id) => document.getElementById(id);

async function loadHealth() {
  const res = await fetch("/api/health");
  const data = await res.json();
  $("device").textContent = `Device: ${data.device}`;
}

async function loadLatest() {
  const res = await fetch("/api/preview/latest");
  const data = await res.json();
  if (data.ready && data.url) {
    $("player").src = data.url;
    $("caption").textContent = "Showing the latest saved result.";
  }
}

async function pollJob(jobId) {
  const bar = $("bar");
  bar.hidden = false;
  let ticks = 5;
  const timer = setInterval(async () => {
    ticks = Math.min(95, ticks + 4);
    bar.value = ticks;
    const res = await fetch(`/api/jobs/${jobId}`);
    const job = await res.json();
    $("status").textContent = `${job.stage}: ${job.message}`;
    if (job.status === "done" && job.result_url) {
      clearInterval(timer);
      bar.value = 100;
      $("player").src = job.result_url;
      $("run").disabled = false;
      $("caption").textContent = "Analysis complete.";
    } else if (job.status === "error") {
      clearInterval(timer);
      bar.hidden = true;
      $("run").disabled = false;
    }
  }, 2500);
}

$("run").addEventListener("click", async () => {
  const file = $("file").files[0];
  if (!file) {
    $("status").textContent = "Please choose a video file.";
    return;
  }
  $("run").disabled = true;
  $("status").textContent = "Uploading…";
  const fd = new FormData();
  fd.append("file", file);
  const duration = $("duration").value || "10";
  const res = await fetch(`/api/analyze?duration=${duration}`, {
    method: "POST",
    body: fd,
  });
  const data = await res.json();
  $("status").textContent = `Job ${data.job_id} started (${data.duration}s).`;
  pollJob(data.job_id);
});

loadHealth();
loadLatest();