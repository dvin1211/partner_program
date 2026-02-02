export function setupQuickWithdraw() {
    const modal = document.getElementById('withdrawModal');
    const form = document.getElementById('withdraw_money_partner');
    const messageContainer = document.getElementById('dashboard_messages__container');
    const balanceElement = document.getElementById('partner-balance');
    const amountInput = form.querySelector('input[name="amount"]');

    const ALERT_DURATION = 5000;
    const ANIMATION_DURATION = 500;

    const parseNumberWithComma = (numberString) => {
        if (!numberString) return 0;

        let cleaned = numberString.toString().replace(/\s/g, ''); 

        if (cleaned.includes(',') && (!cleaned.includes('.') || cleaned.lastIndexOf(',') > cleaned.lastIndexOf('.'))) {
            cleaned = cleaned.replace(/\./g, '')
                .replace(',', '.');   
        }
        else if (cleaned.includes('.') && (!cleaned.includes(',') || cleaned.lastIndexOf('.') > cleaned.lastIndexOf(','))) {
            cleaned = cleaned.replace(/,/g, '');  
        }
        else if (cleaned.includes(',') && cleaned.includes('.')) {
            const lastSeparator = Math.max(cleaned.lastIndexOf(','), cleaned.lastIndexOf('.'));
            if (cleaned[lastSeparator] === ',') {
                cleaned = cleaned.replace(/\./g, '').replace(',', '.');
            } else {
                cleaned = cleaned.replace(/,/g, '');
            }
        }

        const result = parseFloat(cleaned);
        return isNaN(result) ? 0 : result;
    };

    const formatNumberWithComma = (number) => {
        return number.toFixed(2).replace('.', ',');
    };

    const getAmountFromForm = () => {
        if (!amountInput) return 0;
        const inputValue = amountInput.value;
        return parseNumberWithComma(inputValue);
    };

    const animateBalance = (withdrawAmount, duration = 1000) => {
        if (!balanceElement) return;

        const currentText = balanceElement.textContent;
        const currentBalance = parseNumberWithComma(currentText);
        const targetBalance = currentBalance - withdrawAmount;

        if (targetBalance < 0) {
            console.warn('Баланс не может быть отрицательным');
            return;
        }

        const startTime = performance.now();

        function update(currentTime) {
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = currentBalance - (withdrawAmount * easeOut);

            balanceElement.textContent = formatNumberWithComma(currentValue);

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    };

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
                    alert.classList.add('animate-slide-out-left', 'transform-gpu', 'transition-all', 'duration-800', 'ease-in-out');
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
        const withdrawAmount = getAmountFromForm();

        if (withdrawAmount <= 0) {
            showMessages([{
                level: 'error',
                message: 'Введите корректную сумму для вывода'
            }]);
            return;
        }

        const currentBalance = parseNumberWithComma(balanceElement.textContent);
        console.log('Withdraw amount:', withdrawAmount, 'Current balance:', currentBalance);

        if (withdrawAmount > currentBalance) {
            showMessages([{
                level: 'error',
                message: 'Недостаточно средств на балансе'
            }]);
            return;
        }

        try {
            addAlertStyles();

            const requestData = new URLSearchParams();
            for (let [key, value] of formData.entries()) {
                if (key === 'amount') {
                    requestData.append(key, withdrawAmount.toString());
                } else {
                    requestData.append(key, value);
                }
            }

            const response = await fetch('/partner/create_payout_request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: requestData
            });

            if (!response.ok) {
                console.error('Server error:', response.status, response.statusText);
                showNetworkError();
                return;
            }

            const data = await response.json();
            console.log('Success:', data);

            modal.close();

            setTimeout(() => {
                animateBalance(withdrawAmount, 1000);
            }, 300);
            document.getElementById('partner-withdraw-balance').textContent = currentBalance - withdrawAmount;
            showMessages(data.messages || []);

            form.reset();

        } catch (error) {
            console.error('Request failed:', error);
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

        #partner-balance {
            transition: color 0.3s ease;
        }
        
        #partner-balance.animating {
            color: #ff6b6b;
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
};