/* EP header behavior: native details for click/keyboard, close siblings/outside/Escape. */
(() => {
 'use strict';
 const menus=Array.from(document.querySelectorAll('.ep-header__dropdown'));
 menus.forEach(menu=>menu.addEventListener('toggle',()=>{if(menu.open)menus.forEach(other=>{if(other!==menu)other.open=false;});}));
 document.addEventListener('pointerdown',event=>menus.forEach(menu=>{if(!menu.contains(event.target))menu.open=false;}));
 document.addEventListener('keydown',event=>{if(event.key==='Escape'){const open=menus.find(menu=>menu.open);if(open){open.open=false;open.querySelector('summary')?.focus();}}});
})();