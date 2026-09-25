/* flow-player.js — 快照式机制动画引擎(零依赖)
 *
 * 数据注册(experiments 同款思路,<script> 注册表,file:// 可用):
 *   window.ESFLOWS['ch14-write-path'] = {
 *     version: 1, id: 'ch14-write-path', title: '一次写入的完整旅程', speed: 1800,
 *     steps: [
 *       { svg: '<svg viewBox="0 0 760 300">…</svg>', note: '这一步发生了什么' },
 *       …每步一张完整快照(svg 必须完整,不搞增量 diff——永远算不错)
 *     ]
 *   };
 * 页面插槽:<div class="fp-slot" data-flow="ch14-write-path"></div>
 *
 * 动效声明在快照 SVG 内部,插入即播(CSS):
 *   class="fp-pop"        元素弹入(缩放淡入)
 *   class="fp-slide-right"元素从左滑入
 *   class="fp-draw"       线条描画(元素需加 pathLength="1")
 *   class="fp-pulse"      持续呼吸闪烁(表示「活跃」)
 *   class="fp-glow"       一次性发光
 *
 * 引擎职责刻意收窄:切步时写 stage、更新解说、驱动播放。
 * 只有「步进/播放推进」才写 DOM;若用户正在播放器内选中文字,自动暂停(避免打断选区)。
 */
(function () {
  'use strict';
  var SPEEDS = [1, 2, 0.5];

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function Player(slot, flow) {
    this.flow = flow;
    this.idx = -1;
    this.timer = null;
    this.playing = false;
    this.speedIx = 0;
    this.autoplayed = false;

    var box = document.createElement('div');
    box.className = 'fp';
    box.tabIndex = 0;
    box.setAttribute('role', 'region');
    box.setAttribute('aria-label', flow.title);

    var head = document.createElement('div');
    head.className = 'fp-head';
    var title = document.createElement('div');
    title.className = 'fp-title';
    title.textContent = flow.title;
    var count = document.createElement('div');
    count.className = 'fp-count';
    var ctrls = document.createElement('div');
    ctrls.className = 'fp-ctrls';
    this.btnPlay = mkBtn('▶', '播放/暂停', this.toggle.bind(this));
    var bPrev = mkBtn('⏮', '上一步', this.prev.bind(this));
    var bNext = mkBtn('⏭', '下一步', this.next.bind(this));
    var bReset = mkBtn('⟲', '重置', this.reset.bind(this));
    this.btnSpeed = mkBtn('1×', '调速', this.cycleSpeed.bind(this));
    ctrls.appendChild(this.btnPlay);
    ctrls.appendChild(bPrev);
    ctrls.appendChild(bNext);
    ctrls.appendChild(bReset);
    ctrls.appendChild(this.btnSpeed);
    head.appendChild(title);
    head.appendChild(count);
    head.appendChild(ctrls);

    this.stage = document.createElement('div');
    this.stage.className = 'fp-stage';
    this.note = document.createElement('div');
    this.note.className = 'fp-note';

    box.appendChild(head);
    box.appendChild(this.stage);
    box.appendChild(this.note);
    slot.appendChild(box);

    this.countEl = count;
    this.box = box;

    box.addEventListener('keydown', function (e) {
      if (e.key === ' ' || e.key === 'ArrowRight') { e.preventDefault(); this.next(); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); this.prev(); }
    }.bind(this));

    this.render(0);
    this.watch();
  }

  function mkBtn(label, title, fn) {
    var b = document.createElement('button');
    b.className = 'fp-btn';
    b.textContent = label;
    b.title = title;
    b.addEventListener('click', fn);
    return b;
  }

  Player.prototype.userSelecting = function () {
    try {
      var sel = window.getSelection();
      if (sel && !sel.isCollapsed && sel.anchorNode &&
          this.box.contains(sel.anchorNode)) return true;
    } catch (e) { /* 忽略 */ }
    return false;
  };

  Player.prototype.render = function (i) {
    var steps = this.flow.steps;
    if (i < 0) i = 0;
    if (i > steps.length - 1) i = steps.length - 1;
    if (i === this.idx) return;
    this.idx = i;
    var st = steps[i];
    // 整步替换(离散快照,不是逐帧动画);选区内不写
    this.stage.innerHTML = st.svg || '';
    this.note.textContent = st.note || '';
    this.countEl.textContent = (i + 1) + ' / ' + steps.length;
    if (i === steps.length - 1) this.stop();
  };

  Player.prototype.play = function () {
    if (this.playing) return;
    if (this.idx >= this.flow.steps.length - 1) { this.idx = -1; this.render(0); } // 播完重播
    this.playing = true;
    this.btnPlay.textContent = '⏸';
    this.schedule();
  };
  Player.prototype.stop = function () {
    this.playing = false;
    this.btnPlay.textContent = '▶';
    if (this.timer) { clearTimeout(this.timer); this.timer = null; }
  };
  Player.prototype.schedule = function () {
    if (!this.playing) return;
    var self = this;
    var delay = (this.flow.speed || 1800) / SPEEDS[this.speedIx];
    this.timer = setTimeout(function () {
      if (self.userSelecting()) { self.schedule(); return; } // 用户在选文字,让一步
      if (self.idx >= self.flow.steps.length - 1) { self.stop(); return; }
      self.render(self.idx + 1);
      if (self.playing) self.schedule();
    }, delay);
  };
  Player.prototype.toggle = function () { this.playing ? this.stop() : this.play(); };
  Player.prototype.next = function () { this.stop(); this.render(this.idx + 1); };
  Player.prototype.prev = function () { this.stop(); this.render(this.idx - 1); };
  Player.prototype.reset = function () { this.stop(); this.idx = -1; this.render(0); };
  Player.prototype.cycleSpeed = function () {
    this.speedIx = (this.speedIx + 1) % SPEEDS.length;
    this.btnSpeed.textContent = SPEEDS[this.speedIx] + '×';
  };
  /* 滚入视口自动播一遍 */
  Player.prototype.watch = function () {
    var self = this;
    if (!('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && !self.autoplayed) {
          self.autoplayed = true;
          self.play();
          io.disconnect();
        }
      });
    }, { threshold: 0.4 });
    io.observe(this.box);
  };

  document.addEventListener('DOMContentLoaded', function () {
    var flows = window.ESFLOWS || {};
    document.querySelectorAll('.fp-slot').forEach(function (slot) {
      var id = slot.getAttribute('data-flow');
      var flow = flows[id];
      if (!flow) {
        slot.innerHTML = '<div class="fp"><div class="fp-error">未找到动画 ' + esc(id) +
          '(检查注册:window.ESFLOWS)</div></div>';
        return;
      }
      try { new Player(slot, flow); } catch (e) {
        slot.innerHTML = '<div class="fp"><div class="fp-error">动画渲染失败:' + esc(e.message) + '</div></div>';
      }
    });
  });
})();
