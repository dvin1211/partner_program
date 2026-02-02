export function setupPlatformAdd(){
  const btnAddPlatform = document.getElementById("btn-add-platform");
  const btnCloseModal = document.getElementById("btn-close-add-platform-modal");
  const btnCloseModalBackground = document.getElementById("btn-close-add-platform-modal-background");
  const modal = document.getElementById("modal-add-platform");

  btnAddPlatform.addEventListener("click", () => {
    modal.classList.add("modal-open");
  });

  btnCloseModal.addEventListener("click", () => {
    modal.classList.remove("modal-open");
  });
  btnCloseModalBackground.addEventListener("click",()=>{
    modal.classList.remove("modal-open");
  })
}