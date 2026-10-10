/* Sync the chapter theme through the generated viewer's own control.
 * The checked Archify HTML stays unchanged. file:// viewers retain their
 * own controls if the browser isolates each local file's origin.
 */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var frames = Array.from(document.querySelectorAll('.archify-frame'));
    function syncTheme(frame) {
      try {
        var doc = frame.contentDocument;
        var theme = document.documentElement.getAttribute('data-theme');
        var button = doc && doc.getElementById('btn-theme');
        if (button && doc.documentElement.getAttribute('data-theme') !== theme) button.click();
      } catch (e) { /* Local file origins can be isolated; viewer controls still work. */ }
    }
    frames.forEach(function (frame) {
      frame.addEventListener('load', function () { syncTheme(frame); });
      syncTheme(frame);
    });
    new MutationObserver(function () { frames.forEach(syncTheme); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    document.querySelectorAll('[data-replay-diagram]').forEach(function (button) {
      button.addEventListener('click', function () {
        var frame = document.getElementById(button.getAttribute('data-replay-diagram'));
        if (frame) {
          try {
            var viewer = frame.contentWindow.Archify;
            if (viewer && viewer.motionGovernor) viewer.motionGovernor.resume();
          } catch (e) { /* A local file viewer may have an isolated origin. */ }
          frame.src = frame.getAttribute('src');
        }
      });
    });
  });
})();
