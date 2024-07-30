  $('#reg-modal').on('shown.bs.modal', function () {
    $('#myInput').trigger('focus')
  })




function showTab(tabId) {
  var tabs = document.getElementsByClassName('tab-content');
  for (var i = 0; i < tabs.length; i++) {
      tabs[i].style.display = 'none';
  }
  document.getElementById(tabId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
  showTab('order');
});

document.addEventListener('DOMContentLoaded', function() {
    // Sepeti tutacak bir dizi
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    function updateCartDropdown() {
        const cartDropdown = document.getElementById('cartDropdown');
        if (!cartDropdown) {
            console.error('Cart dropdown element not found.');
            return;
        }

        cartDropdown.innerHTML = '';  // Sepet içeriğini temizle

        if (cart.length === 0) {
            cartDropdown.innerHTML = `
                <li><a class="dropdown-item" href="#">Your Cart Empty</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><button class="dropdown-item" id="orderButton">Make an Order</button></li>
            `;
        } else {
            // Toplam fiyatı hesapla
            let totalPrice = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

            cart.forEach((item, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'd-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    <a class="dropdown-item" href="#">${item.name} - ${item.price} TL x ${item.quantity}</a>
                    <button class="btn btn-close btn-sm" aria-label="Remove" data-index="${index}"></button>
                `;
                cartDropdown.appendChild(listItem);
            });

            // Toplam fiyatı ekle
            const totalItem = document.createElement('li');
            totalItem.innerHTML = `<a class="dropdown-item" href="#">Total: ${totalPrice.toFixed(2)} TL</a>`;
            cartDropdown.appendChild(totalItem);

            // Divider ve "Sipariş Ver" butonunu ekle
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
        }

        // Remove buttons click event listener
        document.querySelectorAll('.btn-close').forEach(button => {
            button.addEventListener('click', function(event) {
                const index = parseInt(button.getAttribute('data-index'), 10);
                event.stopPropagation();
                if (index >= 0 && index < cart.length) {
                    // Ürünün miktarını bir azalt
                    cart[index].quantity -= 1;

                    // Eğer miktar 0 ise ürünü sepetten çıkar
                    if (cart[index].quantity <= 0) {
                        cart.splice(index, 1);
                    }

                    localStorage.setItem('cart', JSON.stringify(cart)); // Sepeti localStorage'a kaydet
                    updateCartDropdown();  // Sepeti güncelle
                }
            });
        });

        // Make an Order button click event listener
        document.getElementById('orderButton')?.addEventListener('click', function() {
            localStorage.setItem('cart', JSON.stringify(cart)); // Sepeti localStorage'a kaydet
            window.location.href = '/order'; // Sipariş sayfasına yönlendir
        });
    }

    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productCard = button.closest('.product-card');
            if (!productCard) {
                console.error('Product card element not found.');
                return;
            }

            const productId = productCard.getAttribute('data-id');
            const productName = productCard.getAttribute('data-name');
            const productPrice = productCard.getAttribute('data-price');

            if (productId && productName && productPrice) {
                // Aynı ürünü sepette bul ve miktarını artır
                const existingProduct = cart.find(item => item.id === productId);
                if (existingProduct) {
                    existingProduct.quantity += 1;
                } else {
                    // Ürün yeni ise sepete ekle
                    cart.push({
                        id: productId,
                        name: productName,
                        price: parseFloat(productPrice),  // Fiyatı sayıya dönüştür
                        quantity: 1 // İlk eklenme miktarı
                    });
                }

                // Sepeti localStorage'a kaydet ve güncelle
                localStorage.setItem('cart', JSON.stringify(cart));
                updateCartDropdown();
            } else {
                console.error('Product information is missing.');
            }
        });
    });

    // Sepeti güncellemek için ilk sefer
    updateCartDropdown();
});


document.addEventListener('DOMContentLoaded', function() {
    const orderList = document.getElementById('orderList');
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    // Sepeti güncelleme fonksiyonu
    function updateOrderList() {
        orderList.innerHTML = ''; // Önceki içerikleri temizle

        if (cart.length === 0) {
            orderList.innerHTML = '<li class="list-group-item">Your cart is empty.</li>';
        } else {
            // Toplam fiyatı hesapla
            let totalPrice = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

            // Ürünleri listele
            cart.forEach((item, index) => {
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                listItem.innerHTML = `
                    ${item.name} - ${item.price} TL x ${item.quantity}
                    <button class="btn btn-danger btn-sm ms-2" aria-label="Remove" data-index="${index}">Remove</button>
                `;
                orderList.appendChild(listItem);
            });

            // Toplam fiyatı ekle
            const totalItem = document.createElement('li');
            totalItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            totalItem.innerHTML = `<strong>Total:</strong> ${totalPrice.toFixed(2)} TL`;
            orderList.appendChild(totalItem);

            // Divider
            const divider = document.createElement('li');
            divider.innerHTML = '<hr class="list-group-divider">';
            orderList.appendChild(divider);
        }

        // Çıkarma butonlarına event listener ekle
        document.querySelectorAll('.btn-danger').forEach(button => {
            button.addEventListener('click', function(event) {
                const index = parseInt(button.getAttribute('data-index'), 10);
                if (index >= 0 && index < cart.length) {
                    // Ürünün miktarını bir azalt
                    cart[index].quantity -= 1;

                    // Eğer miktar 0 ise ürünü sepetten çıkar
                    if (cart[index].quantity <= 0) {
                        cart.splice(index, 1);
                    }

                    localStorage.setItem('cart', JSON.stringify(cart)); // Sepeti localStorage'a kaydet
                    updateOrderList();  // Sepeti güncelle
                }
            });
        });
    }

    // İlk seferde listeyi güncelle
    updateOrderList();

    // Confirm Order button click event listener
    document.getElementById('confirmOrderButton')?.addEventListener('click', function() {

        const storedData = JSON.parse(localStorage.getItem('cart') || '[]');

        const cartData = storedData.map(item => ({
            product_id: item.id,
            product_name: item.name,
            product_price: item.price,
            quantity: item.quantity || 1 // Eğer quantity verisi yoksa varsayılan olarak 1 kullan
        }));
        const totalPrice = cartData.reduce((total, item) => total + item.product_price * item.quantity, 0);

        // Form verilerini POST edin
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
                var orderSuccessMessage = document.getElementById('orderSuccessMessage');
                orderSuccessMessage.classList.remove('d-none');
                orderSuccessMessage.scrollIntoView();
                // Sepeti temizle
                localStorage.removeItem('cart');
                // Sepeti güncelle
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
});

document.getElementById('logoutForm').addEventListener('submit', function() {
    localStorage.removeItem('cart');
    updateOrderList();
});

function showContent(contentId) {
    var contents = document.getElementsByClassName('dynamic-content');
    for (var i = 0; i < contents.length; i++) {
        contents[i].style.display = 'none';
    }
    document.getElementById(contentId).style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('productForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Formun normal submit işlemini engelle
        var formData = new FormData(form);

        fetch("{% url 'add_product' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Modalı kapat ve formu sıfırla
                var modal = bootstrap.Modal.getInstance(document.getElementById('productModal'));
                modal.hide();
                form.reset();
                // Ürün listesini güncelle (isteğe bağlı)
                location.reload();  // Tüm sayfayı yenile
            } else {
                // Hata mesajını göster
                alert('Ürün eklenirken bir hata oluştu!');
            }
        })
        .catch(error => {
            console.error('Hata:', error);
        });
    });
});

