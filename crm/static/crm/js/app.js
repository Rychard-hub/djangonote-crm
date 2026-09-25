(function () {
  var STORAGE_KEY = 'bn-theme';

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.querySelectorAll('[data-theme-icon]').forEach(function (el) {
      el.innerHTML = theme === 'dark' ? ICON_SUN : ICON_MOON;
    });
    document.querySelectorAll('[data-theme-label]').forEach(function (el) {
      el.textContent = theme === 'dark' ? 'Šviesi tema' : 'Tamsi tema';
    });
  }

  var ICON_SUN = '<path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"></path>';
  var ICON_MOON = '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path>';

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var current = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
        var next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        applyTheme(next);
      });
    });
    applyTheme(document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light');

    var sheet = document.getElementById('bn-more-sheet');
    document.querySelectorAll('[data-open-more]').forEach(function (btn) {
      btn.addEventListener('click', function () { if (sheet) sheet.classList.add('is-open'); });
    });
    document.querySelectorAll('[data-close-more]').forEach(function (btn) {
      btn.addEventListener('click', function () { if (sheet) sheet.classList.remove('is-open'); });
    });
  });
})();
