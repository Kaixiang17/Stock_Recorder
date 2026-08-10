class I18nEngine {
    constructor() {
        this.currentLang = localStorage.getItem("app_lang") || "zh-TW";
        this.translations = {};
        this.init();
    }

    async init() {
        await this.loadLanguage(this.currentLang);
        this.bindEvents();
    }

    async loadLanguage(lang) {
        try {
            const response = await fetch(`./${lang}.json`);
            if (!response.ok) throw new Error(`Could not load ${lang}.json`);
            this.translations = await response.json();
            this.currentLang = lang;
            localStorage.setItem("app_lang", lang);
            this.updateDOM();
        } catch (error) {
            console.error("i18n Error:", error);
        }
    }

    updateDOM() {
        // Update data-i18n elements
        document.querySelectorAll("[data-i18n]").forEach(el => {
            const key = el.getAttribute("data-i18n");
            const val = this.getNestedValue(this.translations, key);
            if (val) el.innerText = val;
        });

        // Update Language Switcher label
        const langLabel = document.getElementById("current-lang");
        if (langLabel) {
            langLabel.innerText = this.currentLang === "zh-TW" ? "繁中" : "EN";
        }

        // Update HTML lang attribute
        document.documentElement.lang = this.currentLang;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((prev, curr) => prev && prev[curr], obj);
    }

    bindEvents() {
        const toggleBtn = document.getElementById("lang-toggle");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => {
                const newLang = this.currentLang === "zh-TW" ? "en" : "zh-TW";
                this.loadLanguage(newLang);
            });
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.i18n = new I18nEngine();
});
