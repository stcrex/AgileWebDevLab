# GitHub Issue & PR kit — unified Group workspace

Use the sections below on GitHub: create an Issue first, link it from the PR with `Closes #NNN` (or `Fixes #NNN`).

---

## Suggested Issue title

**Merge group chat, invites, and common-free-slot booking into one Group workspace**

---

## Issue body (copy below this line)

### Summary

Group collaboration was split conceptually between a separate chat/invite surface and the `/group/<id>` booking page. The standalone `group_chat` blueprint was never registered in `create_app`, so `/group-chat` did not work. We want one **Group workspace** per study group ID and clearer documentation for markers and teammates.

### Scope / proposed solution

- Single page at **`/group/<id>`**: messages, member list, email invite, and existing common-free-slot + **Book** flow (unchanged JSON APIs).
- **`GET /group-chat`**: redirects logged-in users to `/group/<id>` using their first `GroupMember` row; if none, flash and redirect to Exams.
- Service module **`app/services/group_workspace.py`** for messages, invites, and member queries; **`group_book`** blueprint owns all routes.
- Remove dead **`app/routes/group.py`** and unused **`pages/group_chat.html`**.
- Extend **`tests/test_group_book.py`** for workspace render, redirects, messaging, invites, and 404 when not a member.
- Update **README** (§3.5–3.6) with URL table and step-by-step Group usage.

### Acceptance criteria

- [ ] Authenticated member can load `/group/<id>`, send a message, and see `GroupMessage` rows for that group only.
- [ ] Invite adds a user + `GroupMember` when new; duplicate member does not duplicate rows or spam invite system messages.
- [ ] Existing booking APIs and behaviour unchanged; **`pytest tests/test_group_book.py`** passes.
- [ ] **`pytest -m "not selenium"`** green.
- [ ] README documents `/group/<id>`, `/group-chat`, messages, invites, booking, and default invite password caveat.

---

## Suggested PR title

**feat(group): unified workspace (chat, invite, booking) + README + tests**

---

## PR description (copy below this line)

### What

- Merges **chat**, **invite-by-email**, and **common free slot booking** into **`/group/<group_id>`** (`templates/group_book.html`).
- Adds **`GET /group-chat`** → redirect to the user’s first group workspace (or Exams with flash if not in any group).
- Extracts helpers to **`app/services/group_workspace.py`**; extends **`app/blueprints/group_book.py`** with `POST /group/<id>/message` and `POST /group/<id>/invite`.
- Removes unregistered **`app/routes/group.py`** and **`app/templates/pages/group_chat.html`**.
- StudySync **`app/templates/base.html`**: nav **Group** uses `url_for('group_book.group_chat_redirect')`.
- **README**: new §3.6 “Using the Group workspace”, URL table updates, layout + troubleshooting notes.
- **Tests**: workspace render, redirect, message persist, non-member 404, invite new user, duplicate member idempotency.

### How to verify

```bash
pytest tests/test_group_book.py -v
pytest -m "not selenium"
```

Manual: log in as `alice@lab.local` / `labdemo123` → open **`/group/1`** or **`/group-chat`** → send message, optional invite, book a slot.

### Related

Closes #__ (replace with your GitHub issue number)

---

### 中文摘要（小组内部说明）

- **Issue**：说明为何合并、验收标准。  
- **PR**：实现合并后的 Group 工作台、重定向、测试与 README；发 PR 时把 `Closes #编号` 换成真实 Issue 号。
