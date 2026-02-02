export function setupEditPlatformModal() {
  const editPlatformBtns = document.querySelectorAll('.edit-platform-btn');
  const editPlatformModal = document.getElementById('edit_platform_modal');
  const editPlatformForm = document.getElementById('edit_platform_form');

  const editPlatformName = document.getElementById('EditPlatformName');
  const editPlatformType = document.getElementById('EditPlatformType');
  const editPlatformDescription = document.getElementById('EditPlatformDescription');
  const editPlatformURL = document.getElementById('EditPlatformURL');
  const editPlatformActive = document.getElementById('editPlatformActive');

  editPlatformBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const dataset = this.dataset;
      editPlatformName.value = dataset.platformName || '';

      editPlatformType.value = dataset.platformType || '';
      for (let i = 0; i < editPlatformType.options.length; i++) {
        if (editPlatformType.options[i].text === dataset.platformType) {
          editPlatformType.selectedIndex = i;
        }
      }


      editPlatformDescription.value = dataset.platformDescription || '';
      editPlatformURL.value = dataset.platformUrl || '';
      editPlatformActive.checked = dataset.platformIsActive === 'True'

      editPlatformForm.action = `/partner/edit_platform/${dataset.platformId}`
      editPlatformModal.showModal();
    })
  })
}