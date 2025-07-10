const categorySelect = document.getElementById("id_category");
const productSelect = document.getElementById("id_product");

categorySelect.addEventListener("change", async function () {
  const categoryId = this.value;

  // Reset the product dropdown
  productSelect.innerHTML = '<option value="">Select product</option>';

  try {
    const response = await fetch(
      `/shipments/api/products/?category_id=${categoryId}`
    );
    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.json();

    data.forEach((product) => {
      const option = document.createElement("option");
      option.value = product.id;
      option.textContent = product.name;
      productSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Error fetching products:", error);
  }
});
