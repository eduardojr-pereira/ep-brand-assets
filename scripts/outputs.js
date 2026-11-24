/* Shared output localization, including persisted initial language. */
(() => {
  'use strict';
  const section=document.querySelector('.ep-outputs');
  if(!section)return;
  function sync(){
    const pt=document.documentElement.lang.toLowerCase().startsWith('pt');
    section.querySelectorAll('[data-ep-out-en]').forEach(node=>{node.textContent=pt?node.dataset.epOutPt:node.dataset.epOutEn});
  }
  document.addEventListener('ep:languagechange',sync);
  new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
  sync();
})();
