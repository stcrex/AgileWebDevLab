function csrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

async function apiRequest(url, payload = {}, method = 'POST') {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken(),
            'Accept': 'application/json'
        }
    };
    if (method !== 'GET' && method !== 'HEAD') {
        options.body = JSON.stringify(payload || {});
    }
    const response = await fetch(url, options);
    let data = {};
    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }
    if (!response.ok) {
        throw new Error(data.error || data.message || `Request failed: ${response.status}`);
    }
    return data;
}

async function postJson(url, payload) {
    return apiRequest(url, payload, 'POST');
}

async function deleteJson(url, payload) {
    return apiRequest(url, payload, 'DELETE');
}

function showToast(message, variant = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container || !window.bootstrap) {
        alert(message);
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${variant} border-0`;
    toast.setAttribute('role', 'status');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    container.appendChild(toast);
    const instance = new bootstrap.Toast(toast, { delay: 2600 });
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
    instance.show();
}

async function copyText(text, successMessage = 'Copied to clipboard.') {
    try {
        await navigator.clipboard.writeText(text);
        showToast(successMessage, 'success');
    } catch (error) {
        showToast('Copy failed. You can manually select and copy it.', 'warning');
    }
}

document.addEventListener('click', async (event) => {
    const reminderButton = event.target.closest('[data-action="reminder-toggle"]');
    if (!reminderButton) return;
    const row = reminderButton.closest('[data-reminder-id]');
    const id = row.dataset.reminderId;
    try {
        const data = await postJson(`/api/reminders/${id}/toggle`, {});
        reminderButton.classList.toggle('checked', data.is_done);
        showToast(data.is_done ? 'Reminder marked done.' : 'Reminder reopened.', 'success');
    } catch (error) {
        showToast(error.message, 'danger');
    }
});

window.getCsrfToken = csrfToken;
window.apiRequest = apiRequest;
window.postJson = postJson;
window.deleteJson = deleteJson;
window.showToast = showToast;
window.copyText = copyText;

// Premium UI interactions: cursor glow, reveal-on-scroll, ripple buttons, card tilt.
(function () {
    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function addRipple(event) {
        const target = event.target.closest('.btn, .nav-link, .filter-pill, .suggestion-chips button');
        if (!target || target.disabled || reduceMotion) return;
        const rect = target.getBoundingClientRect();
        const ripple = document.createElement('span');
        ripple.className = 'ripple-circle';
        ripple.style.left = `${event.clientX - rect.left}px`;
        ripple.style.top = `${event.clientY - rect.top}px`;
        target.appendChild(ripple);
        window.setTimeout(() => ripple.remove(), 700);
    }

    function initCursorGlow() {
        const glow = document.getElementById('cursorGlow');
        if (!glow || reduceMotion) return;
        let ticking = false;
        let x = -500;
        let y = -500;
        window.addEventListener('pointermove', (event) => {
            x = event.clientX - 180;
            y = event.clientY - 180;
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    glow.style.setProperty('--cursor-x', `${x}px`);
                    glow.style.setProperty('--cursor-y', `${y}px`);
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }

    function initReveal() {
        const selectors = [
            '.card-panel', '.exam-card', '.course-card-action', '.handbook-card',
            '.member-card', '.group-day-event', '.preference-toggle', '.theme-preview',
            '.profile-panel', '.message-bubble', '.feature-pill', '.auth-card'
        ].join(',');
        const elements = Array.from(document.querySelectorAll(selectors));
        if (!elements.length) return;
        elements.forEach((element, index) => {
            element.classList.add('reveal-ready');
            element.style.transitionDelay = `${Math.min(index * 35, 280)}ms`;
        });
        if (!('IntersectionObserver' in window) || reduceMotion) {
            elements.forEach((element) => element.classList.add('reveal-visible'));
            return;
        }
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('reveal-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -35px 0px' });
        elements.forEach((element) => observer.observe(element));
    }

    function initSurfaceGlowAndTilt() {
        if (reduceMotion) return;
        const surfaces = Array.from(document.querySelectorAll('.card-panel, .exam-card, .course-card-action, .handbook-card, .member-card, .profile-panel, .auth-card'));
        surfaces.forEach((surface) => {
            surface.classList.add('interactive-surface');
            surface.addEventListener('pointermove', (event) => {
                const rect = surface.getBoundingClientRect();
                const px = (event.clientX - rect.left) / rect.width;
                const py = (event.clientY - rect.top) / rect.height;
                const rotateX = (0.5 - py) * 3.5;
                const rotateY = (px - 0.5) * 3.5;
                surface.style.setProperty('--surface-x', `${Math.round(px * 100)}%`);
                surface.style.setProperty('--surface-y', `${Math.round(py * 100)}%`);
                surface.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-2px)`;
            });
            surface.addEventListener('pointerleave', () => {
                surface.style.transform = '';
                surface.style.removeProperty('--surface-x');
                surface.style.removeProperty('--surface-y');
            });
        });
    }

    function initAnimatedNumbers() {
        if (reduceMotion) return;
        const candidates = Array.from(document.querySelectorAll('.member-stats strong, .preference-stat-grid strong'));
        candidates.forEach((el) => {
            const raw = el.textContent.trim();
            if (!/^\d+$/.test(raw)) return;
            const end = parseInt(raw, 10);
            el.textContent = '0';
            const startTime = performance.now();
            const duration = 650 + Math.min(end * 15, 650);
            function step(now) {
                const progress = Math.min((now - startTime) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                el.textContent = Math.round(end * eased).toString();
                if (progress < 1) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        });
    }

    document.addEventListener('click', addRipple);
    document.addEventListener('DOMContentLoaded', () => {
        initCursorGlow();
        initReveal();
        initSurfaceGlowAndTilt();
        initAnimatedNumbers();
        document.body.classList.add('ui-ready');
    });
})();

