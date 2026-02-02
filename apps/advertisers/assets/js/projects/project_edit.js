export function setupProjectEdit() {
    const modal = document.getElementById('editProjectModal');
    const editButtons = document.querySelectorAll('.editProjectModal');

    editButtons.forEach(button => {
        button.addEventListener('click', () => {
            const projectData = {
                id: button.dataset.projectId,
                name: button.dataset.projectName,
                description: button.dataset.projectDescription,
                isActive: button.dataset.projectIsActive === 'true',
                actionName: button.dataset.projectActionName,
                costPerAction: button.dataset.projectCost.replace(',', '.'),
                reducedPrice: button.dataset.projectReducedPrice.replace(',', '.')
            };

            const formFields = {
                id: 'editProjectId',
                name: 'editProjectName',
                url: 'editProjectUrl',
                description: 'editProjectDescription',
                isActive: 'editProjectActive',
                actionName:'customActionNameInput',
                costPerAction: 'costPerActionInput'
            };

            document.getElementById(formFields.id).value = projectData.id;
            document.getElementById(formFields.name).value = projectData.name;
            document.getElementById(formFields.description).value = projectData.description;
            document.getElementById(formFields.isActive).checked = projectData.isActive;
            document.getElementById(formFields.actionName).value = projectData.actionName;
            document.getElementById(formFields.costPerAction).value = projectData.costPerAction;

            const reducedPrice = Math.max(Number(projectData.reducedPrice), 5);
            document.getElementById(formFields.costPerAction).min = reducedPrice;

            const form = document.getElementById('editProjectForm');
            form.action = `/advertiser/edit_project/${projectData.id}`;

            modal.showModal();
        });
    });
}
