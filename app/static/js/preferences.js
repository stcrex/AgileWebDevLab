const setLightTheme = document.getElementById('setLightTheme');
const setDarkTheme = document.getElementById('setDarkTheme');
const setCompactMode = document.getElementById('setCompactMode');
const resetThemeMode = document.getElementById('resetThemeMode');
const themePreviewBox = document.getElementById('themePreviewBox');

function updateButtonState(mode) {
    [setLightTheme, setDarkTheme, setCompactMode, resetThemeMode].forEach((button) => {
        button?.classList.remove('btn-primary');
        button?.classList.add('btn-outline-light');
    });

    const activeButton =
        mode === 'light' ? setLightTheme :
        mode === 'dark' ? setDarkTheme :
        mode === 'compact' ? setCompactMode :
        resetThemeMode;

    activeButton?.classList.remove('btn-outline-light');
    activeButton?.classList.add('btn-primary');
}

function applyPreferenceMode(mode) {
    document.body.classList.remove('compact-mode', 'preview-dark-mode', 'preview-light-mode');

    if (mode === 'compact') {
        document.body.classList.add('compact-mode');
    }

    if (mode === 'dark') {
        document.body.classList.add('preview-dark-mode');
    }

    if (mode === 'light') {
        document.body.classList.add('preview-light-mode');
    }

    if (themePreviewBox) {
        themePreviewBox.dataset.mode = mode;
    }

    if (mode === 'default') {
        localStorage.removeItem('studysync-preference-mode');
    } else {
        localStorage.setItem('studysync-preference-mode', mode);
    }

    updateButtonState(mode);
}

if (setLightTheme) {
    setLightTheme.addEventListener('click', () => {
        applyPreferenceMode('light');
        if (typeof showToast === 'function') {
            showToast('Light dashboard preview enabled.', 'success');
        }
    });
}

if (setDarkTheme) {
    setDarkTheme.addEventListener('click', () => {
        applyPreferenceMode('dark');
        if (typeof showToast === 'function') {
            showToast('Dark dashboard preview enabled.', 'success');
        }
    });
}

if (setCompactMode) {
    setCompactMode.addEventListener('click', () => {
        applyPreferenceMode('compact');
        if (typeof showToast === 'function') {
            showToast('Compact card spacing enabled for this browser.', 'success');
        }
    });
}

if (resetThemeMode) {
    resetThemeMode.addEventListener('click', () => {
        applyPreferenceMode('default');
        if (typeof showToast === 'function') {
            showToast('Layout reset.', 'success');
        }
    });
}

applyPreferenceMode(localStorage.getItem('studysync-preference-mode') || 'default');
