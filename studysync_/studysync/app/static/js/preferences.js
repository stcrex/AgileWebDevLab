const setDarkTheme = document.getElementById('setDarkTheme');
const setCompactMode = document.getElementById('setCompactMode');
const resetThemeMode = document.getElementById('resetThemeMode');
const themePreviewBox = document.getElementById('themePreviewBox');

function applyPreferenceMode(mode) {
    document.body.classList.toggle('compact-mode', mode === 'compact');
    if (themePreviewBox) {
        themePreviewBox.dataset.mode = mode;
    }
    localStorage.setItem('studysync-preference-mode', mode);
}

if (setDarkTheme) {
    setDarkTheme.addEventListener('click', () => {
        applyPreferenceMode('dark');
        showToast('Dark dashboard mode enabled.', 'success');
    });
}

if (setCompactMode) {
    setCompactMode.addEventListener('click', () => {
        applyPreferenceMode('compact');
        showToast('Compact card spacing enabled for this browser.', 'success');
    });
}

if (resetThemeMode) {
    resetThemeMode.addEventListener('click', () => {
        applyPreferenceMode('dark');
        localStorage.removeItem('studysync-preference-mode');
        showToast('Layout reset.', 'success');
    });
}

applyPreferenceMode(localStorage.getItem('studysync-preference-mode') || 'dark');
