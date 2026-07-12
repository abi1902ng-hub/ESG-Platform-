(function () {
  const root = document.documentElement;
  const stored = localStorage.getItem("ecosphere-theme");
  if (stored) root.setAttribute("data-bs-theme", stored);

  function updateIcon() {
    const icon = document.getElementById("themeIcon");
    if (!icon) return;
    const isDark = root.getAttribute("data-bs-theme") === "dark";
    icon.className = isDark ? "bi bi-sun" : "bi bi-moon-stars";
  }

  document.addEventListener("DOMContentLoaded", function () {
    updateIcon();

    const themeToggle = document.getElementById("themeToggle");
    if (themeToggle) {
      themeToggle.addEventListener("click", function () {
        const current = root.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
        root.setAttribute("data-bs-theme", current);
        localStorage.setItem("ecosphere-theme", current);
        updateIcon();
      });
    }

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("appSidebar");
    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("open");
      });
    }
  });
})();
