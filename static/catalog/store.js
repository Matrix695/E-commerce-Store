const menuButton = document.querySelector('.menu-toggle');
const siteNav = document.querySelector('.site-nav');

menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  siteNav?.classList.toggle('is-open', !isOpen);
});

const updateBagCounts = (count) => {
  const numericCount = Number.isFinite(Number(count)) ? Number(count) : 0;

  document.querySelectorAll('.bag-link .bag-count').forEach((badge) => {
    badge.textContent = String(numericCount);
  });

  const bagLink = document.querySelector('.bag-link');
  if (bagLink) {
    bagLink.setAttribute('aria-label', `Shopping bag, ${numericCount} items`);
  }
};

let bagNotificationTimeout;
let bagNotificationHideTimeout;

const showBagNotification = (message, count) => {
  const notification = document.querySelector('.bag-notification');
  if (!notification) return;

  const itemCount = Number.isFinite(Number(count)) ? Number(count) : 0;
  notification.querySelector('.bag-notification-message').textContent = message;
  notification.querySelector('.bag-notification-count').textContent = `${itemCount} ${itemCount === 1 ? 'item' : 'items'} in your bag`;

  window.clearTimeout(bagNotificationTimeout);
  window.clearTimeout(bagNotificationHideTimeout);
  notification.hidden = false;
  notification.classList.remove('is-visible');
  window.requestAnimationFrame(() => notification.classList.add('is-visible'));

  bagNotificationTimeout = window.setTimeout(() => {
    notification.classList.remove('is-visible');
    bagNotificationHideTimeout = window.setTimeout(() => {
      notification.hidden = true;
    }, 220);
  }, 3200);
};

const updateFavoriteCounts = (count) => {
  const numericCount = Number.isFinite(Number(count)) ? Number(count) : 0;
  const likedLink = document.querySelector('.liked-link');
  if (!likedLink) return;

  let badge = likedLink.querySelector('.favorite-count');
  if (numericCount > 0) {
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'bag-count favorite-count';
      likedLink.append(' ', badge);
    }
    badge.textContent = String(numericCount);
  } else {
    badge?.remove();
  }
};

document.querySelectorAll('.favorite-toggle-form').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const button = form.querySelector('.favorite-toggle');
    const productName = button.dataset.productName || 'Item';
    const formData = new FormData(form);
    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
      });

      const data = await response.json().catch(() => ({}));
      if (response.ok && data.success) {
        button.classList.toggle('is-active', data.is_favorite);
        button.querySelector('span').textContent = data.is_favorite ? '♥' : '♡';
        button.setAttribute(
          'aria-label',
          `${data.is_favorite ? 'Remove' : 'Add'} ${productName} ${data.is_favorite ? 'from' : 'to'} liked items`,
        );
        updateFavoriteCounts(data.favorite_count);
        return;
      }
    } catch (error) {
      console.warn('Like update failed, falling back to normal navigation.', error);
    }

    form.submit();
  });
});

document.querySelectorAll('.cart-form, .detail-add').forEach((form) => {
  const checkoutLink = form.closest('.bag-action-group')?.querySelector('.checkout-inline');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok && data.success) {
        form.classList.add('is-added');
        updateBagCounts(data.cart_count ?? 0);
        showBagNotification(data.message || 'Item added to your bag.', data.cart_count ?? 0);
        checkoutLink?.classList.add('is-visible');
        return;
      }
    } catch (error) {
      console.warn('Add to bag request failed, falling back to normal navigation.', error);
    }

    form.submit();
  });
});

document.querySelectorAll('.cart-remove-form').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
        },
        body: new FormData(form),
      });
      const data = await response.json().catch(() => ({}));

      if (response.ok && data.success) {
        form.closest('.cart-item')?.remove();
        updateBagCounts(data.cart_count);

        const formattedTotal = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Number(data.total) || 0);
        document.querySelectorAll('[data-cart-subtotal], [data-cart-total]').forEach((total) => {
          total.textContent = `₹${formattedTotal}`;
        });

        if (data.is_empty) {
          document.querySelector('[data-cart-layout]')?.remove();
          document.querySelector('[data-empty-cart]')?.removeAttribute('hidden');
        }
        return;
      }
    } catch (error) {
      console.warn('Cart removal failed, falling back to normal navigation.', error);
    }

    form.submit();
  });
});

const slides = Array.from(document.querySelectorAll('.hero-slide'));
const heroCaptionText = document.querySelector('.hero-caption-text');

slides.forEach((slide) => {
  if (slide.dataset.image) {
    slide.style.backgroundImage = `url("${slide.dataset.image}")`;
  }
});

if (slides.length) {
  let currentSlide = 0;

  const showSlide = (nextIndex) => {
    const currentElement = slides[currentSlide];
    const nextElement = slides[nextIndex];

    if (!nextElement || nextElement === currentElement) return;

    currentElement.classList.remove('is-active');
    currentElement.classList.add('is-leaving');

    nextElement.classList.remove('is-leaving');
    nextElement.classList.add('is-active');

    currentSlide = nextIndex;
    if (heroCaptionText) {
      heroCaptionText.textContent = nextElement.dataset.caption || '';
    }

    window.setTimeout(() => {
      currentElement.classList.remove('is-leaving');
    }, 1200);
  };

  window.setInterval(() => {
    const nextIndex = (currentSlide + 1) % slides.length;
    showSlide(nextIndex);
  }, 4200);
}

document.querySelectorAll('.messages').forEach((messages) => {
  window.setTimeout(() => {
    messages.classList.add('is-hidden');
    window.setTimeout(() => messages.remove(), 350);
  }, 3200);
});

document.querySelectorAll('.cancel-order-form').forEach((form) => {
  form.addEventListener('submit', (event) => {
    if (!window.confirm(form.dataset.confirm)) {
      event.preventDefault();
    }
  });
});
