const groupChatThread = document.getElementById('groupChatThread');
const groupChatForm = document.getElementById('groupChatForm');
const groupChatBody = document.getElementById('groupChatBody');
const refreshGroupChat = document.getElementById('refreshGroupChat');
const groupChatMembers = document.getElementById('groupChatMembers');
const groupChatInviteForm = document.getElementById('groupChatInviteForm');
const inviteChatName = document.getElementById('inviteChatName');
const inviteChatEmail = document.getElementById('inviteChatEmail');
const inviteChatRole = document.getElementById('inviteChatRole');
const groupChatInviteResult = document.getElementById('groupChatInviteResult');
const copyGroupChatCode = document.getElementById('copyGroupChatCode');
const groupChatSummary = document.getElementById('groupChatSummary');

function scrollGroupChatToBottom() {
    if (groupChatThread) {
        groupChatThread.scrollTop = groupChatThread.scrollHeight;
    }
}

function renderGroupMember(member) {
    const wrapper = document.createElement('div');
    wrapper.className = `group-chat-member ${member.is_me ? 'selected' : ''}`;

    const avatar = document.createElement('a');
    avatar.className = 'mini-avatar';
    avatar.href = `/students/${member.id}`;
    avatar.textContent = member.initials;

    const info = document.createElement('div');
    const name = document.createElement('strong');
    const link = document.createElement('a');
    link.href = `/students/${member.id}`;
    link.textContent = member.name;
    name.appendChild(link);

    const small = document.createElement('small');
    small.textContent = `${member.role} · ${member.last_seen}`;

    info.append(name, small);
    wrapper.append(avatar, info);
    return wrapper;
}

function renderGroupMessage(message) {
    const row = document.createElement('div');
    row.className = `group-msg-row ${message.is_mine ? 'mine' : 'theirs'}`;

    if (!message.is_mine) {
        const avatar = document.createElement('span');
        avatar.className = 'mini-avatar';
        avatar.textContent = message.sender_initials;
        row.appendChild(avatar);
    }

    const bubble = document.createElement('div');
    bubble.className = 'group-msg-bubble';

    const meta = document.createElement('div');
    meta.className = 'group-msg-meta';

    const name = document.createElement('strong');
    name.textContent = message.is_mine ? 'You' : message.sender_name;

    const time = document.createElement('small');
    time.textContent = `${message.created_date}, ${message.created_time}`;

    const paragraph = document.createElement('p');
    paragraph.textContent = message.body;

    meta.append(name, time);
    bubble.append(meta, paragraph);
    row.appendChild(bubble);
    return row;
}

async function loadGroupChat() {
    if (!groupChatThread) return;
    const response = await fetch('/api/group-chat/messages', {
        headers: { 'Accept': 'application/json' }
    });
    if (!response.ok) return;
    const data = await response.json();
    if (groupChatMembers && Array.isArray(data.members)) {
        groupChatMembers.innerHTML = '';
        data.members.forEach(member => groupChatMembers.appendChild(renderGroupMember(member)));
        if (groupChatSummary) {
            groupChatSummary.innerHTML = `<span class="online-dot"></span> ${data.members.length} members · shared project discussion`;
        }
    }
    groupChatThread.innerHTML = '';
    data.messages.forEach(message => groupChatThread.appendChild(renderGroupMessage(message)));
    scrollGroupChatToBottom();
}

if (groupChatForm) {
    groupChatForm.addEventListener('submit', async event => {
        event.preventDefault();
        const body = groupChatBody.value.trim();
        if (!body) return;

        const data = await postJson('/api/group-chat/messages', { body });
        groupChatThread.appendChild(renderGroupMessage(data.message));
        groupChatBody.value = '';
        scrollGroupChatToBottom();
    });
}

if (refreshGroupChat) {
    refreshGroupChat.addEventListener('click', loadGroupChat);
}

scrollGroupChatToBottom();
setInterval(loadGroupChat, 6000);


if (copyGroupChatCode) {
    copyGroupChatCode.addEventListener('click', () => {
        const code = document.getElementById('groupChatCodeText')?.textContent || '';
        copyText(code, 'Group chat code copied.');
    });
}

if (groupChatInviteForm) {
    groupChatInviteForm.addEventListener('submit', async event => {
        event.preventDefault();
        const email = inviteChatEmail.value.trim();
        const name = inviteChatName.value.trim();
        const role = inviteChatRole.value;

        if (!email) {
            showToast('Please enter the student email.', 'danger');
            return;
        }

        const submitButton = groupChatInviteForm.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Inviting';

        try {
            const data = await postJson('/api/group/invite', { email, name, role });
            groupChatInviteResult.textContent = data.invite_text;
            showToast(data.message, 'success');
            await copyText(data.invite_text, 'Invite copied.');
            inviteChatEmail.value = '';
            inviteChatName.value = '';
            await loadGroupChat();
        } catch (error) {
            groupChatInviteResult.textContent = error.message;
            showToast(error.message, 'danger');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        }
    });
}
