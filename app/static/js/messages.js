const messengerLayout = document.querySelector('.messenger-layout');
const messageThread = document.getElementById('messageThread');
const messageForm = document.getElementById('messageForm');
const messageBody = document.getElementById('messageBody');
const conversationName = document.getElementById('conversationName');

function activeContactId() {
    return messengerLayout ? messengerLayout.dataset.selectedContact : '';
}

function scrollMessagesToBottom() {
    if (messageThread) {
        messageThread.scrollTop = messageThread.scrollHeight;
    }
}

function renderMessage(message) {
    const row = document.createElement('div');
    row.className = `dm-row ${message.is_mine ? 'mine' : 'theirs'}`;

    const bubble = document.createElement('div');
    bubble.className = 'dm-bubble';

    const paragraph = document.createElement('p');
    paragraph.textContent = message.body;

    const meta = document.createElement('small');
    meta.textContent = `${message.created_time} · ${message.is_mine ? 'You' : message.sender_name}`;

    bubble.append(paragraph, meta);
    row.appendChild(bubble);
    return row;
}

async function loadConversation(contactId) {
    if (!contactId || !messageThread) return;

    const response = await fetch(`/api/messages/${contactId}`, {
        headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) return;

    const data = await response.json();
    messageThread.innerHTML = '';
    data.messages.forEach(message => messageThread.appendChild(renderMessage(message)));
    if (conversationName) {
        conversationName.textContent = data.contact.name;
    }
    document.querySelectorAll('.messenger-contact').forEach(contact => {
        contact.classList.toggle('active', contact.dataset.contactId === String(contactId));
        if (contact.dataset.contactId === String(contactId)) {
            const unread = contact.querySelector('.unread-badge');
            if (unread) unread.remove();
        }
    });
    scrollMessagesToBottom();
}

document.querySelectorAll('.messenger-contact').forEach(contact => {
    contact.addEventListener('click', async event => {
        event.preventDefault();
        const contactId = contact.dataset.contactId;
        messengerLayout.dataset.selectedContact = contactId;
        if (messageBody) {
            messageBody.placeholder = `Type a message to ${contact.dataset.contactName}...`;
            messageBody.focus();
        }
        history.replaceState(null, '', `/messages?contact=${contactId}`);
        await loadConversation(contactId);
    });
});

if (messageForm) {
    messageForm.addEventListener('submit', async event => {
        event.preventDefault();
        const contactId = activeContactId();
        const body = messageBody.value.trim();
        if (!contactId || !body) return;

        const data = await postJson(`/api/messages/${contactId}`, { body });
        messageThread.appendChild(renderMessage(data.message));
        messageBody.value = '';
        scrollMessagesToBottom();
    });
}

scrollMessagesToBottom();
setInterval(() => {
    const contactId = activeContactId();
    if (contactId) loadConversation(contactId);
}, 5000);
