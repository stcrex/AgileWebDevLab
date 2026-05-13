function updateCountdown() {
    const element = document.querySelector('[data-countdown]');
    if (!element) return;
    const target = new Date(element.dataset.countdown);
    const diff = Math.max(0, target - new Date());
    const totalMinutes = Math.floor(diff / 60000);
    const days = Math.floor(totalMinutes / (60 * 24));
    const hours = Math.floor((totalMinutes - days * 24 * 60) / 60);
    const minutes = totalMinutes % 60;
    element.querySelector('[data-days]').textContent = days;
    element.querySelector('[data-hours]').textContent = hours;
    element.querySelector('[data-minutes]').textContent = minutes;
}
updateCountdown();
setInterval(updateCountdown, 60000);

document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-action="topic-toggle"]');
    if (!button) return;
    const row = button.closest('[data-topic-id]');
    const id = row.dataset.topicId;
    const newStatus = button.classList.contains('checked') ? 'In Progress' : 'Done';
    const data = await postJson(`/api/topics/${id}/status`, { status: newStatus });
    button.classList.toggle('checked', data.status === 'Done');
    const pill = row.querySelector('.status-pill');
    pill.textContent = data.status;
    pill.className = `status-pill status-${data.status.toLowerCase().replaceAll(' ', '-')} ms-auto`;
});

const shareButton = document.getElementById('shareExamButton');
if (shareButton) {
    shareButton.addEventListener('click', async () => {
        try {
            const response = await fetch(`/api/exams/${shareButton.dataset.examId}/share`, { headers: { 'Accept': 'application/json' } });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Could not prepare share text.');
            await copyText(data.text, 'Exam summary copied to clipboard.');
        } catch (error) {
            showToast(error.message, 'danger');
        }
    });
}

function connectHandbookExamSelect(selectId, titleId) {
    const subjectSelect = document.getElementById(selectId);
    const titleInput = document.getElementById(titleId);
    if (!subjectSelect || !titleInput) return;
    subjectSelect.addEventListener('change', () => {
        const option = subjectSelect.options[subjectSelect.selectedIndex];
        if (!option || !option.value) return;
        const code = option.dataset.code || '';
        if (!titleInput.value.trim() || titleInput.dataset.autofilled === 'true') {
            titleInput.value = `${code} Exam`;
            titleInput.dataset.autofilled = 'true';
        }
    });
    titleInput.addEventListener('input', () => {
        titleInput.dataset.autofilled = 'false';
    });
}

connectHandbookExamSelect('standaloneExamSubject', 'standaloneExamTitle');
