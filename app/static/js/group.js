document.querySelectorAll('.task-status').forEach(select => {
    select.addEventListener('change', async () => {
        const row = select.closest('[data-task-id]');
        try {
            await postJson(`/api/group/tasks/${row.dataset.taskId}/status`, { status: select.value });
            showToast(`Task updated to ${select.value}.`, 'success');
        } catch (error) {
            showToast(error.message, 'danger');
        }
    });
});

document.querySelectorAll('.book-slot').forEach(button => {
    button.addEventListener('click', async () => {
        const slotRow = button.closest('[data-slot-label]');
        const label = slotRow?.dataset.slotLabel || 'selected slot';
        const original = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Booking';

        try {
            const data = await postJson('/api/group/study-session', {
                title: `Group Study Session — ${label}`,
                starts_at: button.dataset.start,
                ends_at: button.dataset.end,
                location: 'UWA Library / Online'
            });
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-success');
            button.innerHTML = '<i class="bi bi-check2-circle"></i> Booked';
            showToast(data.message, 'success');
        } catch (error) {
            button.disabled = false;
            button.innerHTML = original;
            showToast(error.message, 'danger');
        }
    });
});

const inviteForm = document.getElementById('inviteForm');
const inviteEmail = document.getElementById('inviteEmail');
const inviteResult = document.getElementById('inviteResult');
const copyGroupCode = document.getElementById('copyGroupCode');

if (inviteForm) {
    inviteForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        try {
            const data = await postJson('/api/group/invite', { email: inviteEmail.value.trim() });
            inviteResult.textContent = data.invite_text;
            showToast(data.message, 'success');
            await copyText(data.invite_text, 'Invite text copied.');
        } catch (error) {
            inviteResult.textContent = error.message;
            showToast(error.message, 'danger');
        }
    });
}

if (copyGroupCode) {
    copyGroupCode.addEventListener('click', () => {
        const text = document.getElementById('groupCodeText')?.textContent || '';
        copyText(text, 'Group code copied.');
    });
}
