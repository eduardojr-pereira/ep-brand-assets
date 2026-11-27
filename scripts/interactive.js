/*
 * Responsibility: Catalogue filtering, slide/evidence controls and marquee motion.
 * No project data ownership, theme preference or independent translations.
 */

(() => {
    'use strict';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const fine = matchMedia('(hover:hover) and (pointer:fine)');
    const all = (root, selector) => [...root.querySelectorAll(selector)];
    const normalize = value => String(value).normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim();
    function catalog(root) {
        const groups = all(root, '[data-ui-filter]');
        const input = root.querySelector('[data-ui-search]');
        const clear = root.querySelector('[data-ui-clear-search]');
        const count = root.querySelector('[data-ui-count]');
        const empty = root.querySelector('[data-ui-empty]');
        function update() {
            const values = Object.fromEntries(groups.map(g => [g.dataset.uiFilter, g.dataset.uiValue || 'all']));
            const query = normalize(input.value).split(/\s+/).filter(Boolean);
            let total = 0;
            all(root,'[data-ui-project]').forEach(card => {
                const text = normalize(`${card.textContent} ${card.dataset.search} ${all(card,'img').map(i=>i.alt).join(' ')}`);
                card.hidden = !( (values.collection === 'all' || values.collection === card.dataset.collection) &&
                    (values.area === 'all' || card.dataset.areas.split(/\s+/).includes(values.area)) && query.every(t=>text.includes(t)) );
                if (!card.hidden) total++;
            });
            count.textContent = `${total} ${total === 1 ? count.dataset.singular : count.dataset.plural}`;
            empty.hidden = total !== 0;
            clear.hidden = !input.value;
            root.querySelector('.ui-catalog__info [data-ui-reset]').hidden = !input.value && groups.every(g => (g.dataset.uiValue || 'all') === 'all');
        }
        root.addEventListener('ui:filterchange',update);
        input.addEventListener('input',update);
        clear.addEventListener('click',()=>{ input.value=''; update(); input.focus(); });
        all(root,'[data-ui-reset]').forEach(button=>button.addEventListener('click',()=>{
            input.value=''; groups.forEach(g=>window.UI.navigation.select(g,g.dataset.uiDefault || 'all',false)); update(); input.focus();
        }));
        document.addEventListener('ui:languagechange',()=>{groups.forEach(g=>window.UI.navigation.select(g,g.dataset.uiValue || 'all',false));update();});
        root.setAttribute('data-ui-enhanced','');
        update();
    }
    function evidence(root) {
        const frames=all(root,'[data-ui-frame]'), captions=all(root,'[data-ui-caption]'), dots=all(root,'[data-ui-frame-index]');
        const toggle=root.querySelector('[data-ui-evidence-toggle]');
        const cycleToken = getComputedStyle(root).getPropertyValue('--ui-duration-evidence-cycle').trim();
        const cycleDuration = parseFloat(cycleToken) * (cycleToken.endsWith('ms') ? 1 : 1000);
        let index=0, requested=true, visible=!('IntersectionObserver' in window), timer;
        function render(animate=false) {
            frames.forEach((frame,i)=>{frame.hidden=i!==index;frame.removeAttribute('data-entering');if(i===index && animate && !reduced.matches)frame.setAttribute('data-entering','');});
            captions.forEach((caption,i)=>caption.hidden=i!==index);
            dots.forEach((dot,i)=>dot.setAttribute('aria-current',String(i===index)));
        }
        function schedule() {
            clearInterval(timer);
            const playing=requested && !reduced.matches;
            if(toggle){toggle.textContent=playing?'Ⅱ':'▶';toggle.setAttribute('aria-label',playing?toggle.dataset.pause:toggle.dataset.play);toggle.disabled=reduced.matches;}
            if(playing && Number.isFinite(cycleDuration) && cycleDuration > 0 && visible && !document.hidden && !root.closest('[inert]') && !root.matches(':hover,:focus-within') && frames.length>1)
                timer=setInterval(()=>{index=(index+1)%frames.length;render(true);},cycleDuration);
        }
        function theme() {
            const light=document.documentElement.dataset.theme==='light';
            frames.forEach(frame=>{const src=light?frame.dataset.lightSrc:frame.dataset.darkSrc;if(src && frame.getAttribute('src')!==src)frame.src=src;});
        }
        dots.forEach((dot,i)=>dot.addEventListener('click',()=>{index=i;render(true);schedule();}));
        toggle?.addEventListener('click',()=>{requested=!requested;schedule();});
        ['pointerenter','pointerleave','focusin','focusout'].forEach(event=>root.addEventListener(event,()=>requestAnimationFrame(schedule)));
        document.addEventListener('visibilitychange',schedule);
        document.addEventListener('ui:themechange',theme);
        document.addEventListener('ui:languagechange',schedule);
        root.addEventListener('ui:slidechange',schedule);
        reduced.addEventListener('change',schedule);
        if('IntersectionObserver' in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;schedule();}).observe(root);
        root.setAttribute('data-ui-enhanced','');render();theme();schedule();
    }
    function carousel(root) {
        const track=root.querySelector('[data-ui-carousel-track]'), slides=all(track,'[data-ui-slide]');
        const prev=root.querySelector('[data-ui-carousel-action="previous"]'),next=root.querySelector('[data-ui-carousel-action="next"]');
        const count=root.querySelector('[data-ui-carousel-count]');
        let index=0, settle, drag=null, blockClick=false;
        const clamp=i=>Math.max(0,Math.min(slides.length-1,i));
        function update(i,animate=false) {
            const before=index; index=clamp(i);
            slides.forEach((slide,j)=>{slide.inert=j!==index;slide.toggleAttribute('data-ui-current',j===index);slide.removeAttribute('data-ui-slide-enter');if(j===index && animate && !reduced.matches)slide.dataset.uiSlideEnter=index<before?'reverse':'forward';all(slide,'[data-ui-evidence]').forEach(e=>e.dispatchEvent(new Event('ui:slidechange')));});
            const focused=document.activeElement;
            prev.disabled=index===0;next.disabled=index===slides.length-1;
            if((focused===prev && prev.disabled)||(focused===next && next.disabled))track.focus({preventScroll:true});
            count.textContent=`${String(index+1).padStart(2,'0')} / ${String(slides.length).padStart(2,'0')}`;
            root.style.setProperty('--ui-carousel-progress',`${(index+1)/slides.length*100}%`);
        }
        function go(i) {i=clamp(i); if(slides[index].contains(document.activeElement))track.focus({preventScroll:true}); update(i,i!==index);track.scrollTo({left:i*track.clientWidth,behavior:reduced.matches?'instant':'smooth'});}
        prev.addEventListener('click',()=>go(index-1));next.addEventListener('click',()=>go(index+1));
        track.addEventListener('keydown',event=>{if(event.target!==track)return;const map={ArrowLeft:index-1,ArrowRight:index+1,Home:0,End:slides.length-1};if(event.key in map){event.preventDefault();go(map[event.key]);}});
        track.addEventListener('scroll',()=>{clearTimeout(settle);settle=setTimeout(()=>{const i=clamp(Math.round(track.scrollLeft/Math.max(1,track.clientWidth)));if(i!==index)update(i,true);},120);},{passive:true});
        track.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.button!==0||e.target.closest('a,button,input,select,textarea'))return;drag={id:e.pointerId,x:e.clientX,left:track.scrollLeft,moved:false};});
        track.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x;if(Math.abs(dx)>6&&!drag.moved){drag.moved=true;track.setPointerCapture(e.pointerId);track.setAttribute('data-dragging','');}if(drag.moved){e.preventDefault();track.scrollLeft=drag.left-dx;}});
        function end(){if(!drag)return;const moved=drag.moved;drag=null;track.removeAttribute('data-dragging');if(moved){blockClick=true;go(Math.round(track.scrollLeft/Math.max(1,track.clientWidth)));setTimeout(()=>blockClick=false,0);}}
        window.addEventListener('pointerup',end);window.addEventListener('pointercancel',end);
        track.addEventListener('click',e=>{if(blockClick){e.preventDefault();e.stopPropagation();}},true);
        window.addEventListener('resize',()=>track.scrollTo({left:index*track.clientWidth,behavior:'instant'}));
        root.setAttribute('data-ui-enhanced','');update(0);
    }
    function marquee(root) {
        const link=root.querySelector('[data-ui-lens]'), lanes=root.querySelector('.ui-marquee__lanes'), toggle=root.querySelector('[data-ui-marquee-toggle]');
        const tracks=all(lanes,'.ui-marquee__track');
        let lens=null,lensTracks=[], widths=[1,1], offsets=[0,0], paused=false, hover=false, focused=false, visible=!('IntersectionObserver' in window), raf=0,last=0;
        function paint(){tracks.forEach((track,i)=>{const transform=`translate3d(${i===0?offsets[i]-widths[i]:-offsets[i]}px,0,0)`;track.style.transform=transform;if(lensTracks[i])lensTracks[i].style.transform=transform;});}
        function stop(){cancelAnimationFrame(raf);raf=0;last=0;}
        function eligible(){return !reduced.matches&&!paused&&!hover&&!focused&&visible&&!document.hidden;}
        function tick(now){raf=0;if(!eligible()){last=0;return;}const dt=last?Math.min((now-last)/1000,.05):0;last=now;offsets=offsets.map((o,i)=>(o+dt*(root.clientWidth<640?42:66)*(i===0?1:.65))%widths[i]);paint();raf=requestAnimationFrame(tick);}
        function schedule(){if(eligible()){if(!raf)raf=requestAnimationFrame(tick);}else stop();toggle.textContent=paused?'▶':'Ⅱ';toggle.setAttribute('aria-label',paused?toggle.dataset.play:toggle.dataset.pause);}
        function layout(){stop();lens?.remove();lens=null;lensTracks=[];link.removeAttribute('data-lens-active');root.toggleAttribute('data-ui-running',!reduced.matches);tracks.forEach((track,i)=>{const first=track.firstElementChild;track.replaceChildren(first);if(reduced.matches)return;const ratio=offsets[i]/widths[i];widths[i]=Math.max(1,first.getBoundingClientRect().width);offsets[i]=ratio*widths[i];const count=Math.ceil(root.clientWidth/widths[i])+2;for(let n=1;n<count;n++)track.append(first.cloneNode(true));});if(!reduced.matches){lens=lanes.cloneNode(true);lens.classList.add('ui-marquee__lens');lens.setAttribute('aria-hidden','true');link.append(lens);lensTracks=all(lens,'.ui-marquee__track');paint();}schedule();}
        link.addEventListener('pointerenter',e=>{if(e.pointerType==='mouse'){hover=true;schedule();}});
        link.addEventListener('pointermove',e=>{if(!fine.matches||reduced.matches||e.pointerType!=='mouse'||!lens)return;const r=link.getBoundingClientRect();link.style.setProperty('--ui-lens-x',`${e.clientX-r.left}px`);link.style.setProperty('--ui-lens-y',`${e.clientY-r.top}px`);link.setAttribute('data-lens-active','');});
        link.addEventListener('pointerleave',()=>{hover=false;link.removeAttribute('data-lens-active');schedule();});
        link.addEventListener('focus',()=>{focused=true;schedule();});link.addEventListener('blur',()=>{focused=false;schedule();});
        toggle.addEventListener('click',()=>{paused=!paused;schedule();});
        document.addEventListener('visibilitychange',schedule);
        document.addEventListener('ui:languagechange',layout);
        reduced.addEventListener('change',layout);fine.addEventListener('change',()=>link.removeAttribute('data-lens-active'));
        if('IntersectionObserver' in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;schedule();}).observe(root);
        window.addEventListener('resize',layout);document.fonts?.ready.then(layout);layout();
    }
    function init(){all(document,'[data-ui-catalog]').forEach(catalog);all(document,'[data-ui-evidence]').forEach(evidence);all(document,'[data-ui-carousel]').forEach(carousel);all(document,'[data-ui-marquee]').forEach(marquee);}
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
