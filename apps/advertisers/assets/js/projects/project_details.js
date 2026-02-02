export function setupProjectDetails() {
    const showProjectDetailsBtns = document.querySelectorAll('.showProjectDetailsModal');
    showProjectDetailsBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const projectData = this.dataset;

            document.getElementById('ProjectID').textContent = `ID проекта: ${projectData.projectId}`;
            document.getElementById('ProjectTitle').textContent = projectData.projectName;
            document.getElementById('ProjectDescription').textContent = projectData.projectDescription;
            document.getElementById('ProjectPartnersCount').textContent = projectData.projectPartnersCount;
            document.getElementById('ProjectTotalClicks').textContent = projectData.projectTotalClicks;
            document.getElementById('ActionName').textContent = projectData.projectActionName;
            document.getElementById('CostPerAction').textContent = projectData.projectCost + ' ₽';
            document.getElementById('ProjectUrl').textContent = projectData.projectUrl;
            document.getElementById('ProjectTemplateUrl').textContent = projectData.projectLinkTemplate;
            document.getElementById('ProjectConversion').textContent = projectData.projectConversionsPercent + '%';
            document.getElementById('ProjectTotalConversion').textContent = projectData.projectConversionCount;

            const statusBadge = document.getElementById('ProjectStatusBadge');
            const statusText = document.getElementById('ProjectStatusText');

            
            if (projectData.projectIsActive === 'true') {
                statusBadge.className = 'badge badge-accent';
                statusText.textContent = 'Активный';
            } else {
                statusBadge.className = 'badge badge-error';
                statusText.textContent = 'Неактивный';
            }

            document.getElementById('projectDetailsModal').showModal();
        });
    });


    const closeProjectBtn = document.getElementById('closeProjectDetailsModal');
    closeProjectBtn.addEventListener('click', () => {
        document.getElementById('projectDetailsModal').close();
    });
}