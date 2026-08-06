const filenameFromDisposition = (value) => {
  const match = /filename="?([^";]+)"?/i.exec(value || "");
  return match ? match[1] : "converted-file";
};

document.querySelectorAll("form[data-endpoint]").forEach((form) => {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button");
    const status = form.querySelector(".status");
    button.disabled = true;
    status.textContent = "Processing locally…";
    try {
      const response = await fetch(form.dataset.endpoint, { method: "POST", body: new FormData(form) });
      if (!response.ok) {
        let message = `Conversion failed (${response.status})`;
        try { message = (await response.json()).detail || message; } catch (_) {}
        throw new Error(message);
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = filenameFromDisposition(response.headers.get("content-disposition"));
      link.click();
      URL.revokeObjectURL(url);
      status.textContent = "Done — temporary server files deleted.";
    } catch (error) {
      status.textContent = error.message;
    } finally {
      button.disabled = false;
    }
  });
});
fetch("/api/capabilities").then(r => r.json()).then(data => {
  document.getElementById("limit").textContent = `${data.max_upload_mb} MB`;
});
