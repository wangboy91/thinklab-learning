/* ES5 guard: only this page's explicitly marked required scripts. */
(function () {
  var ready=false, runtimeError='', resourceError='', timer;
  var dependencies={'content.js':'CONTENT','algorithms.js':'Algorithms','codes.js':'CODES','sync.js':'ProgressSync','routes.js':'ROUTES','lessons.js':'LESSONS','algorithms-extra.js':'EXTRA_TRACES'};
  function box(message){var element=document.getElementById('startup-error');if(!element){element=document.createElement('div');element.id='startup-error';element.setAttribute('role','alert');var app=document.getElementById('app');if(app)app.insertBefore(element,app.firstChild)}if(element){element.textContent=message+' 可打开“连接检查”确认资源响应。';element.style.cssText='padding:12px;margin:12px 0;background:#fff0d8;color:#573c15;border-radius:8px;font:16px/1.6 sans-serif;'}}
  function clear(){var element=document.getElementById('startup-error');if(element&&element.parentNode)element.parentNode.removeChild(element);resourceError=''}
  function missing(){var list=[];for(var file in dependencies)if(Object.prototype.hasOwnProperty.call(dependencies,file)&&!window[dependencies[file]])list.push(file);return list}
  function check(){if(runtimeError){box(runtimeError);return}if(!ready)return;var files=missing();if(files.length){box('关键网页资源未完成：'+files.join('、')+'。请刷新');return}clear()}
  window.ThinkLabBoot={ready:function(){ready=true;clearTimeout(timer);check()},check:check,error:function(message){runtimeError=message;box(message)}};
  window.addEventListener('error',function(event){var target=event.target;
    if(target&&target.tagName==='SCRIPT'){
      if(!target.getAttribute||target.getAttribute('data-thinklab-critical')!=='true')return;
      var src=target.getAttribute('src')||'',file=src.split('/').pop().split('?')[0].split('#')[0];
      resourceError='网页资源没有加载完成：'+file+'。请刷新';
      if(ready&&missing().length===0){clear();return}box(resourceError);return;
    }
    if(event.message){runtimeError='页面执行出错：'+event.message;box(runtimeError)}
  },true);
  window.addEventListener('unhandledrejection',function(){runtimeError='网页操作未完成；进度未清空，请刷新重试';box(runtimeError)});
  timer=setTimeout(function(){if(!ready)box(resourceError||'题库加载超过 6 秒，请刷新')},6000);
}());
