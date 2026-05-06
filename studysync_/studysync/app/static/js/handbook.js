document.querySelectorAll('.add-handbook-course').forEach((button) => {
    button.addEventListener('click', async () => {
        const subjectId = button.dataset.subjectId;
        button.disabled = true;
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Adding...';

        try {
            const response = await fetch(`/api/handbook/subjects/${subjectId}/add-course`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRFToken': window.getCsrfToken(),
                },
            });
            const result = await response.json();
            if (!response.ok || !result.ok) {
                throw new Error(result.error || 'Unable to add subject');
            }
            button.classList.remove('btn-primary');
            button.classList.add('btn-success');
            button.innerHTML = '<i class="bi bi-check2-circle"></i> Added';
            const toast = document.createElement('div');
            toast.className = 'inline-toast';
            toast.textContent = result.message;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 2400);
        } catch (error) {
            button.disabled = false;
            button.innerHTML = originalText;
            alert(error.message);
        }
    });
});
