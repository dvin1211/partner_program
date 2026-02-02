export function setupModals() {
    const detailButtons = document.querySelectorAll('.show_project_details');

    const approveProjectBtns = document.querySelectorAll('.approve_project');
    const rejectProjectBtns = document.querySelectorAll('.reject_project');

    const approveModerationForm = document.getElementById('approve-moderation-form');
    const rejectModerationForm = document.getElementById('reject-moderation-form');

    const modal = document.getElementById('detailsModal');

    function showDetailsModal(element) {
        const data = element.dataset;

        document.getElementById('modalTitle').textContent = data.name || `Проект #${data.id}`;
        document.getElementById('modalType').textContent = 'Проект';

        const statusEl = document.getElementById('modalStatus');
        statusEl.textContent = data.status || 'На модерации';
        statusEl.className = 'badge badge-lg ' + (
            data.status === 'Одобрено' ? 'badge-success' :
                data.status === 'Отклонено' ? 'badge-error' : 'badge-warning'
        );

        document.getElementById('modalContactEmail').textContent = data.email || 'Не указан';
        document.getElementById('modalAdvertiserContainer').classList.remove('hidden');
        document.getElementById('modalProjectDetails').classList.remove('hidden');

        document.getElementById('modalAdvertiser').textContent = data.owner || 'Не указан';
        document.getElementById('modalCost').textContent = `${data.cost} ₽` || 'Не указана';

        // Описание
        document.getElementById('modalDescription').textContent = data.description || 'Описание отсутствует';

        modal.showModal();
    }

    function moderateModal(element) {
        const data = element.dataset;
        if (data.actionType == 'reject') {
            rejectModerationForm.classList.remove('hidden');
            approveModerationForm.classList.add('hidden');
            rejectModerationForm.action = `/manager/reject_project/${data.id}`;
        } else if (data.actionType == 'approve') {
            approveModerationForm.classList.remove('hidden')
            rejectModerationForm.classList.add('hidden');
            approveModerationForm.action = `/manager/approve_project/${data.id}`;
        }
        showDetailsModal(element);
    }

    detailButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            showDetailsModal(this);
        });
    });

    approveProjectBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            moderateModal(this);
        })
    });
    
    rejectProjectBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            moderateModal(this);
        })
    });
}