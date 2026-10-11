const themeToggle = document.querySelector("[data-theme-toggle]");

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const isDark = document.body.classList.toggle("theme-dark");
        themeToggle.setAttribute("aria-pressed", String(isDark));
        themeToggle.textContent = isDark ? "Светлая тема" : "Тёмная тема";
    });
}
