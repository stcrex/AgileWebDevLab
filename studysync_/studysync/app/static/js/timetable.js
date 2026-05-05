document.addEventListener('DOMContentLoaded', () => {
    const panel = document.getElementById('timetablePanel');
    const detailModalEl = document.getElementById('eventDetailModal');
    const createModalEl = document.getElementById('eventModal');
    const form = document.getElementById('createEventForm');
    const deleteBtn = document.getElementById('deleteEventBtn');
    let selectedEventId = null;

    function setText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text || '';
    }

    function openModal(id) {
        if (window.openAppModal) {
            window.openAppModal(id);
            return;
        }
        const modalEl = document.getElementById(id);
        if (modalEl && window.bootstrap) bootstrap.Modal.getOrCreateInstance(modalEl).show();
    }

    function closeModal(id) {
        if (window.closeAppModal) {
            window.closeAppModal(id);
            return;
        }
        const modalEl = document.getElementById(id);
        if (modalEl && window.bootstrap) bootstrap.Modal.getOrCreateInstance(modalEl).hide();
    }

    function openEventDetails(card) {
        selectedEventId = card.dataset.eventId;
        setText('eventDetailTitle', card.dataset.eventTitle);
        setText('eventDetailType', card.dataset.eventType);
        setText('eventDetailStart', `Starts: ${card.dataset.eventStart}`);
        setText('eventDetailEnd', `Ends: ${card.dataset.eventEnd}`);
        setText('eventDetailDuration', `Duration: ${card.dataset.eventDuration}`);
        setText('eventDetailLocation', `Location: ${card.dataset.eventLocation}`);
        setText('eventDetailCourse', `Course: ${card.dataset.eventCourse}`);
        setText('eventDetailShared', `Shared with group: ${card.dataset.eventShared}`);
        openModal('eventDetailModal');
    }

    document.getElementById('createEventBtn')?.addEventListener('click', (event) => {
        // Use our robust modal helper so the create button works even if effects/CDN timing misbehaves.
        event.preventDefault();
        event.stopPropagation();
        openModal('eventModal');
    });

    document.querySelectorAll('[data-event-card]').forEach((card) => {
        card.addEventListener('click', () => openEventDetails(card));
        card.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openEventDetails(card);
            }
        });
    });

    document.querySelectorAll('#timetableFilters [data-filter]').forEach((button) => {
        button.addEventListener('click', () => {
            const selected = button.dataset.filter;
            document.querySelectorAll('#timetableFilters [data-filter]').forEach((btn) => btn.classList.remove('active'));
            button.classList.add('active');
            document.querySelectorAll('[data-event-card]').forEach((card) => {
                const matches = selected === 'all' || card.dataset.eventType === selected;
                card.classList.toggle('is-hidden', !matches);
            });
        });
    });

    function scrollTimetable(direction) {
        if (!panel) return;
        const verticalStep = Math.max(120, Math.round(panel.clientHeight * 0.55));
        const horizontalStep = Math.max(220, Math.round(panel.clientWidth * 0.45));
        const options = { behavior: 'smooth' };
        if (direction === 'up') panel.scrollBy({ top: -verticalStep, ...options });
        if (direction === 'down') panel.scrollBy({ top: verticalStep, ...options });
        if (direction === 'left') panel.scrollBy({ left: -horizontalStep, ...options });
        if (direction === 'right') panel.scrollBy({ left: horizontalStep, ...options });
        if (direction === 'now') panel.scrollTo({ top: 104, left: 0, ...options });
    }

    document.querySelectorAll('[data-scroll-timetable]').forEach((button) => {
        button.addEventListener('click', () => scrollTimetable(button.dataset.scrollTimetable));
    });

    if (panel) {
        panel.addEventListener('wheel', (event) => {
            // Trackpads sometimes send horizontal movement already. Shift + wheel intentionally scrolls sideways.
            if (event.shiftKey && Math.abs(event.deltaY) > Math.abs(event.deltaX)) {
                panel.scrollLeft += event.deltaY;
                event.preventDefault();
            }
        }, { passive: false });

        // Start near the first study hour instead of hiding the events below the fold.
        window.setTimeout(() => panel.scrollTo({ top: 84, left: 0 }), 120);
    }

    if (form) {
        const startInput = form.querySelector('[name="starts_at"]');
        const endInput = form.querySelector('[name="ends_at"]');
        const titleInput = form.querySelector('[name="title"]');

        function toDateTimeLocalValue(date) {
            const pad = (num) => String(num).padStart(2, '0');
            return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
        }

        function updateEndTime() {
            if (!startInput || !endInput || !startInput.value) return;
            const start = new Date(startInput.value);
            const end = new Date(endInput.value || 0);
            if (!endInput.value || end <= start) {
                start.setHours(start.getHours() + 1);
                endInput.value = toDateTimeLocalValue(start);
            }
        }

        if (startInput) startInput.addEventListener('change', updateEndTime);

        function formErrorMessage(data) {
            if (!data) return 'Could not save event. Please check the form.';
            if (data.error) return data.error;
            if (data.errors) {
                const parts = [];
                Object.entries(data.errors).forEach(([field, messages]) => {
                    const label = field.replace(/_/g, ' ');
                    const value = Array.isArray(messages) ? messages.join(', ') : String(messages);
                    parts.push(`${label}: ${value}`);
                });
                if (parts.length) return parts.join(' | ');
            }
            return 'Could not save event. Please check the form.';
        }

        function weekUrlFor(dateValue) {
            const url = new URL(window.location.href);
            const dateOnly = (dateValue || '').split('T')[0];
            if (dateOnly) url.searchParams.set('week', dateOnly);
            return url.toString();
        }

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            event.stopPropagation();

            const title = titleInput ? titleInput.value.trim() : '';
            if (!title) {
                showToast('Please enter an event title.', 'warning');
                titleInput?.focus();
                return;
            }
            if (startInput && endInput && new Date(endInput.value) <= new Date(startInput.value)) {
                showToast('End time must be after start time.', 'warning');
                endInput.focus();
                return;
            }

            const saveButton = form.querySelector('button[type="submit"]');
            const originalButtonHtml = saveButton ? saveButton.innerHTML : '';
            if (saveButton) {
                saveButton.disabled = true;
                saveButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Saving...';
            }

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'Accept': 'application/json',
                        'X-CSRFToken': typeof csrfToken === 'function' ? csrfToken() : ''
                    },
                    credentials: 'same-origin'
                });
                let data = {};
                try {
                    data = await response.json();
                } catch (parseError) {
                    data = {};
                }
                if (!response.ok) {
                    showToast(formErrorMessage(data), 'danger');
                    return;
                }

                showToast('Event saved. Opening the correct week...', 'success');
                closeModal('eventModal');
                window.setTimeout(() => {
                    window.location.href = weekUrlFor(startInput ? startInput.value : data.starts_at);
                }, 350);
            } catch (error) {
                showToast(error.message || 'Could not save event. Please try again.', 'danger');
            } finally {
                if (saveButton) {
                    saveButton.disabled = false;
                    saveButton.innerHTML = originalButtonHtml;
                }
            }
        });
    }

    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (!selectedEventId) return;
            if (!confirm('Delete this timetable event?')) return;
            try {
                await deleteJson(`/api/events/${selectedEventId}`);
                const card = document.querySelector(`[data-event-id="${selectedEventId}"]`);
                if (card) card.remove();
                closeModal('eventDetailModal');
                showToast('Event deleted from timetable.', 'success');
            } catch (error) {
                showToast(error.message, 'danger');
            }
        });
    }

    if (createModalEl) {
        createModalEl.addEventListener('shown.bs.modal', () => {
            const title = createModalEl.querySelector('[name="title"]');
            if (title) title.focus();
        });
    }

    if (detailModalEl) {
        detailModalEl.addEventListener('hidden.bs.modal', () => { selectedEventId = null; });
    }
});
