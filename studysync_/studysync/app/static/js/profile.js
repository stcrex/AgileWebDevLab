const ajaxSaveButton = document.getElementById('ajax-save-profile');
const profileStatus = document.getElementById('profile-save-status');

function profileValue(id) {
    return document.getElementById(id)?.value || '';
}

function setProfileStatus(message, isError = false) {
    if (!profileStatus) return;
    profileStatus.textContent = message;
    profileStatus.classList.toggle('text-danger', isError);
    profileStatus.classList.toggle('text-success', !isError && Boolean(message));
}

ajaxSaveButton?.addEventListener('click', async () => {
    setProfileStatus('Saving...');
    const payload = {
        name: profileValue('profile-name'),
        uwa_id: profileValue('profile-uwa-id'),
        program: profileValue('profile-program'),
        year_level: profileValue('profile-year-level'),
        bio: profileValue('profile-bio'),
        skills: profileValue('profile-skills'),
        study_goal: profileValue('profile-study-goal'),
        availability: profileValue('profile-availability'),
        preferred_contact: profileValue('profile-preferred-contact'),
        avatar_color: profileValue('profile-avatar-color'),
        show_email: document.getElementById('profile-show-email')?.checked || false
    };

    try {
        const result = await postJson('/api/profile', payload);
        setProfileStatus('Saved with AJAX ✓');
        document.querySelectorAll('.sidebar-user strong').forEach((element) => {
            element.textContent = result.profile.name;
        });
        setTimeout(() => setProfileStatus(''), 3000);
    } catch (error) {
        setProfileStatus('Could not save profile. Check required fields.', true);
    }
});
