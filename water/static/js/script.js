$('#reg-modal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
})


function showTab(tabId) {
    let tabs = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].style.display = 'none';
    }
    document.getElementById(tabId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    showTab('order');
});

document.addEventListener('DOMContentLoaded', function () {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    function updateCartBadge() {
        const cartItemCount = document.getElementById('cartItemCount');
        if (!cartItemCount) {
            console.error('Cart item count element not found.');
            return;
        }

        const itemCount = cart.reduce((total, item) => total + item.quantity, 0);
        cartItemCount.textContent = itemCount.toString();

        cartItemCount.style.display = itemCount > 0 ? 'inline-block' : 'none';
    }

    function updateCartDropdown() {
        const cartDropdown = document.getElementById('cartDropdown');
        if (!cartDropdown) {
            console.error('Cart dropdown element not found.');
            return;
        }

        cartDropdown.innerHTML = '';

        if (cart.length === 0) {
            cartDropdown.innerHTML = `
                <li><a class="dropdown-item" href="#">Your Cart is Empty</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><button class="dropdown-item" id="orderButton">Make an Order</button></li>
            `;
        } else {
            let totalPrice = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

            cart.forEach((item, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'd-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    <a class="dropdown-item" href="#">
                        ${item.name} - ${item.price} TL x ${item.quantity}
                        <div class="btn-group ms-2">
                            <button class="btn btn-outline-secondary btn-sm btn-decrease" data-index="${index}">-</button>
                            <button class="btn btn-outline-secondary btn-sm btn-increase" data-index="${index}">+</button>
                        </div>
                    </a>
                `;
                cartDropdown.appendChild(listItem);
            });

            const totalItem = document.createElement('li');
            totalItem.innerHTML = `<a class="dropdown-item" href="#">Total: ${totalPrice.toFixed(2)} TL</a>`;
            cartDropdown.appendChild(totalItem);

            const divider = document.createElement('li');
            divider.innerHTML = '<hr class="dropdown-divider">';
            cartDropdown.appendChild(divider);

            const orderButton = document.createElement('li');
            const button = document.createElement('button');
            button.className = 'dropdown-item';
            button.id = 'orderButton';
            button.innerText = 'Make an Order';
            orderButton.appendChild(button);
            cartDropdown.appendChild(orderButton);

            const clearCartButton = document.createElement('li');
            const clearButton = document.createElement('button');
            clearButton.className = 'dropdown-item';
            clearButton.id = 'clearCartButton';
            clearButton.innerText = 'Clear Cart';
            clearCartButton.appendChild(clearButton);
            cartDropdown.appendChild(clearCartButton);
        }

        updateCartBadge();

        document.querySelectorAll('.btn-decrease').forEach(button => {
            button.addEventListener('click', function (event) {
                const index = parseInt(button.getAttribute('data-index'), 10);
                event.stopPropagation();
                if (index >= 0 && index < cart.length) {
                    cart[index].quantity -= 1;

                    if (cart[index].quantity <= 0) {
                        cart.splice(index, 1);
                    }

                    localStorage.setItem('cart', JSON.stringify(cart));
                    updateCartDropdown();
                }
            });
        });

        document.querySelectorAll('.btn-increase').forEach(button => {
            button.addEventListener('click', function (event) {
                const index = parseInt(button.getAttribute('data-index'), 10);
                event.stopPropagation();
                if (index >= 0 && index < cart.length) {
                    cart[index].quantity += 1;
                    localStorage.setItem('cart', JSON.stringify(cart));
                    updateCartDropdown();
                }
            });
        });

        document.getElementById('orderButton')?.addEventListener('click', function () {
            localStorage.setItem('cart', JSON.stringify(cart));
            window.location.href = '/order';
        });

        document.getElementById('clearCartButton')?.addEventListener('click', function () {
            cart.length = 0;
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartDropdown();
        });
    }

    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function () {
            const productCard = button.closest('.product-card');
            if (!productCard) {
                console.error('Product card element not found.');
                return;
            }

            const productId = productCard.getAttribute('data-id');
            const productName = productCard.getAttribute('data-name');
            const productPrice = productCard.getAttribute('data-price');

            if (productId && productName && productPrice) {
                const existingProduct = cart.find(item => item.id === productId);
                if (existingProduct) {
                    existingProduct.quantity += 1;
                } else {
                    cart.push({
                        id: productId,
                        name: productName,
                        price: parseFloat(productPrice),
                        quantity: 1
                    });
                }

                localStorage.setItem('cart', JSON.stringify(cart));
                updateCartDropdown();
            } else {
                console.error('Product information is missing.');
            }
        });
    });

    updateCartDropdown();
});


document.addEventListener('DOMContentLoaded', function () {
    const orderList = document.getElementById('orderList');
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    function updateOrderList() {
        orderList.innerHTML = '';

        if (cart.length === 0) {
            orderList.innerHTML = '<li class="list-group-item">Your cart is empty.</li>';
        } else {
            let totalPrice = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

            cart.forEach((item, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    ${item.name} - ${item.price} TL x ${item.quantity}
                    <button class="btn btn-danger btn-sm ms-2" aria-label="Remove" data-index="${index}">Remove</button>
                `;
                orderList.appendChild(listItem);
            });

            const totalItem = document.createElement('li');
            totalItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            totalItem.innerHTML = `<strong>Total:</strong> ${totalPrice.toFixed(2)} TL`;
            orderList.appendChild(totalItem);

            const divider = document.createElement('li');
            divider.innerHTML = '<hr class="list-group-divider">';
            orderList.appendChild(divider);
        }

        document.querySelectorAll('.btn-danger').forEach(button => {
            button.addEventListener('click', function () {
                const index = parseInt(button.getAttribute('data-index'), 10);
                if (index >= 0 && index < cart.length) {
                    cart[index].quantity -= 1;

                    if (cart[index].quantity <= 0) {
                        cart.splice(index, 1);
                    }

                    localStorage.setItem('cart', JSON.stringify(cart));
                    updateOrderList();
                }
            });
        });
    }

    updateOrderList();

    document.getElementById('confirmOrderButton')?.addEventListener('click', function () {

        const storedData = JSON.parse(localStorage.getItem('cart') || '[]');

        const cartData = storedData.map(item => ({
            product_id: item.id,
            product_name: item.name,
            product_price: item.price,
            quantity: item.quantity || 1
        }));
        const totalPrice = cartData.reduce((total, item) => total + item.product_price * item.quantity, 0);

        fetch('/create-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                cart: cartData,
                total_price: totalPrice
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const orderSuccessMessage = document.getElementById('orderSuccessMessage');
                    orderSuccessMessage.classList.remove('d-none');
                    orderSuccessMessage.scrollIntoView();
                    localStorage.removeItem('cart');
                    updateOrderList();
                    setTimeout(() => {
                        window.location.href = '/user_dashboard';
                    }, 5000);
                } else {
                    alert('Error placing order: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
    document.getElementById('logoutForm').addEventListener('submit', function () {
        localStorage.removeItem('cart');
        updateOrderList();
    });
});


function showContent(contentId) {
    const contents = document.getElementsByClassName('dynamic-content');
    for (let i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }
    document.getElementById(contentId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('productForm');
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        const formData = new FormData(form);

        fetch("{% url 'add_product' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': String(formData.get('csrfmiddlewaretoken'))
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {

                    const modal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
                    modal.hide();
                    form.reset();

                    location.reload();
                } else {

                    alert('An error occurred while adding the product!');
                }
            })
            .catch(error => {
                console.error('Hata:', error);
            });
    });
});

