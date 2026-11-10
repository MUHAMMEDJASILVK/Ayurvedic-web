// Kerala Ayurveda Store - E-Commerce Interactivity

document.addEventListener('DOMContentLoaded', function () {
  initSearchAutocomplete();
  initAddToCartButtons();
  initOtpTimer();
  initPaymentMethodSelector();
  initQuickRestock();
});

// Toast Helper
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>🌿</span> <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Get CSRF Token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 1. Search Autocomplete (Amazon style)
function initSearchAutocomplete() {
  const searchInput = document.getElementById('header-search-input');
  const suggestionsBox = document.getElementById('search-suggestions-box');
  if (!searchInput || !suggestionsBox) return;

  let debounceTimer;
  searchInput.addEventListener('input', function () {
    clearTimeout(debounceTimer);
    const q = this.value.trim();
    if (q.length < 2) {
      suggestionsBox.style.display = 'none';
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/search-suggest/?q=${encodeURIComponent(q)}`)
        .then(res => res.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            suggestionsBox.innerHTML = data.results.map(item => `
              <a href="${item.url}" class="suggestion-item">
                <div>
                  <div class="suggestion-title">${item.title}</div>
                  <div class="suggestion-sub">${item.subtitle}</div>
                </div>
                <span class="suggestion-tag">${item.type}</span>
              </a>
            `).join('');
            suggestionsBox.style.display = 'block';
          } else {
            suggestionsBox.style.display = 'none';
          }
        })
        .catch(() => {
          suggestionsBox.style.display = 'none';
        });
    }, 200);
  });

  // Close when clicking outside
  document.addEventListener('click', function (e) {
    if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
      suggestionsBox.style.display = 'none';
    }
  });
}

// 2. AJAX Add to Cart
function initAddToCartButtons() {
  document.querySelectorAll('.ajax-add-cart-form').forEach(form => {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const submitBtn = this.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Adding...';

      const formData = new FormData(this);
      const url = this.getAttribute('action');

      fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(res => res.json())
      .then(data => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        if (data.status === 'success') {
          showToast(data.message, 'success');
          // Update cart badge
          const badges = document.querySelectorAll('.cart-count-badge');
          badges.forEach(b => {
            b.textContent = data.cart_count;
            b.style.transform = 'scale(1.3)';
            setTimeout(() => { b.style.transform = 'scale(1)'; }, 200);
          });
        } else {
          showToast(data.message || 'Could not add to cart.', 'error');
        }
      })
      .catch(err => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        showToast('Error connecting to server.', 'error');
      });
    });
  });
}

// 3. OTP Countdown Timer (for verify_otp.html)
function initOtpTimer() {
  const timerElem = document.getElementById('otp-timer');
  const resendBtn = document.getElementById('btn-resend-otp');
  if (!timerElem || !resendBtn) return;

  let timeLeft = 60;
  resendBtn.style.pointerEvents = 'none';
  resendBtn.style.opacity = '0.5';

  const countdown = setInterval(() => {
    timeLeft--;
    timerElem.textContent = `${timeLeft}s`;
    if (timeLeft <= 0) {
      clearInterval(countdown);
      timerElem.textContent = '';
      resendBtn.style.pointerEvents = 'auto';
      resendBtn.style.opacity = '1';
      resendBtn.innerHTML = 'Resend OTP Now';
    }
  }, 1000);

  resendBtn.addEventListener('click', function (e) {
    e.preventDefault();
    resendBtn.style.pointerEvents = 'none';
    resendBtn.style.opacity = '0.5';
    resendBtn.innerHTML = 'Sending new OTP...';

    fetch('/accounts/resend-otp/', {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => res.json())
    .then(data => {
      showToast(data.message || 'Fresh OTP codes sent to your registered Email & Phone!', 'success');
      timeLeft = 60;
      initOtpTimer();
    })
    .catch(() => {
      window.location.href = '/accounts/resend-otp/';
    });
  });
}

// 4. Payment Method Selector on Checkout
function initPaymentMethodSelector() {
  const paymentInputs = document.querySelectorAll('input[name="payment_method"]');
  const paymentPanels = document.querySelectorAll('.payment-tab-content');
  if (paymentInputs.length === 0) return;

  paymentInputs.forEach(input => {
    input.addEventListener('change', function () {
      paymentPanels.forEach(p => p.style.display = 'none');
      const targetPanel = document.getElementById(`panel-${this.value}`);
      if (targetPanel) {
        targetPanel.style.display = 'block';
      }
    });
  });
}

// 5. Quick Restock Modal / Action for Inventory Manager
function initQuickRestock() {
  document.querySelectorAll('.btn-quick-restock').forEach(btn => {
    btn.addEventListener('click', function () {
      const prodId = this.dataset.productId;
      const prodName = this.dataset.productName;
      const addQty = prompt(`Enter number of units to add to inventory for "${prodName}":`, "25");
      if (addQty && !isNaN(addQty) && parseInt(addQty) > 0) {
        const formData = new FormData();
        formData.append('action_type', 'add');
        formData.append('quantity', addQty);
        formData.append('remarks', 'Quick Restock via Seller Dashboard');

        fetch(`/inventory/stock/update/${prodId}/`, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
          }
        })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            showToast(data.message, 'success');
            const stockCell = document.getElementById(`stock-val-${prodId}`);
            if (stockCell) stockCell.textContent = data.new_stock;
          } else {
            showToast(data.message || 'Failed to update stock.', 'error');
          }
        })
        .catch(() => showToast('Error updating stock.', 'error'));
      }
    });
  });
}
