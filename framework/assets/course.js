(function () {
  'use strict';
  function text(tag, value) {
    var el = document.createElement(tag); el.textContent = value; return el;
  }
  function copyButton(code) {
    var button = text('button', '复制代码');
    button.type = 'button'; button.className = 'copy-code';
    button.addEventListener('click', async function () {
      try {
        if (navigator.clipboard && window.isSecureContext) {
          await navigator.clipboard.writeText(code.textContent);
        } else {
          var area = document.createElement('textarea');
          area.value = code.textContent; document.body.appendChild(area); area.select();
          var copied = document.execCommand('copy'); area.remove();
          if (!copied) throw new Error('copy failed');
        }
        button.textContent = '已复制';
      } catch (_) { button.textContent = '请选中代码复制'; }
    });
    return button;
  }
  document.querySelectorAll('pre.code-block').forEach(function (pre) {
    var bar = document.createElement('div'); bar.className = 'code-tools';
    bar.appendChild(text('span', pre.dataset.label || pre.querySelector('code').className.replace('language-', '').toUpperCase()));
    bar.appendChild(copyButton(pre.querySelector('code')));
    pre.before(bar);
  });
  function theme() {
    var dark = document.documentElement.dataset.theme === 'dark';
    document.querySelectorAll('[data-d2-light]').forEach(function (img) {
      img.src = dark ? img.dataset.d2Dark : img.dataset.d2Light;
      var expand = img.closest('figure').querySelector('[data-expand-d2]');
      if (expand) expand.href = img.src;
    });
  }
  theme();
  new MutationObserver(theme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
})();
