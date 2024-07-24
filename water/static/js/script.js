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
          cartDropdown.innerHTML = '<li><a class="dropdown-item" href="#">Sepet boş</a></li><li><hr class="dropdown-divider"></li><li><button class="dropdown-item" id="orderButton">Sipariş Ver</button></li>';
      } else {
          cart.forEach(item => {
              const listItem = document.createElement('li');
              listItem.innerHTML = `<a class="dropdown-item" href="#">${item.name} - ${item.price} TL</a>`;
              cartDropdown.insertBefore(listItem, cartDropdown.querySelector('li:last-child'));
          });
          
          // Divider ve "Sipariş Ver" butonunu yeniden ekle
          const divider = document.createElement('li');
          divider.innerHTML = '<hr class="dropdown-divider">';
          cartDropdown.appendChild(divider);

          const orderButton = document.createElement('li');
          const button = document.createElement('button');
          button.className = 'dropdown-item';
          button.id = 'orderButton';
          button.innerText = 'Sipariş Ver';
          orderButton.appendChild(button);
          cartDropdown.appendChild(orderButton);
      }
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

          // Ürün bilgilerini bir obje olarak sepete ekleyin
          cart.push({
              id: productId,
              name: productName,
              price: productPrice
          });

          // Sepeti güncelle
          updateCartDropdown();
      });
  });

  // Sepeti güncellemek için ilk sefer
  updateCartDropdown();
});
