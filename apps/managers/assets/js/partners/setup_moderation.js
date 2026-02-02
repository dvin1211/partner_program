export function setupTransactions() {
    const modal = document.getElementById('payout-details-modal');
    const buttons = document.querySelectorAll('.approve-btn, .reject-btn, .details-btn');
    
    buttons.forEach(btn => {
        btn.addEventListener('click', function() {
            const dataset = this.dataset;
            const actionType = this.classList.contains('approve-btn') ? 'approve' : 
                             this.classList.contains('reject-btn') ? 'reject' : 'details';
            

            fillTransactionData(dataset);

            manageForms(actionType, dataset);

            modal.showModal();
        });
    });
}

function fillTransactionData(dataset) {
    document.getElementById('TransactionID').textContent = dataset.transactionId;
    document.getElementById('TransactionAmount').textContent = `${dataset.transactionAmount} ₽`;
    document.getElementById('TransactionDate').textContent = dataset.transactionDate;
    document.getElementById('TransactionPartner').textContent = dataset.transactionPartner;
    document.getElementById('TransactionPartnerEmail').textContent = dataset.transactionPartnerEmail;
    
    updateTransactionStatus(dataset.transactionStatus);
    
    updateTransactionRequisites(dataset);
}

function updateTransactionStatus(status) {
    const transactionStatus = document.getElementById('TransactionStatus');
    transactionStatus.innerHTML = '';
    
    const statusBadge = document.createElement('span');
    statusBadge.classList.add('badge', 'badge-warning');
    statusBadge.textContent = status;
    transactionStatus.appendChild(statusBadge);
}

function updateTransactionRequisites(dataset) {
    const requisitesContainer = document.getElementById('TransactionRequisites');
    requisitesContainer.innerHTML = '';
    
    let paymentMethod = '';
    let requisitesHTML = '';
    
    if (dataset.transactionMethod === "card") {
        paymentMethod = "Банковская карта";
        requisitesHTML = `
            Карта: ${dataset.transactionCardNumber}<br>
            Банк: ${dataset.transactionBankName}<br>
            Получатель: ${dataset.transactionCardOwner}
        `;
    } else if (dataset.transactionMethod === "bank_transfer") {
        paymentMethod = "Банковский перевод";
        requisitesHTML = `
            Владелец счёта: ${dataset.transactionBankAccountHolderName}<br>
            Номер счёта: ${dataset.transactionBankAccountNumber}<br>
            БИК банка: ${dataset.transactionBankBic}
        `;
    }
    
    document.getElementById('TransactionPaymentMethod').textContent = paymentMethod;
    
    if (requisitesHTML) {
        const requisitesElement = document.createElement('div');
        requisitesElement.classList.add('transaction_requisites_data', 'font-mono', 'text-sm', 'bg-base-200', 'p-2', 'rounded');
        requisitesElement.innerHTML = requisitesHTML;
        requisitesContainer.appendChild(requisitesElement);
    }
}

function manageForms(actionType, dataset) {
    const approveForm = document.getElementById('approve-form');
    const rejectForm = document.getElementById('reject-form');
    
    approveForm.classList.add('hidden');
    rejectForm.classList.add('hidden');
    
    switch (actionType) {
        case 'approve':
            approveForm.action = `/manager/approve_transaction/${dataset.transactionId}/${dataset.transactionPartnerId}`;
            approveForm.classList.remove('hidden');
            break;
        case 'reject':
            rejectForm.action = `/manager/reject_transaction/${dataset.transactionId}/${dataset.transactionPartnerId}`;
            rejectForm.classList.remove('hidden');
            break;
        case 'details':
            break;
    }
}