(() => {
    const THEME_KEY = "theme";
    const toggle = document.getElementById("theme-toggle");

    const getTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme === "dark" || savedTheme === "light") {
            return savedTheme;
        }

        return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    };

    const setTheme = (theme) => {
        document.documentElement.setAttribute("data-bs-theme", theme);
        localStorage.setItem(THEME_KEY, theme);
        if (toggle) {
            toggle.checked = theme === "dark";
        }
    };

    setTheme(getTheme());

    if (!toggle) {
        return;
    }

    toggle.addEventListener("change", (event) => {
        setTheme(event.target.checked ? "dark" : "light");
    });
})();
