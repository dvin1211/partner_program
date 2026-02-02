export function setupAdvertiserTransactions() {

    // Обработка форм для выставления счетов
    function sendDetailsTransaction() {
        let sendDetailsBtn = document.querySelectorAll('.send_adv_details');
        const modal = document.getElementById('invoice_modal');
        sendDetailsBtn.forEach(item => {
            item.addEventListener('click', function () {
                const dataset = this.dataset;
                console.log(dataset)
                document.getElementById('advertiser_transaction_id').value = dataset.advTransactionId;
                document.getElementById('advertiser_transaction_requisites').innerHTML = `<a class='text-blue-700' href='/manager/advertiser_requisites/${dataset.advId}'>Реквизиты</a>`
                document.getElementById('advertiser_transaction_fio').innerText = dataset.advTransactionIfo.trim().toLowerCase() != 'none' ? dataset.advTransactionIfo : "Не указано";
                document.getElementById('advertiser_transaction_email').innerText = dataset.advTransactionEmail;
                document.getElementById('advertiser_transaction_amount').innerText = String(dataset.advTransactionAmount) + "₽";
                document.getElementById('advertiser_transaction_amount_with_commission').innerText = String(dataset.advTransactionAmountWithCommission) + "₽";

                modal.showModal();
            })
        })

        document.getElementById('invoiceForm').addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            fetch(`/manager/proccess_adv_transaction/${formData.get('transaction_id')}`, {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        const messageContainer = document.getElementById('adv_transactions_messages__container');
                        messageContainer.innerHTML = '';
                        modal.close();

                        const messageElement = document.createElement('div');
                        messageElement.className = `alert-message alert alert-error text-white p-4 mb-6 transition-transform transform duration-500 ease-out shadow-lg`;
                        messageElement.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>Произошла сетевая ошибка`;

                        messageContainer.appendChild(messageElement);

                        setTimeout(() => {
                            messageElement.classList.add('translate-x-full', 'opacity-0');
                            setTimeout(() => {
                                messageContainer.removeChild(messageElement);
                            }, 500);
                        }, 5000);

                        return false;
                    }
                    return response.json()
                })
                .then(data => {

                    const messageContainer = document.getElementById('adv_transactions_messages__container');
                    messageContainer.innerHTML = '';

                    modal.close();
                    data.messages.forEach(msg => {
                        const alertClass = msg.level;
                        const messageElement = document.createElement('div');
                        messageElement.className = `alert-message alert alert-${alertClass} text-white p-4 mb-6 transition-transform transform duration-500 ease-out shadow-lg`;
                        if (alertClass != 'success') {
                            messageElement.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>${msg.message}`;
                        } else {
                            messageElement.innerHTML = `<i class="fas fa-check-circle mr-2"></i>${msg.message}`;
                        }
                        messageContainer.appendChild(messageElement);

                        setTimeout(() => {
                            messageElement.classList.add('translate-x-full', 'opacity-0');
                            setTimeout(() => {
                                messageContainer.removeChild(messageElement);
                            }, 500);
                        }, 5000);
                        location.reload()
                    });
                })
        })
    }


    // Отклонение / Одобрение транзакция рекламодателей
    function approveOrRejectAdvertiserTransactions() {
        const rejectModal = document.getElementById('rejectAdvTransactionModal');
        const rejectBtns = document.querySelectorAll('.reject_adv_transaction');
        rejectBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const dataset = this.dataset;
                document.getElementById('reject_adv_transaction_id').innerText = dataset.advTransactionId;
                document.getElementById('reject_adv_transaction_requisites').innerHTML = `<a class='text-blue-700' href='/manager/advertiser_requisites/${dataset.advId}'>Реквизиты</a>`
                document.getElementById('reject_advertiser_transaction_id').value = dataset.advTransactionId;
                document.getElementById('reject_adv_transaction_fio').innerText = dataset.advTransactionIfo;
                document.getElementById('reject_adv_transaction_email').innerText = dataset.advTransactionEmail;
                document.getElementById('reject_adv_transaction_amount').innerText = String(dataset.advTransactionAmount) + "₽";
                document.getElementById('reject_adv_transaction_amount_with_commission').innerText = String(dataset.advTransactionAmountWithCommission) + "₽";
                rejectModal.showModal();
            })
        })

        const approveModal = document.getElementById('confirmAdvTransactionModal');
        const approveBtns = document.querySelectorAll('.approve_adv_transaction');
        approveBtns.forEach(btn => {
            btn.addEventListener('click', function () {
                const dataset = this.dataset;
                document.getElementById('approve_adv_transaction_id').innerText = dataset.advTransactionId;
                document.getElementById('approve_adv_transaction_requisites').innerHTML = `<a class='text-blue-700' href='/manager/advertiser_requisites/${dataset.advId}'>Реквизиты</a>`
                document.getElementById('confirm_advertiser_transaction_id').value = dataset.advTransactionId;
                document.getElementById('approve_adv_transaction_fio').innerText = dataset.advTransactionIfo;
                document.getElementById('approve_adv_transaction_email').innerText = dataset.advTransactionEmail;
                document.getElementById('approve_adv_transaction_amount').innerText = String(dataset.advTransactionAmount) + "₽";
                document.getElementById('approve_adv_transaction_amount_with_commission').innerText = String(dataset.advTransactionAmountWithCommission) + "₽";
                approveModal.showModal();
            })
        })

        // Одобрить транзакцию
        document.getElementById('confirmAdvTransactionModal').addEventListener('submit', function (event) {
            event.preventDefault();
            const modal = document.getElementById('confirmAdvTransactionModal');
            const formData = new FormData(event.target);            
            fetch(`/manager/approve_adv_transaction/${formData.get('transaction_id')}`, {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        const messageContainer = document.getElementById('adv_transactions_messages__container');
                        messageContainer.innerHTML = '';
                        modal.close();

                        const messageElement = document.createElement('div');
                        messageElement.className = `alert-message alert alert-error text-white p-4 mb-6 transition-transform transform duration-500 ease-out shadow-lg`;
                        messageElement.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>Произошла сетевая ошибка`;

                        messageContainer.appendChild(messageElement);

                        setTimeout(() => {
                            messageElement.classList.add('translate-x-full', 'opacity-0');
                            setTimeout(() => {
                                messageContainer.removeChild(messageElement);
                            }, 500);
                        }, 5000);

                        return false;
                    }
                    return response.json();
                })
                .then(data => {
                    const messageContainer = document.getElementById('adv_transactions_messages__container');
                    messageContainer.innerHTML = '';

                    modal.close();
                    data.messages.forEach(msg => {
                        const alertClass = msg.level;
                        const messageElement = document.createElement('div');
                        messageElement.className = `alert-message alert alert-${alertClass} text-white p-4 mb-6 transition-transform transform duration-500 ease-out shadow-lg`;
                        if (alertClass != 'success') {
                            messageElement.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>${msg.message}`;
                        } else {
                            messageElement.innerHTML = `<i class="fas fa-check-circle mr-2"></i>${msg.message}`;
                        }
                        messageContainer.appendChild(messageElement);

                        setTimeout(() => {
                            messageElement.classList.add('translate-x-full', 'opacity-0');
                            setTimeout(() => {
                                messageContainer.removeChild(messageElement);
                            }, 500);
                        }, 5000);
                        location.reload()
                    });
                })
        })

        // Отклонить транзакцию
        document.getElementById('rejectAdvTransactionForm').addEventListener('submit', function (event) {
            event.preventDefault();
            const modal = document.getElementById('rejectAdvTransactionModal');
            const formData = new FormData(event.target);
            fetch(`/manager/reject_adv_transaction/${formData.get('transaction_id')}`, {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        const messageContainer = document.getElementById('adv_transactions_messages__container');
                        messageContainer.innerHTML = '';
                        modal.close();

                        const messageElement = document.createElement('div');
                        messageElement.className = `alert-message alert alert-error text-white p-4 mb-6 transition-transform transform duration-500 ease-out shadow-lg`;
                        messageElement.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>Произошла сетевая ошибка`;

                        messageContainer.appendChild(messageElement);

                        setTimeout(() => {
                            messageElement.classList.add('translate-x-full', 'opacity-0');
                            setTimeout(() => {
                                messageContainer.removeChild(messageElement);
                            }, 500);
                        }, 5000);

                        return false;
                    }
                    return response.json();
                })
                .then(data => {
                    const messageContainer = document.getElementById('adv_transactions_messages__container');
                    messageContainer.innerHTML = '';

                    modal.close();
                    data.messages.forEach(msg => {
                        const alertClass = msg.level;
                        const messageElement = document.createElement('div');
                        messageElement.className = `alert-message alert alert-${alertClass} text-white p-4 mb-6 transition-transform transform duration-500 ease-out shadow-lg`;
                        if (alertClass != 'success') {
                            messageElement.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>${msg.message}`;
                        } else {
                            messageElement.innerHTML = `<i class="fas fa-check-circle mr-2"></i>${msg.message}`;
                        }
                        messageContainer.appendChild(messageElement);

                        setTimeout(() => {
                            messageElement.classList.add('translate-x-full', 'opacity-0');
                            setTimeout(() => {
                                messageContainer.removeChild(messageElement);
                            }, 500);
                        }, 5000);
                        location.reload()
                    });
                })
        })
    }

    function InitAdvertiserTransactions() {
        sendDetailsTransaction()
        approveOrRejectAdvertiserTransactions()
    }

    InitAdvertiserTransactions()
}