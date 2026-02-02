const form = document.getElementById('auth_form');
form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    try {
        const response = await fetch(`auth/login`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            return showToast('Ошибка при авторизации', 'error');
        }

        const result = await response.json();
        if (!result.success) {
            return showToast('Неверный логин или пароль', 'error');
        }
    }
    catch (error) {
        return showToast('Ошибка сети', 'error');
    }
    showToast('Успешная авторизация', 'success');
    setTimeout(() => {
        location.assign('/dashboard')
    }, 2000);
})

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert-message alert alert-${type} text-white p-4 mr-6 mb-6 shadow-lg animate-fade-in z-999`;
    toast.innerHTML = `
            <div>
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>`;

    document.getElementById('auth_messages__container').appendChild(toast);
    setTimeout(() => {
        toast.classList.add('animate-slide-out-left');
        setTimeout(() => toast.remove(), 800);
    }, 5000);
}