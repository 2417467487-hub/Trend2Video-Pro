(function () {
  const allowedHosts = ["github.com", "www.producthunt.com", "news.ycombinator.com"];
  if (!allowedHosts.includes(window.location.hostname)) return;
  if (document.getElementById("trend2video-generate-button")) return;

  const button = document.createElement("button");
  button.id = "trend2video-generate-button";
  button.textContent = "Generate Video";
  button.style.cssText = [
    "position:fixed",
    "right:18px",
    "bottom:18px",
    "z-index:2147483647",
    "border:0",
    "border-radius:10px",
    "padding:12px 16px",
    "font:600 14px system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif",
    "color:#ffffff",
    "background:#0891b2",
    "box-shadow:0 10px 28px rgba(8,145,178,.35)",
    "cursor:pointer"
  ].join(";");

  async function sendToTrend2Video() {
    const originalText = button.textContent;
    button.textContent = "Sending...";
    button.disabled = true;
    try {
      const response = await fetch("http://127.0.0.1:8000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: document.title.replace(/\s+/g, " ").trim(),
          url: window.location.href,
          platform: "Bilibili",
          style: "Tech News",
          duration: 60
        })
      });
      if (!response.ok) throw new Error(`Local API returned ${response.status}`);
      button.textContent = "Package started";
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
      }, 3500);
    } catch (error) {
      button.textContent = "API offline";
      console.warn("[Trend2Video Pro]", error);
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
      }, 3500);
    }
  }

  button.addEventListener("click", sendToTrend2Video);
  document.documentElement.appendChild(button);
})();
