document.addEventListener('DOMContentLoaded', function () {
    const productSelect = document.getElementById('searchbox_products');
    const productTableBody = document.querySelector('#table_products tbody');
    const subTotalInput = document.getElementById('sub_total');
    const taxPercentageInput = document.getElementById('tax_percentage');
    const taxAmountInput = document.getElementById('tax_amount');
    const grandTotalInput = document.getElementById('grand_total');
    const amountPayedInput = document.getElementById('amount_payed');
    const amountChangeInput = document.getElementById('amount_change');
    const form = document.querySelector('.saleForm');

    let productIndex = 0;
    let selectedProducts = [];

    // Handle product selection
    function handleProductSelection() {
        const selectedOption = productSelect.options[productSelect.selectedIndex];
        const productId = selectedOption.value;
        const productName = selectedOption.getAttribute('data-name');
        const productVolume = selectedOption.getAttribute('data-volume');
        const productPrice = parseFloat(selectedOption.getAttribute('data-price'));

        if (productId && !selectedProducts.includes(productId)) {
            selectedProducts.push(productId);
            addProductRow(productId, productName, productVolume, productPrice);
            updateTotals();
        }
    }

    // Add new product row to the table
    function addProductRow(productId, productName, productVolume, productPrice) {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${++productIndex}</td>
            <td>${productName}</td>
            <td>${productVolume}</td>
            <td>${productPrice.toFixed(2)}</td>
            <td><input type="number" class="form-control quantity-input" value="1" min="1" data-price="${productPrice}" data-product-id="${productId}"></td>
            <td class="product-total">${productPrice.toFixed(2)}</td>
            <td class="text-center"><button type="button" class="btn btn-danger btn-sm delete-product" data-product-id="${productId}"><i class="fas fa-trash-alt"></i></button></td>
        `;
        productTableBody.appendChild(newRow);
    }

    // Update totals when quantity or tax percentage changes
    function updateTotals() {
        let subtotal = 0;
        document.querySelectorAll('.product-total').forEach(totalCell => {
            subtotal += parseFloat(totalCell.textContent);
        });
        subTotalInput.value = subtotal.toFixed(2);

        const taxPercentage = parseFloat(taxPercentageInput.value) || 0;
        const taxAmount = subtotal * (taxPercentage / 100);
        taxAmountInput.value = taxAmount.toFixed(2);

        const grandTotal = subtotal + taxAmount;
        grandTotalInput.value = grandTotal.toFixed(2);

        const amountPayed = parseFloat(amountPayedInput.value) || 0;
        const amountChange = amountPayed - grandTotal;
        amountChangeInput.value = amountChange.toFixed(2);
    }

    // Update individual product total when quantity changes
    function updateProductTotal(input) {
        const price = parseFloat(input.getAttribute('data-price'));
        const quantity = Math.max(parseInt(input.value), 1); // Prevent invalid quantities
        const productTotal = price * quantity;
        input.closest('tr').querySelector('.product-total').textContent = productTotal.toFixed(2);
    }

    // Remove product when delete button is clicked
    function removeProduct(e) {
        if (e.target.closest('.delete-product')) {
            const productId = e.target.closest('.delete-product').getAttribute('data-product-id');
            selectedProducts = selectedProducts.filter(id => id !== productId);
            e.target.closest('tr').remove();
            updateTotals();
        }
    }

    // Add hidden product data to the form on submit
    function addProductDataToForm(event) {
        const grandTotal = parseFloat(grandTotalInput.value);
        const amountPayed = parseFloat(amountPayedInput.value) || 0;

        if (amountPayed < grandTotal) {
            event.preventDefault(); // Prevent form submission
            alert('The paid amount must be equal to or greater than the total amount.');
            return false;
        }

        // Remove existing hidden product inputs
        document.querySelectorAll('input[name="products"]').forEach(input => input.remove());

        // Add new hidden inputs with product data
        selectedProducts.forEach(productId => {
            const row = Array.from(productTableBody.querySelectorAll('tr')).find(row =>
                row.querySelector('.delete-product').getAttribute('data-product-id') === productId
            );
            const quantity = parseInt(row.querySelector('.quantity-input').value);
            const price = parseFloat(row.querySelector('.product-total').textContent) / quantity;
            const totalProduct = parseFloat(row.querySelector('.product-total').textContent);

            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'products';
            input.value = JSON.stringify({
                id: productId,
                price: price,
                quantity: quantity,
                total_product: totalProduct
            });
            form.appendChild(input);
        });
    }

    // Event Listeners
    productSelect.addEventListener('change', handleProductSelection);
    productTableBody.addEventListener('input', function (e) {
        if (e.target.classList.contains('quantity-input')) {
            updateProductTotal(e.target);
            updateTotals();
        }
    });
    productTableBody.addEventListener('click', removeProduct);
    taxPercentageInput.addEventListener('input', updateTotals);
    amountPayedInput.addEventListener('keyup', updateTotals);
    form.addEventListener('submit', addProductDataToForm);
});
