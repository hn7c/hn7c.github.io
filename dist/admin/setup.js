/* A working setup screen until the owner connects their own Turbo site. */
(async function () {
  const panel = document.getElementById("editor-setup");
  const status = document.getElementById("editor-status");
  const help = document.getElementById("connection-help");

  function showError(message) {
    panel.hidden = false;
    status.textContent = message;
    help.hidden = false;
  }

  try {
    const response = await fetch("./config.yml", { cache: "no-store" });
    if (!response.ok) throw new Error("The editor configuration could not be loaded. Check that admin/config.yml was deployed.");
    const configuration = await response.text();
    const siteId = configuration.match(/^\s*turbo_site_id:\s*["']?([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})["']?\s*(?:#.*)?$/im);
    if (!siteId) {
      showError("The editor files are installed. Your Decap Turbo connection still needs to be configured.");
      return;
    }

    window.CMS_MANUAL_INIT = true;
    status.textContent = "Loading Decap CMS…";
    const script = document.createElement("script");
    // This stable version includes the Turbo backend. Upgrade deliberately.
    script.src = "https://cdn.jsdelivr.net/npm/decap-cms@3.17.0/dist/decap-cms.js";
    script.onerror = () => showError("Decap CMS could not be downloaded. Check your connection or content blocker, then reload.");
    script.onload = async () => {
      try {
        if (typeof window.initCMS !== "function") throw new Error("Decap CMS did not load correctly. Please reload.");
        panel.hidden = true;
        await window.initCMS();
      } catch (error) {
        showError(error.message || "The editor could not start. Check your Turbo settings and reload.");
      }
    };
    document.head.appendChild(script);
  } catch (error) {
    showError(error.message || "The editor could not read its configuration.");
  }
}());
