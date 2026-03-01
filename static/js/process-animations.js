/**
 * Страница «Процесс»: появление блоков слева/справа при скролле (GSAP + ScrollTrigger).
 */
(function () {
  'use strict';

  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  var page = document.querySelector('.process-page');
  if (!page) return;

  var intro = document.getElementById('process-intro');
  var blocks = page.querySelectorAll('.process-block[data-from]');
  var cta = document.getElementById('process-cta');

  // Интро при загрузке
  if (intro) {
    var h1 = intro.querySelector('h1');
    var lead = intro.querySelector('.process-intro-lead');
    gsap.set([h1, lead], { opacity: 0, y: 36 });
    gsap.to(h1, { opacity: 1, y: 0, duration: 0.95, ease: 'power3.out' });
    gsap.to(lead, { opacity: 1, y: 0, duration: 0.85, delay: 0.18, ease: 'power3.out' });
  }

  // Каждый блок выезжает слева или справа при скролле
  var fromLeft = 120;
  var fromRight = 120;

  blocks.forEach(function (block, i) {
    var from = block.getAttribute('data-from');
    var x = from === 'left' ? -fromLeft : fromRight;
    gsap.set(block, { opacity: 0, x: x });
    gsap.to(block, {
      opacity: 1,
      x: 0,
      duration: 0.9,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: block,
        start: 'top 85%',
        end: 'top 55%',
        toggleActions: 'play none none none'
      }
    });
  });

  // CTA при доскролле
  if (cta) {
    gsap.set(cta, { opacity: 0, y: 48 });
    gsap.to(cta, {
      opacity: 1,
      y: 0,
      duration: 0.85,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: cta,
        start: 'top 88%',
        toggleActions: 'play none none none'
      }
    });
  }
})();
