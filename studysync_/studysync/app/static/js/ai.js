const form = document.getElementById('chatForm');
const input = document.getElementById('chatText');
const messages = document.getElementById('chatMessages');
const clearButton = document.getElementById('clearAiHistory');
const historyButton = document.getElementById('showAiHistory');
const historyList = document.getElementById('aiHistoryList');

function addMessage(role, text) {
    const row = document.createElement('div');
    row.className = `chat-row ${role}`;
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    const pre = document.createElement('pre');
    pre.textContent = text;
    bubble.appendChild(pre);
    row.appendChild(bubble);
    messages.insertBefore(row, messages.querySelector('.suggestion-chips'));
    messages.scrollTop = messages.scrollHeight;
    return pre;
}

async function sendMessage(text) {
    addMessage('user', text);
    input.value = '';
    const pending = addMessage('assistant', 'Thinking through your timetable and weak topics...');
    try {
        const data = await postJson('/api/ai/message', { message: text });
        pending.textContent = data.reply;
    } catch (error) {
        pending.textContent = 'Sorry, I could not generate a plan right now. Check the server console.';
        showToast(error.message, 'danger');
    }
}

function clearChatRows() {
    messages.querySelectorAll('.chat-row').forEach(row => row.remove());
}

if (form) {
    form.addEventListener('submit', (event) => {
        event.preventDefault();
        const text = input.value.trim();
        if (text) sendMessage(text);
    });
}

document.querySelectorAll('[data-suggest]').forEach(button => {
    button.addEventListener('click', () => sendMessage(button.dataset.suggest));
});

if (clearButton) {
    clearButton.addEventListener('click', async () => {
        if (!confirm('Clear all saved AI planner messages?')) return;
        try {
            const data = await deleteJson('/api/ai/history', {});
            clearChatRows();
            showToast(`Cleared ${data.removed} AI message(s).`, 'success');
        } catch (error) {
            showToast(error.message, 'danger');
        }
    });
}

if (historyButton) {
    historyButton.addEventListener('click', async () => {
        historyList.innerHTML = '<p class="muted">Loading history...</p>';
        try {
            const response = await fetch('/api/ai/history', { headers: { 'Accept': 'application/json' } });
            const history = await response.json();
            if (!history.length) {
                historyList.innerHTML = '<p class="muted">No AI planner history yet.</p>';
                return;
            }
            historyList.innerHTML = history.map(item => `
                <div class="history-item ${item.role}">
                    <div class="d-flex justify-content-between gap-3">
                        <strong>${item.role === 'user' ? 'You' : 'StudySync AI'}</strong>
                        <small>${item.created_label}</small>
                    </div>
                    <pre>${escapeHtml(item.content)}</pre>
                </div>
            `).join('');
        } catch (error) {
            historyList.innerHTML = '<p class="text-danger">Could not load history.</p>';
        }
    });
}

function escapeHtml(text) {
    return String(text).replace(/[&<>"']/g, (char) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    }[char]));
}
