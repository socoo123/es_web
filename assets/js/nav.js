/* nav.js — 主题切换 + 章节页侧边目录(零依赖) */
(function () {
  'use strict';
  var THEME_KEY = 'es-web:theme';

  function readTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }
  function apply(t) {
    document.documentElement.setAttribute('data-theme', t);
    try { localStorage.setItem(THEME_KEY, t); } catch (e) { /* 隐私模式等,忽略 */ }
    var btn = document.querySelector('.theme-toggle');
    if (btn) btn.textContent = t === 'dark' ? '☀️ 浅色' : '🌙 深色';
  }

  apply(readTheme() === 'dark' ? 'dark' : 'light');

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.theme-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        var cur = document.documentElement.getAttribute('data-theme');
        apply(cur === 'dark' ? 'light' : 'dark');
      });
    }

    // 章节页:由 h2 生成侧边目录(窄屏隐藏,CSS 控制)
    var art = document.querySelector('article.chapter');
    if (!art || !art.id) return;
    var hs = art.querySelectorAll('h2');
    if (!hs.length) return;
    var toc = document.createElement('nav');
    toc.className = 'toc';
    var html = '<div class="toc-title">本课目录</div>';
    hs.forEach(function (h, i) {
      if (!h.id) h.id = art.id + '-s' + (i + 1);
      html += '<a href="#' + h.id + '">' + h.textContent + '</a>';
    });
    toc.innerHTML = html;
    document.body.appendChild(toc);
  });
})();
