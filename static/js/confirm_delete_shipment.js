const modal = document.getElementById("confirmModal");
const form = document.getElementById("confirmDeleteForm");
const nameSpan = document.getElementById("productName");

function openConfirmModal(button) {
  const itemId = button.dataset.id;
  const productName = button.dataset.name;

  nameSpan.textContent = productName;
  form.action = `/shipments/${itemId}/delete/`;

  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeConfirmModal() {
  modal.classList.remove("flex");
  modal.classList.add("hidden");
}
