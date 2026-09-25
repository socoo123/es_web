/* progress.js — localStorage 学习进度:课末「标记已读」+ 首页统计 */
(function () {
  'use strict';
  var KEY = 'es-web:read';

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(o) {
    try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) { /* 忽略 */ }
  }

  document.addEventListener('DOMContentLoaded', function () {
    // 章节页:已读开关
    var art = document.querySelector('article.chapter');
    var btn = document.querySelector('.read-toggle');
    if (art && art.dataset.ch && btn) {
      var ch = art.dataset.ch;
      var paint = function () {
        var on = !!load()[ch];
        btn.classList.toggle('is-on', on);
        btn.textContent = on ? '✓ 本课已读(点击取消)' : '标记本课已读';
      };
      paint();
      btn.addEventListener('click', function () {
        var o = load();
        if (o[ch]) delete o[ch]; else o[ch] = true;
        save(o);
        paint();
      });
    }

    // 首页:总进度条 + 卡片已读标记
    var fill = document.querySelector('.progress-fill');
    var text = document.querySelector('.progress-text');
    var cards = document.querySelectorAll('.card[data-ch]');
    if (!cards.length) return;
    var o = load();
    var done = 0;
    cards.forEach(function (c) {
      var on = !!o[c.getAttribute('data-ch')];
      c.classList.toggle('is-read', on);
      if (on) done++;
    });
    if (fill) fill.style.width = (cards.length ? Math.round(done / cards.length * 100) : 0) + '%';
    if (text) text.textContent = '已读 ' + done + ' / ' + cards.length + ' 课';
  });
})();
