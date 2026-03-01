(function () {
  'use strict';

  function initBurger() {
    var burger = document.querySelector('.burger');
    var overlay = document.querySelector('.burger-overlay');
    var body = document.body;

    if (!burger || !overlay) return;

    function openMenu() {
      overlay.classList.add('active');
      burger.classList.add('open');
      body.style.overflow = 'hidden';
    }
    function closeMenu() {
      overlay.classList.remove('active');
      burger.classList.remove('open');
      body.style.overflow = '';
    }

    burger.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      if (overlay.classList.contains('active')) closeMenu();
      else openMenu();
    });
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) closeMenu();
    });
    var menuLinks = document.querySelectorAll('.burger-menu a');
    for (var i = 0; i < menuLinks.length; i++) {
      menuLinks[i].addEventListener('click', closeMenu);
    }
    var closeBtn = document.querySelector('.burger-close');
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initBurger);
  } else {
    initBurger();
  }

  // FAB — плавающая кнопка контактов (открыть / закрыть)
  (function () {
    var fab = document.getElementById('fab');
    var fabToggle = document.getElementById('fab-toggle');
    var fabClose = document.getElementById('fab-close');
    var fabPanel = document.getElementById('fab-panel');
    if (!fab || !fabToggle) return;

    function openFab() {
      fab.classList.add('open');
      if (fabPanel) fabPanel.setAttribute('aria-hidden', 'false');
    }
    function closeFab() {
      fab.classList.remove('open');
      if (fabPanel) fabPanel.setAttribute('aria-hidden', 'true');
    }

    fabToggle.addEventListener('click', function () {
      if (fab.classList.contains('open')) closeFab();
      else openFab();
    });
    if (fabClose) fabClose.addEventListener('click', closeFab);
  })();

  // Хедер — фон при скролле
  const header = document.getElementById('header');
  if (header) {
    function headerScroll() {
      header.classList.toggle('scrolled', window.scrollY > 80);
    }
    window.addEventListener('scroll', headerScroll, { passive: true });
    headerScroll();
  }

  // Скролл-эффект Hero (видео затемняется, текст уходит вверх)
  const hero = document.querySelector('.hero');
  if (hero) {
    function onScroll() {
      const y = window.scrollY;
      const threshold = 120;
      if (y > threshold) hero.classList.add('scrolled');
      else hero.classList.remove('scrolled');
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // Список преимуществ на странице «О нас» — поочерёдное появление при скролле
  const aboutAdvantages = document.querySelector('.about-advantages');
  const aboutList = document.querySelector('.about-advantages-list');
  if (aboutAdvantages && aboutList) {
    var advantagesObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) aboutList.classList.add('in-view');
        });
      },
      { threshold: 0.2 }
    );
    advantagesObserver.observe(aboutAdvantages);
  }

  // Счётчик цифр «как спидометр» в блоке «За цифрами — наш успех»
  (function () {
    var statsSection = document.querySelector('.about-stats');
    var statValues = document.querySelectorAll('.about-stat-value[data-value]');
    if (!statsSection || !statValues.length) return;

    function easeOutExpo(t) {
      return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    }

    function animateValue(el, start, end, duration, prefix, suffix, done) {
      var startTime = null;
      prefix = prefix || '';
      suffix = suffix || '';

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var elapsed = timestamp - startTime;
        var progress = Math.min(elapsed / duration, 1);
        var eased = easeOutExpo(progress);
        var current = Math.round(start + (end - start) * eased);
        el.textContent = prefix + current + suffix;
        if (progress < 1) {
          requestAnimationFrame(step);
        } else {
          el.textContent = prefix + end + suffix;
          if (done) done();
        }
      }
      requestAnimationFrame(step);
    }

    var statsObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          statsObserver.disconnect();
          statValues.forEach(function (el) {
            if (el.dataset.animated) return;
            el.dataset.animated = '1';
            var end = parseInt(el.getAttribute('data-value'), 10);
            var prefix = el.getAttribute('data-prefix') || '';
            var suffix = el.getAttribute('data-suffix') || '';
            animateValue(el, 0, end, 1800, prefix, suffix);
          });
        });
      },
      { threshold: 0.25 }
    );
    statsObserver.observe(statsSection);
  })();

  // Счётчик «спидометр» в Hero
  (function () {
    var heroStatsSection = document.querySelector('.hero-stats');
    var heroStatValues = document.querySelectorAll('.hero-stat-value[data-value]');
    if (!heroStatsSection || !heroStatValues.length) return;

    function easeOutExpo(t) {
      return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    }

    function animateValue(el, start, end, duration, prefix, suffix) {
      var startTime = null;
      prefix = prefix || '';
      suffix = suffix || '';
      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var elapsed = timestamp - startTime;
        var progress = Math.min(elapsed / duration, 1);
        var eased = easeOutExpo(progress);
        var current = Math.round(start + (end - start) * eased);
        el.textContent = prefix + current + suffix;
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = prefix + end + suffix;
      }
      requestAnimationFrame(step);
    }

    var heroStatsObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          heroStatsObserver.disconnect();
          heroStatValues.forEach(function (el) {
            if (el.dataset.animated) return;
            el.dataset.animated = '1';
            var end = parseInt(el.getAttribute('data-value'), 10);
            var prefix = el.getAttribute('data-prefix') || '';
            var suffix = el.getAttribute('data-suffix') || '';
            animateValue(el, 0, end, 1800, prefix, suffix);
          });
        });
      },
      { threshold: 0.2 }
    );
    heroStatsObserver.observe(heroStatsSection);
  })();

  // Плавное появление блоков при скролле
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );
    reveals.forEach(function (el) {
      el.style.transition = 'opacity 0.7s cubic-bezier(0.4, 0, 0.2, 1), transform 0.7s cubic-bezier(0.4, 0, 0.2, 1)';
      observer.observe(el);
    });
  }

  // Анимация цифр при появлении (опционально — можно добавить счётчик)
  const statValues = document.querySelectorAll('.hero-stat-value');
  statValues.forEach(function (el) {
    el.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
  });

  // Уведомление о cookies: принятие / отклонение, сохранение выбора в куки
  (function () {
    var COOKIE_NAME = 'cookie_consent';
    var COOKIE_MAX_AGE_DAYS = 365;
    var banner = document.getElementById('cookie-consent');
    if (!banner) return;

    function getCookie(name) {
      var match = document.cookie.match(new RegExp('(?:^|;\\s*)' + name + '=([^;]*)'));
      return match ? decodeURIComponent(match[1]) : null;
    }

    function setCookie(name, value, days) {
      var maxAge = days * 24 * 60 * 60;
      var secure = window.location.protocol === 'https:' ? '; Secure' : '';
      document.cookie = name + '=' + encodeURIComponent(value) + '; path=/; max-age=' + maxAge + '; SameSite=Lax' + secure;
    }

    function hideBanner() {
      banner.classList.add('hidden');
      banner.setAttribute('aria-hidden', 'true');
      setTimeout(function () {
        banner.setAttribute('hidden', '');
      }, 400);
    }

    function getCsrfToken() {
      var meta = document.querySelector('meta[name="csrf-token"]');
      return meta ? meta.getAttribute('content') : '';
    }

    function onChoice(action) {
      setCookie(COOKIE_NAME, action, COOKIE_MAX_AGE_DAYS);
      hideBanner();
      // Уведомить бэкенд: установить HttpOnly-куки и записать согласие в БД
      fetch('/api/cookie-consent/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ action: action }),
        credentials: 'same-origin'
      }).catch(function () {});
    }

    if (!getCookie(COOKIE_NAME)) {
      banner.removeAttribute('hidden');
      banner.setAttribute('aria-hidden', 'false');
    } else {
      banner.setAttribute('hidden', '');
    }

    banner.querySelectorAll('[data-action]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        onChoice(btn.getAttribute('data-action'));
      });
    });
  })();
})();
