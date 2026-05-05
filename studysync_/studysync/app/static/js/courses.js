let selectedCourse = null;

function courseFromElement(element) {
    const card = element.closest('[data-course-card]');
    if (!card) return null;
    return {
        id: card.dataset.courseId,
        code: card.dataset.courseCode,
        title: card.dataset.courseTitle,
        colour: card.dataset.courseColour,
        events: card.dataset.courseEvents || '0',
        exams: card.dataset.courseExams || '0',
        url: card.dataset.courseUrl
    };
}

function showCourseModal(id) {
    if (window.openAppModal) return window.openAppModal(id);
    const node = document.getElementById(id);
    if (node && window.bootstrap) bootstrap.Modal.getOrCreateInstance(node).show();
}

function hideCourseModal(id) {
    if (window.closeAppModal) return window.closeAppModal(id);
    const node = document.getElementById(id);
    if (node && window.bootstrap) bootstrap.Modal.getOrCreateInstance(node).hide();
}

function resetModalForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    const submit = form.querySelector('[type="submit"]');
    if (submit) {
        submit.disabled = false;
        submit.innerHTML = submit.dataset.originalLabel || submit.innerHTML;
    }
}

function fillCourseInfo(course) {
    if (!course) return;
    selectedCourse = course;
    document.getElementById('courseInfoCode').textContent = course.code;
    document.getElementById('courseInfoTitle').textContent = course.title;
    document.getElementById('courseInfoEvents').textContent = course.events;
    document.getElementById('courseInfoExams').textContent = course.exams;
    document.getElementById('modalViewCourse').href = course.url;
}

function prepareEventModal(course) {
    if (!course) return;
    selectedCourse = course;
    resetModalForm('courseEventForm');
    const courseId = document.getElementById('courseEventCourseId');
    const title = document.getElementById('courseEventTitle');
    const location = document.getElementById('courseEventLocation');
    if (courseId) courseId.value = course.id;
    if (title) title.value = `${course.code} Lecture`;
    if (location && !location.value.trim()) location.value = 'Room / Lab';
    const modalTitle = document.getElementById('courseEventModalTitle');
    if (modalTitle) modalTitle.innerHTML = `<i class="bi bi-calendar-plus"></i> Create Event for ${course.code}`;
}

function prepareExamModal(course) {
    if (!course) return;
    selectedCourse = course;
    resetModalForm('courseExamForm');
    const courseId = document.getElementById('courseExamCourseId');
    const title = document.getElementById('courseExamTitle');
    const room = document.getElementById('courseExamRoom');
    const weight = document.getElementById('courseExamWeight');
    if (courseId) courseId.value = course.id;
    if (title) title.value = `${course.code} Mid-semester Test`;
    if (room && !room.value.trim()) room.value = 'Room TBC';
    if (weight && !weight.value) weight.value = '20';
    const modalTitle = document.getElementById('courseExamModalTitle');
    if (modalTitle) modalTitle.innerHTML = `<i class="bi bi-file-earmark-plus"></i> Create Exam for ${course.code}`;
}

function openFromCourseInfo(targetId, prepareFn) {
    if (typeof prepareFn === 'function') prepareFn();
    hideCourseModal('courseInfoModal');
    window.setTimeout(() => showCourseModal(targetId), 180);
}

function showCourseDetailsFromCard(card) {
    const course = courseFromElement(card);
    if (!course) return;
    fillCourseInfo(course);
    showCourseModal('courseInfoModal');
}

function formErrorMessage(data) {
    if (!data) return 'Could not save. Please check the form.';
    if (data.error) return data.error;
    if (data.errors) {
        const parts = [];
        Object.entries(data.errors).forEach(([field, messages]) => {
            const value = Array.isArray(messages) ? messages.join(', ') : String(messages);
            parts.push(`${field.replace(/_/g, ' ')}: ${value}`);
        });
        if (parts.length) return parts.join(' | ');
    }
    return 'Could not save. Please check the form.';
}

function weekUrlFor(dateValue) {
    const url = new URL('/timetable', window.location.origin);
    const dateOnly = (dateValue || '').split('T')[0];
    if (dateOnly) url.searchParams.set('week', dateOnly);
    return url.toString();
}

async function submitModalForm(form, successMessage, redirectBuilder) {
    const submit = form.querySelector('[type="submit"]');
    const original = submit ? submit.innerHTML : '';
    if (submit) {
        if (!submit.dataset.originalLabel) submit.dataset.originalLabel = original;
        submit.disabled = true;
        submit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Saving...';
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
        try { data = await response.json(); } catch (_) { data = {}; }
        if (!response.ok) throw new Error(formErrorMessage(data));
        showToast(successMessage, 'success');
        if (redirectBuilder) {
            window.setTimeout(() => { window.location.href = redirectBuilder(data); }, 300);
        }
    } catch (error) {
        showToast(error.message, 'danger');
    } finally {
        if (submit) {
            submit.disabled = false;
            submit.innerHTML = submit.dataset.originalLabel || original;
        }
    }
}

document.addEventListener('click', (event) => {
    const addEventButton = event.target.closest('[data-action="course-add-event"]');
    if (addEventButton) {
        event.preventDefault();
        event.stopPropagation();
        const course = courseFromElement(addEventButton);
        prepareEventModal(course);
        showCourseModal('courseEventModal');
        return;
    }

    const addExamButton = event.target.closest('[data-action="course-add-exam"]');
    if (addExamButton) {
        event.preventDefault();
        event.stopPropagation();
        const course = courseFromElement(addExamButton);
        prepareExamModal(course);
        showCourseModal('courseExamModal');
        return;
    }

    if (event.target.closest('[data-no-card-open]')) return;

    const card = event.target.closest('[data-course-card]');
    if (!card) return;
    showCourseDetailsFromCard(card);
});

document.addEventListener('keydown', (event) => {
    if (!['Enter', ' '].includes(event.key)) return;
    const card = event.target.closest('[data-course-card]');
    if (!card || event.target.closest('[data-no-card-open]')) return;
    event.preventDefault();
    showCourseDetailsFromCard(card);
});

document.getElementById('modalAddCourseEvent')?.addEventListener('click', (event) => {
    event.preventDefault();
    if (!selectedCourse) return;
    openFromCourseInfo('courseEventModal', () => prepareEventModal(selectedCourse));
});

document.getElementById('modalAddCourseExam')?.addEventListener('click', (event) => {
    event.preventDefault();
    if (!selectedCourse) return;
    openFromCourseInfo('courseExamModal', () => prepareExamModal(selectedCourse));
});

document.getElementById('courseEventForm')?.addEventListener('submit', (event) => {
    event.preventDefault();
    submitModalForm(event.currentTarget, 'Course event saved. Opening timetable...', (data) => {
        const start = event.currentTarget.querySelector('[name="starts_at"]')?.value || data.starts_at;
        return weekUrlFor(start);
    });
});

document.getElementById('courseExamForm')?.addEventListener('submit', (event) => {
    event.preventDefault();
    submitModalForm(event.currentTarget, 'Exam saved. Opening exam page...', (data) => data.url || '/exams');
});
