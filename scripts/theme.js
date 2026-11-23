/* EP global theme controller. No Lottie or mutation of header switch markup. */
(function(){
  'use strict';
  const root=document.documentElement;
  function current(){return root.getAttribute('data-theme')==='light'?'light':'dark';}
  function syncButtons(theme){
    document.querySelectorAll('[data-theme-toggle]').forEach(button=>{
      const isLight=theme==='light';
      if(button.getAttribute('role')==='switch'){
        button.setAttribute('aria-checked',String(isLight));
        button.removeAttribute('aria-pressed');
      }else button.setAttribute('aria-pressed',String(isLight));
      // Existing generic theme buttons retain the old label behavior.
      // Never overwrite header switch descendants: language labels and visual track must survive.
      if(!button.classList.contains('ep-header__theme-switch')){
        button.textContent=isLight?(button.dataset.darkLabel||'Dark'):(button.dataset.lightLabel||'Light');
      }
      const pt=document.documentElement.lang.toLowerCase().startsWith('pt');
      button.setAttribute('aria-label',pt?(isLight?'Ativar tema escuro':'Ativar tema claro'):(isLight?'Switch to dark theme':'Switch to light theme'));
    });
  }
  function apply(theme){
    const value=theme==='light'?'light':'dark';
    root.setAttribute('data-theme',value);
    try{localStorage.setItem('ep_theme',value);}catch(_){}
    syncButtons(value);
    document.dispatchEvent(new CustomEvent('ep:themechange',{detail:{theme:value}}));
  }
  document.addEventListener('DOMContentLoaded',()=>{
    document.querySelectorAll('[data-theme-toggle]').forEach(button=>button.addEventListener('click',()=>apply(current()==='dark'?'light':'dark')));
    apply(current());
  });
  window.EPTheme=Object.freeze({current,apply});
})();
