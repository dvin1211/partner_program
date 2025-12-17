export function setupDeletePartnerLinkModal() {
    const DeletePartnerLinkModal = document.getElementById('delete-partner-link-modal');
    const deletePartnerLinkForm = document.getElementById('delete-partner-link-form');
    const deletePartnerLinkBtns = document.querySelectorAll('.delete_generated_link');
    deletePartnerLinkBtns.forEach(btn => {
      btn.addEventListener('click', function(){
        deletePartnerLinkForm.action = `/partner/delete_partner_link/${this.dataset.linkId}`
        DeletePartnerLinkModal.showModal();
      })
    })
  }