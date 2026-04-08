(() => {
    const THEME_KEY = "theme";
    const toggle = document.getElementById("theme-toggle");
    const systemThemeQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const getTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        if (savedTheme === "dark" || savedTheme === "light") {
            return savedTheme;
        }

        return systemThemeQuery.matches ? "dark" : "light";
    };

    const setTheme = (theme, persist = true) => {
        document.documentElement.setAttribute("data-bs-theme", theme);
        if (persist) {
            localStorage.setItem(THEME_KEY, theme);
        }
        if (toggle) {
            toggle.checked = theme === "dark";
        }
    };

    const hasSavedTheme = () => {
        const savedTheme = localStorage.getItem(THEME_KEY);
        return savedTheme === "dark" || savedTheme === "light";
    };

    setTheme(getTheme(), hasSavedTheme());

    systemThemeQuery.addEventListener("change", (event) => {
        if (hasSavedTheme()) {
            return;
        }

        setTheme(event.matches ? "dark" : "light", false);
    });

    if (!toggle) {
        return;
    }

    toggle.addEventListener("change", (event) => {
        setTheme(event.target.checked ? "dark" : "light");
    });
})();
