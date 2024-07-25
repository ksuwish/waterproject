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
  const cart = [];  // Sepeti tutacak bir dizi

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
          let totalPrice = cart.reduce((total, item) => total + parseFloat(item.price), 0);

          cart.forEach((item, index) => {
              const listItem = document.createElement('li');
              listItem.className = 'd-flex justify-content-between align-items-center';
              listItem.innerHTML = `
                <a class="dropdown-item" href="#">${item.name} - ${item.price} TL</a>
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
              event.stopPropagation(); // Tıklama olayını yayılmayı durdurur
              const index = parseInt(button.getAttribute('data-index'), 10);
              if (index >= 0 && index < cart.length) {
                  cart.splice(index, 1);  // Ürünü sepetten çıkar
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
              // Ürün bilgilerini bir obje olarak sepete ekleyin
              cart.push({
                  id: productId,
                  name: productName,
                  price: parseFloat(productPrice)  // Fiyatı sayıya dönüştür
              });

              // Sepeti güncelle
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

  if (cart.length === 0) {
      orderList.innerHTML = '<li class="list-group-item">Your cart is empty.</li>';
  } else {
      cart.forEach(item => {
          const listItem = document.createElement('li');
          listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
          listItem.innerHTML = `${item.name} - ${item.price} TL`;
          orderList.appendChild(listItem);
      });
  }

  // Confirm Order button click event listener
  document.getElementById('confirmOrderButton').addEventListener('click', function() {
      // Siparişi işleme kodunu buraya ekleyebilirsiniz
      alert('Order confirmed!'); // Örneğin, kullanıcıya onay mesajı gösterilebilir
      localStorage.removeItem('cart'); // Sepeti temizle
      window.location.href = '/user_dashboard'; // Ana sayfaya dön
  });
});



document.getElementById('orderButton')?.addEventListener('click', function() {
  // Sepeti JSON formatında alın
  const cartData = JSON.stringify(cart);

  // Form verilerini POST edin
  fetch('/create-order/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: new URLSearchParams({
          'cart': cartData
      })
  })
  .then(response => response.json())
  .then(data => {
      if (data.error) {
          alert(data.error);
      } else {
          window.location.href = '/user_dashboard'; // Sipariş tamamlandıktan sonra yönlendirme
      }
  })
  .catch(error => console.error('Error:', error));
});