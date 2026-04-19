(() => {
  const root = document.querySelector(".auth-page");
  if (!root) return;

  const params = new URLSearchParams(window.location.search);
  const error = params.get("error");
  if (!error) return;

  const alertEl =
    document.querySelector("#auth-alert") || document.querySelector(".auth-alert");
  if (!alertEl) return;

  alertEl.textContent = error;
  alertEl.hidden = false;

  // Optional: remove error from URL after showing it
  try {
    params.delete("error");
    const newQuery = params.toString();
    const newUrl =
      window.location.pathname +
      (newQuery ? `?${newQuery}` : "") +
      window.location.hash;
    window.history.replaceState({}, "", newUrl);
  } catch {
    // ignore
  }
})();

