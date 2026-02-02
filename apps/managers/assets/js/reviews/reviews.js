import '@fortawesome/fontawesome-free/js/all'
import '/apps/managers/assets/css/manager.css'


function publishReview(reviewId) {
    const modal = document.getElementById('confirm_modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const confirmButton = document.getElementById('confirm-button');
    const confirmForm = document.getElementById('confirm_form');

    modalTitle.textContent = 'Одобрить отзыв';
    modalMessage.textContent = 'Вы уверены, что хотите одобрить этот отзыв? Он будет опубликован на сайте.';
    confirmButton.innerHTML = '<i class="fas fa-check mr-2"></i>Одобрить';
    confirmButton.className = 'btn btn-success ml-2';
    confirmForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const response = await fetch(`/manager/publish_review/${reviewId}`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            console.error('Server error:', response.status, response.statusText);
            return;
        }

        const result = await response.json();
        showNotification('Отзыв одобрен и опубликован', 'success');
        modal.close();
    })

    modal.showModal();
}

function deleteReview(reviewId) {
    const modal = document.getElementById('confirm_modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const confirmButton = document.getElementById('confirm-button');
    const confirmForm = document.getElementById('confirm_form');

    modalTitle.textContent = 'Отклонить отзыв';
    modalMessage.textContent = 'Вы уверены, что хотите отклонить этот отзыв? Это действие нельзя будет отменить.';
    confirmButton.innerHTML = '<i class="fas fa-times mr-2"></i>Отклонить';
    confirmButton.className = 'btn btn-error ml-2';
    confirmForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData(e.target);
        const response = await fetch(`/manager/remove_review/${reviewId}`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            showNotification('Ошибка сервера','error')
            console.error('Server error:', response.status, response.statusText);
            return;
        }

        const result = await response.json();
        showNotification('Отзыв отклонен', 'error');
        modal.close();
    });

    modal.showModal();
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} fixed top-4 right-4 z-50 max-w-md shadow-lg`;
    notification.innerHTML = `
                <div>
                    <span>${message}</span>
                </div>
                <button class="btn btn-sm btn-ghost" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;

    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}



function setupSaveChanges() {
    const forms = document.querySelectorAll('.edit_review');
    forms.forEach(form => {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const reviewId = form.querySelector('.save-changes').dataset.reviewId;
            const data = new FormData(form);
            const response = await fetch(`/manager/edit_review/${reviewId}`, {
                method: "POST",
                body: data
            });

            if (!response.ok) {
                showNotification('Ошибка сервера','error')
                console.error('Server error:', response.status, response.statusText);
                return;
            }

            const result = await response.json();
            showNotification('Изменения сохранены!');

        })
    })
}

function setupChangeComment() {
    const reviewComments = document.querySelectorAll('.review-textarea');
    reviewComments.forEach(review => {
        review.addEventListener('change', function () {
            const reviewItem = review.closest('.review-item');
            const reviewInput = reviewItem.querySelector('.review_comment');
            reviewInput.value = review.value;
        });
        review.addEventListener('input', function () {
            const reviewItem = review.closest('.review-item');
            const reviewInput = reviewItem.querySelector('.review_comment');
            reviewInput.value = review.value;
        });
    })
}

function setupPublish() {
    const buttons = document.querySelectorAll('.publish-review');
    buttons.forEach(btn => {
        btn.addEventListener('click', async function () {
            publishReview(this.dataset.reviewId);
        })
    })
}

function setupDelete() {
    const buttons = document.querySelectorAll('.remove-review');
    buttons.forEach(btn => {
        btn.addEventListener('click', async function () {
            deleteReview(this.dataset.reviewId);
        })
    })
}

document.addEventListener('DOMContentLoaded', function () {
    setupSaveChanges();
    setupChangeComment();
    setupPublish();
    setupDelete();
});