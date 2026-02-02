export function setupModals() {
    const detailButtons = document.querySelectorAll('.show_platform_details');

    const approvePlatformBtns = document.querySelectorAll('.approve_platform');
    const rejectPlatformBtns = document.querySelectorAll('.reject_platform');

    const approveModerationForm = document.getElementById('approve-moderation-form');
    const rejectModerationForm = document.getElementById('reject-moderation-form');

    const modal = document.getElementById('detailsModal');

    function showDetailsModal(element) {
        const data = element.dataset;
        
        document.getElementById('modalTitle').textContent = data.name || `Площадка #${data.id}`;
        document.getElementById('modalType').textContent = 'Площадка';
        document.getElementById('modalPlatformType').textContent = data.platformType;

        const statusEl = document.getElementById('modalStatus');
        statusEl.textContent = data.status || 'На модерации';
        statusEl.className = 'badge badge-lg ' + (
            data.status === 'Одобрено' ? 'badge-success' : 
            data.status === 'Отклонено' ? 'badge-error' : 'badge-warning'
        );
        
        
        document.getElementById('modalContactEmail').textContent = data.email || 'Не указан';
        
        document.getElementById('modalDescription').textContent = data.description || 'Описание отсутствует';
                
        modal.showModal();
    }

    function moderateModal(element) {
        const data = element.dataset;
        if(data.actionType == 'reject')
        {
            rejectModerationForm.classList.remove('hidden');
            approveModerationForm.classList.add('hidden');
            rejectModerationForm.action = `/manager/reject_platform/${data.id}`;
        } else if(data.actionType == 'approve') {
            rejectModerationForm.classList.add('hidden');
            approveModerationForm.classList.remove('hidden');
            approveModerationForm.action = `/manager/approve_platform/${data.id}`;
        }
        showDetailsModal(element);
    }

    detailButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            showDetailsModal(this);
        });
    });

    approvePlatformBtns.forEach(btn => {
        btn.addEventListener('click',function(){
            moderateModal(this);
        })
    });

    rejectPlatformBtns.forEach(btn => {
        btn.addEventListener('click',function(){
            moderateModal(this);
        })
    });
}