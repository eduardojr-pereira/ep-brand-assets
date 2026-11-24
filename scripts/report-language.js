/* EP report language compatibility bridge. */
(function () {
  'use strict';

  function sync() {
    const locale = document.documentElement.lang;
    const button = document.getElementById(
      locale === 'pt-BR' ? 'locale-pt' : 'locale-en'
    );

    if (button && button.getAttribute('aria-pressed') !== 'true') {
      button.click();
    }
  }

  document.addEventListener('ep:languagechange', sync);
  document.addEventListener('DOMContentLoaded', sync);
})();
