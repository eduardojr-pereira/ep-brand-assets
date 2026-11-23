/* Must be loaded synchronously in <head>, before styles, to prevent wrong-theme flash. */
(function () {
  'use strict';
  var saved;
  try { saved = localStorage.getItem('ep_theme'); } catch (_) {}
  document.documentElement.setAttribute('data-theme', saved === 'light' ? 'light' : 'dark');
})();