// Reliable modal manager for StudySync.
// Uses Bootstrap when it is available, and falls back to plain DOM logic when
// the CDN is offline. It only listens for normal click events, so submit
// buttons inside modals are never swallowed before their forms can run.
(function () {
    function getModal(idOrElement) {
        if (!idOrElement) return null;
        if (typeof idOrElement === 'string') {
            return document.getElementById(idOrElement.replace(/^#/, ''));
        }
        return idOrElement.closest ? idOrElement.closest('.modal') : idOrElement;
    }

    function removeBackdrops() {
        document.querySelectorAll('.modal-backdrop, .app-managed-backdrop').forEach((node) => node.remove());
    }

    function cleanupBody() {
        if (document.querySelector('.modal.show')) return;
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('overflow');
        document.body.style.removeProperty('padding-right');
        document.body.removeAttribute('data-bs-overflow');
        document.body.removeAttribute('data-bs-padding-right');
        removeBackdrops();
    }

    function manualOpen(modal) {
        if (!modal) return;
        document.querySelectorAll('.modal.show').forEach((openModal) => {
            if (openModal !== modal) manualClose(openModal);
        });
        removeBackdrops();
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop app-managed-backdrop fade show';
        document.body.appendChild(backdrop);
        modal.style.display = 'block';
        modal.classList.add('show');
        modal.removeAttribute('aria-hidden');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('role', 'dialog');
        document.body.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
        modal.dispatchEvent(new CustomEvent('app-modal-shown', { bubbles: true }));
    }

    function manualClose(modal) {
        if (!modal) return;
        modal.classList.remove('show');
        modal.style.display = 'none';
        modal.setAttribute('aria-hidden', 'true');
        modal.removeAttribute('aria-modal');
        modal.removeAttribute('role');
        modal.dispatchEvent(new CustomEvent('app-modal-hidden', { bubbles: true }));
        cleanupBody();
    }

    function openModal(modalOrId) {
        const modal = getModal(modalOrId);
        if (!modal) return;
        if (window.bootstrap && bootstrap.Modal) {
            // Hide any existing modal first to avoid stacked/dim stuck overlays.
            document.querySelectorAll('.modal.show').forEach((openModal) => {
                if (openModal !== modal) bootstrap.Modal.getOrCreateInstance(openModal).hide();
            });
            bootstrap.Modal.getOrCreateInstance(modal, { backdrop: true, keyboard: true }).show();
            window.setTimeout(cleanupBody, 450);
        } else {
            manualOpen(modal);
        }
    }

    function closeModal(modalOrId) {
        const modal = getModal(modalOrId) || document.querySelector('.modal.show');
        if (!modal) return;
        if (window.bootstrap && bootstrap.Modal) {
            const instance = bootstrap.Modal.getInstance(modal) || bootstrap.Modal.getOrCreateInstance(modal);
            instance.hide();
            window.setTimeout(cleanupBody, 450);
        } else {
            manualClose(modal);
        }
    }

    window.openAppModal = openModal;
    window.closeAppModal = closeModal;
    window.cleanupAppModals = function () {
        document.querySelectorAll('.modal.show').forEach(closeModal);
        window.setTimeout(cleanupBody, 450);
    };

    document.addEventListener('click', (event) => {
        const opener = event.target.closest('[data-app-open-modal], [data-bs-toggle="modal"][data-bs-target]');
        if (!opener) return;
        const target = opener.getAttribute('data-app-open-modal') || opener.getAttribute('data-bs-target');
        const modal = getModal(target);
        if (!modal) return;
        event.preventDefault();
        openModal(modal);
    });

    document.addEventListener('click', (event) => {
        const closeButton = event.target.closest('[data-app-close-modal], [data-bs-dismiss="modal"]');
        if (closeButton) {
            const modal = closeButton.closest('.modal');
            if (modal) {
                event.preventDefault();
                closeModal(modal);
            }
            return;
        }
        // Fallback backdrop close: only close when the actual modal shell is clicked,
        // not when a form/button inside the dialog is clicked.
        if (event.target.classList && event.target.classList.contains('modal') && event.target.classList.contains('show')) {
            closeModal(event.target);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;
        const modal = document.querySelector('.modal.show');
        if (modal) closeModal(modal);
    });

    document.addEventListener('hidden.bs.modal', cleanupBody);
    document.addEventListener('shown.bs.modal', () => window.setTimeout(removeBackdrops, 10));
})();
