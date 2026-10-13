/* ES5 startup guard: still parses when a browser rejects newer application JS. */
(function () {
  var ready = false, lastError = '', timer;
  function show(message) {
    lastError = message;
    var box = document.getElementById('startup-error');
    if (!box) {
      box = document.createElement('div'); box.id = 'startup-error'; box.setAttribute('role', 'alert');
      var app = document.getElementById('app'); if (app) app.insertBefore(box, app.firstChild);
    }
    if (box) { box.textContent = message + ' 可打开“连接检查”确认是否到达电脑。'; box.style.cssText = 'padding:12px;margin:12px 0;background:#fff0d8;color:#573c15;border-radius:8px;font:16px/1.6 sans-serif;'; }
  }
  window.ThinkLabBoot = { ready: function () { ready = true; clearTimeout(timer); }, error: show };
  window.addEventListener('error', function (event) {
    var target = event.target;
    if (target && target.tagName === 'SCRIPT') show('网页资源没有加载完成，请刷新或使用系统浏览器打开。');
    else if (event.message) show('页面初始化出错：' + event.message + '。请使用更新的 Chrome 或 Safari。');
  }, true);
  window.addEventListener('unhandledrejection', function () { show('网页操作未完成；进度不会被清空，请刷新重试。'); });
  timer = setTimeout(function () { if (!ready) show(lastError || '题库加载超过 6 秒，请刷新或打开连接检查。'); }, 6000);
}());
