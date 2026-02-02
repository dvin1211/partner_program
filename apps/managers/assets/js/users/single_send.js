export function setupSingleSend() {
    const sendButtons = document.querySelectorAll('.send_email');
    let submitHandler = null; // Храним ссылку на обработчик
    
    sendButtons.forEach(button => {
        button.addEventListener('click', function () {
            const dataset = this.dataset;
            let fio = dataset.userFullName != '' ? dataset.userFullName : "Не указано";
            document.getElementById('send-msg-user-fio').innerText = fio;
            document.getElementById('send-msg-user-email').innerHTML = dataset.userEmail;
            document.getElementById('send-msg-modal').show();
            
            const form = document.getElementById('send-msg-form');
            
            if (submitHandler) {
                form.removeEventListener('submit', submitHandler);
            }
            
            submitHandler = async function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch(`/manager/make_single_notification/${dataset.userId}`, {
                    method: "POST",
                    body: formData
                });
                if (!response.ok) throw new Error("Ошибка сети");
                showToast("Сообщение отправлено пользователю!");
                document.getElementById('send-msg-modal').close();
                return await response.json();
            };
            
            // Добавляем новый обработчик
            form.addEventListener('submit', submitHandler);
        });
    });
}


function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert-message alert alert-${type} text-white p-4 mr-6 mb-6 shadow-lg animate-fade-in`;
        toast.innerHTML = `
            <div>
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>`;
        document.getElementById('toast-container').appendChild(toast);
        setTimeout(() => {
            toast.classList.add('animate-slide-out-left');
            setTimeout(() => toast.remove(), 800);
        }, 5000);
    }