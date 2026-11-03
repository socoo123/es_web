/* Native anchors still work without JavaScript; highlight the section being read. */
(function () {
  'use strict';
  var links = Array.from(document.querySelectorAll('.curriculum-nav a'));
  var stages = links.map(function (link) { return document.querySelector(link.hash); });
  var header = document.querySelector('.topbar');
  function paint() {
    var current = stages[0];
    var edge = header.getBoundingClientRect().bottom + 120;
    stages.forEach(function (stage) {
      if (stage.getBoundingClientRect().top <= edge) current = stage;
    });
    links.forEach(function (link) {
      if (link.hash === '#' + current.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }
  var pending = false;
  window.addEventListener('scroll', function () {
    if (pending) return;
    pending = true;
    requestAnimationFrame(function () { paint(); pending = false; });
  }, { passive: true });
  window.addEventListener('resize', paint);
  window.addEventListener('pageshow', paint);
  paint();
})();
