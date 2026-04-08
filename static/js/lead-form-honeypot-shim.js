/**
 * Подмешивает honeypot-поле в POST (FormData) на страницах с React-заявками.
 * Поле должно оставаться пустым; боты часто заполняют все поля.
 */
(function () {
  'use strict';
  var HP = 'hp_company';
  var PATH_PREFIXES = [
    '/poisk-avto/',
    '/vykup/',
    '/dostavka-avto/',
    '/postanovka-na-uchet/',
  ];

  function isLeadPost(url) {
    try {
      var u = typeof url === 'string' ? url : url && url.url;
      if (!u) return false;
      var path = new URL(u, window.location.origin).pathname;
      for (var i = 0; i < PATH_PREFIXES.length; i++) {
        if (path.indexOf(PATH_PREFIXES[i]) === 0) return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  var origFetch = window.fetch;
  window.fetch = function (input, init) {
    if (
      init &&
      init.method &&
      String(init.method).toUpperCase() === 'POST' &&
      init.body instanceof FormData &&
      isLeadPost(input)
    ) {
      if (!init.body.has(HP)) {
        init.body.append(HP, '');
      }
    }
    return origFetch.apply(this, arguments);
  };
})();
