(() => {
  function sync(){const pt=document.documentElement.lang.toLowerCase().startsWith('pt');document.querySelectorAll('[data-ep-project-en]').forEach(n=>{n.textContent=pt?n.dataset.epProjectPt:n.dataset.epProjectEn;});}
  document.addEventListener('ep:languagechange',sync);
  new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});sync();
})();
