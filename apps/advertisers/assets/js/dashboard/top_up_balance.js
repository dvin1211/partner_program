export function setupTopUpBalance() {
    const modal = document.getElementById('topup_modal');
    const form = document.getElementById('top_up_balance');
    const messageContainer = document.getElementById('dashboard_messages__container');

    const ALERT_DURATION = 5000;
    const ANIMATION_DURATION = 500;

    const createAlertMessage = (message, level = 'error') => {
        const iconClass = level === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';
        const alertClass = `alert-${level}`;

        return `
            <div class="alert-message alert ${alertClass} text-white p-4 mr-6 mb-6 transition-all duration-300 ease-out shadow-lg animate-fade-in">
                <i class="fas ${iconClass} mr-2"></i>${message}
            </div>
        `;
    };

    const showMessages = (messages) => {
        messageContainer.innerHTML = '';

        messages.forEach(msg => {
            const messageElement = document.createElement('div');
            messageElement.innerHTML = createAlertMessage(msg.message, msg.level);
            messageContainer.appendChild(messageElement.firstElementChild);

            setTimeout(() => {
                const alert = messageContainer.querySelector('.alert-message:last-child');
                if (alert) {
                    alert.classList.add('animate-slide-out-left','transform-gpu','transition-all','duration-800','ease-in-out');
                    setTimeout(() => alert.remove(), ANIMATION_DURATION);
                }
            }, ALERT_DURATION);
        });
    };

    const showNetworkError = () => {
        modal.close();
        showMessages([{
            level: 'error',
            message: 'Произошла сетевая ошибка'
        }]);
    };

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(form);

        try {
            addAlertStyles();
            const response = await fetch('/advertiser/top_up_balance', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                showNetworkError();
                return;
            }
            const data = await response.json();

            modal.close();
            showMessages(data.messages || []);

        } catch (error) {
            showNetworkError();
        }
    });
}

const addAlertStyles = () => {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-out-left {
            0% {
                opacity: 1;
                transform: translateX(0);
            }
            70% {
                opacity: 0;
                transform: translateX(+100%);
            }
            100% {
                opacity: 0;
                transform: translateX(+100%);
                max-height: 0;
                margin-bottom: 0;
                padding: 0;
                border: none;
            }
        }
        
        .animate-slide-out-left {
            animation: slide-out-left 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            pointer-events: none;
        }
    `;
    document.head.appendChild(style);
};