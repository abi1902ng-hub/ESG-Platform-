(function () {
  function animateStats() {
    const stats = document.querySelectorAll(".stat-value[data-target]");
    stats.forEach(function (el) {
      const target = parseInt(el.getAttribute("data-target"), 10);
      const duration = 1200;
      const start = performance.now();

      function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(eased * target);
        if (progress < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const heroStats = document.getElementById("heroStats");
    if (!heroStats) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      heroStats.querySelectorAll("[data-target]").forEach(function (el) {
        el.textContent = el.getAttribute("data-target");
      });
      return;
    }

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateStats();
            observer.disconnect();
          }
        });
      },
      { threshold: 0.4 }
    );
    observer.observe(heroStats);
  });
})();
