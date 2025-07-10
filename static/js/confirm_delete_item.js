const modal = document.getElementById("confirmModal");
const form = document.getElementById("confirmDeleteForm");
const nameSpan = document.getElementById("productName");


function openConfirmModal(element) {
  const itemId = element.dataset.id;
  const productName = element.dataset.name;

  nameSpan.textContent = productName;
  form.action = `/shipments/item/${itemId}/delete/`;

  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function closeConfirmModal() {
  modal.classList.remove("flex");
  modal.classList.add("hidden");
}
