document.addEventListener("DOMContentLoaded", function () {
  const quantityInput = document.getElementById("quantity");
  const hiddenQuantityInput = document.getElementById("hidden-quantity");

  document
    .getElementById("increase-quantity")
    .addEventListener("click", function () {
      let quantity = parseInt(quantityInput.value);
      quantityInput.value = quantity + 1;
      hiddenQuantityInput.value = quantity + 1;
    });

  document
    .getElementById("decrease-quantity")
    .addEventListener("click", function () {
      let quantity = parseInt(quantityInput.value);
      if (quantity > 1) {
        quantityInput.value = quantity - 1;
        hiddenQuantityInput.value = quantity - 1;
      }
    });
});
