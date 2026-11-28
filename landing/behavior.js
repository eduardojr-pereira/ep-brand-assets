/*
 * Responsibility: Coordinate landing-specific hero replay, scroll-driven CTA media and contact illustration/validation.
 * Boundaries: No duplicated theme, locale, shared component state, analytics, backend, or simulated delivery success.
 */
(() => {
    'use strict';
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    const fine = matchMedia('(hover:hover) and (pointer:fine)');
    const clamp = value => Math.max(0, Math.min(1, value));
    const headerOffset = () => document.querySelector('[data-ui-header]')?.offsetHeight || 0;
    const tr = (key) => UI.i18n.format('content.landing.' + key);
    const hero = document.getElementById('home');
    let locale = UI.i18n.current();
    document.addEventListener('ui:languagechange', () => {
        const next = UI.i18n.current();
        if (next !== locale) {
            if (hero) UI.motion.replay(hero);
            // The shared controller replays only reached, visible editorial repeat targets.
            // Contact uses once and keeps its content and form state stable.
            UI.motion.replay(document.body, { visibleEditorial: true, top: headerOffset() });
        }
        locale = next;
    });
    function cta(section) {
        const stage = section.querySelector('[data-landing-stage]');
        const sticky = section.querySelector('.ui-landing-cta__sticky');
        const curtain = section.querySelector('[data-landing-curtain]');
        const zoom = section.querySelector('[data-landing-zoom]');
        const vectors = [...section.querySelectorAll('[data-landing-vector]')];
        const lines = [...section.querySelectorAll('[data-landing-line]')];
        const reveal = section.querySelector('[data-landing-reveal]');
        const video = section.querySelector('[data-landing-video]');
        const playbackControl = section.querySelector('[data-landing-video-control]');
        const toggle = playbackControl.querySelector('button');
        const toggleLabel = toggle.querySelector('[data-ui-label]');
        const outlines = JSON.parse(section.querySelector('#landing-cta-outlines').textContent);
        let geometry = null, raf = 0, visible = false, paused = reduced.matches, failed = false;
        const animate = () => !reduced.matches && innerHeight > 450;
        function update() {
            raf = 0;
            if (!geometry) return;
            const g = geometry;
            const travel = section.offsetHeight - sticky.offsetHeight;
            const progress = animate() && travel > 0 ? clamp((headerOffset() - section.getBoundingClientRect().top) / travel) : 1;
            const t = clamp((progress - .07) / .79);
            const center = t*t*(3-2*t), scale = Math.pow(g.max, t);
            const x = g.x + (g.cx-g.x)*center, y = g.y + (g.cy-g.y)*center;
            zoom.setAttribute('transform', `translate(${x} ${y}) scale(${scale}) translate(${-g.x} ${-g.y})`);
            curtain.style.visibility = t >= 1 ? 'hidden' : 'visible';
            section.toggleAttribute('data-landing-revealed', t >= .99);
            const focused = reveal.contains(document.activeElement);
            reveal.inert = t < .99 && !focused;
        }
        function schedule() { if (!raf) raf = requestAnimationFrame(update); }
        function resize() {
            const w = stage.clientWidth, h = stage.clientHeight;
            if (!w || !h) return;
            const shapes = lines.map(line => outlines[line.textContent]);
            if (shapes.some(x => !x)) return;
            section.toggleAttribute('data-landing-enhanced', animate());
            curtain.setAttribute('viewBox', `0 0 ${w} ${h}`);
            for (const el of [section.querySelector('#landing-cta-mask'),section.querySelector('[data-landing-mask-base]'),section.querySelector('[data-landing-cover]')]) {
                el.setAttribute('width',w); el.setAttribute('height',h);
            }
            const fs = Math.min(h*.34, (w-Math.min(w*.08,148))*2048/Math.max(...shapes.map(s=>s.width)));
            const k = fs/2048;
            shapes.forEach((shape,i)=>{
                const x=(w-shape.width*k)/2, y=h/2-fs*1.72/2+fs*.73+i*fs*.92;
                vectors[i].setAttribute('d',shape.d);
                vectors[i].setAttribute('transform',`translate(${x} ${y}) scale(${k} ${-k})`);
                if (i===1) geometry={x:x+shape.focus*k,y:y-590.5*k,cx:w/2,cy:h/2,max:Math.max(2,Math.max(w/(295*k),h/(1181*k))*1.65)};
            });
            schedule();
        }
        function playback() {
            playbackControl.hidden = failed;
            toggle.setAttribute('aria-pressed',String(paused));
            UI.i18n.bind(toggleLabel,'text','content.landing.cta.'+(paused?'play':'pause'));
            if (paused || !visible || document.hidden || failed) video.pause();
            else video.play().catch(()=>{paused=true;playback();});
        }
        toggle.addEventListener('click',()=>{paused=!paused;playback();});
        video.addEventListener('error',()=>{failed=true;section.querySelector('[data-landing-video-error]').hidden=false;playback();});
        if ('IntersectionObserver' in window) new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;playback();}).observe(stage);
        else { visible=true; }
        if ('ResizeObserver' in window) new ResizeObserver(resize).observe(stage);
        addEventListener('scroll',schedule,{passive:true});
        addEventListener('resize',resize,{passive:true});
        document.addEventListener('visibilitychange',playback);
        document.addEventListener('ui:languagechange',()=>{resize();playback();});
        reduced.addEventListener('change',()=>{if(reduced.matches)paused=true;resize();playback();});
        resize(); playback();
    }
    function contact(section) {
        const form=section.querySelector('[data-landing-form]');
        const inputs=[...form.querySelectorAll('input,textarea')];
        const status=form.querySelector('[data-landing-form-status]');
        let attempted=false;
        function validate(input) {
            const error=document.getElementById(input.id+'-error');
            const key=!input.value.trim()?'required':input.validity.typeMismatch?'invalid':null;
            if(key) UI.i18n.bind(error,'text','content.landing.contact.'+key); else UI.i18n.clear(error);
            input.setAttribute('aria-invalid',String(Boolean(key)));
            return !key;
        }
        form.addEventListener('submit', event=>{
            event.preventDefault(); attempted=true;
            const invalid=inputs.filter(input=>!validate(input));
            if(!invalid.length) UI.i18n.bind(status,'text','content.landing.contact.valid');
            else { UI.i18n.clear(status); invalid[0].focus(); }
        });
        inputs.forEach(input=>input.addEventListener('input',()=>{if(attempted)validate(input);UI.i18n.clear(status);}));
        // Enable only after cancellation is installed. No field names or network endpoint.
        form.querySelector('[data-landing-form-fields]').disabled=false;
        const plate=section.querySelector('.ui-landing-contact__plates');
        const beam=section.querySelector('[data-landing-beam]');
        const cone=section.querySelector('[data-landing-cone]');
        const core=section.querySelector('[data-landing-core]');
        const gradient=section.querySelector('#landing-beam-gradient');
        const title=section.querySelector('#landing-contact-title');
        const touch=matchMedia('(max-width:640px)');
        let progress=0,target=0,frame=0,last=0,geometry=null,hover=false,keyFocus=false,keyboard=false,touchLit=false;
        const smooth=x=>x*x*(3-2*x);
        function paint(value) {
            progress=clamp(value); if(!geometry)return;
            const g=geometry, lamp=smooth(clamp(progress/.18)), emerge=smooth(clamp((progress-.18)/.11)), growth=smooth(clamp((progress-.29)/.71));
            const travel=.075*emerge+.925*growth, start=g.x+6*g.scale, tip=start+(g.end-start)*travel, y=g.y+(g.ey-g.y)*travel;
            const width=Math.max(2,Math.min(touch.matches?48:92,g.h*.15,(g.end-start)*.16)*travel);
            const set=(name,value)=>section.style.setProperty('--ui-contact-'+name,value);
            set('cut-start',`${g.x+(35+45*growth)*g.scale}px`);set('cut-end',`${g.x+(49+45*growth)*g.scale}px`);
            set('lamp',lamp);set('beam',emerge);
            gradient.setAttribute('x1',start);gradient.setAttribute('x2',Math.max(start+1,tip));gradient.setAttribute('y1',g.y);gradient.setAttribute('y2',y);
            cone.setAttribute('d',`M ${start} ${g.y-3} L ${tip} ${y-width} L ${tip} ${y+width} L ${start} ${g.y+3} Z`);
            core.setAttribute('d',`M ${start} ${g.y-1.8} L ${tip} ${y-width*.29} L ${tip} ${y+width*.29} L ${start} ${g.y+1.8} Z`);
        }
        function measure() {
            const w=plate.clientWidth,h=plate.clientHeight;if(!w||!h)return;
            const scale=Math.max(w/1774,h/887), iw=1774*scale, ih=887*scale;
            const x=(w-iw)*(touch.matches?0:.2)+iw*.154,y=(h-ih)*.5+ih*.202;
            const box=section.getBoundingClientRect(),t=title.getBoundingClientRect();
            const end=touch.matches?Math.min(w+5,x+w*.68):Math.min(w*.76,Math.max(x+140,t.left-box.left+t.width*.43));
            geometry={w,h,scale,x,y,end,ey:y+Math.min(touch.matches?20:48,h*.058)};
            beam.setAttribute('viewBox',`0 0 ${w} ${h}`);
            for(const [key,value] of Object.entries({x,y,rx:iw*.052,ry:ih*.09})) section.style.setProperty('--ui-contact-'+key,value+'px');
            paint(progress);
        }
        function tick(now) {
            frame=0;const dt=Math.min(50,now-last);last=now;
            const diff=target-progress;paint(progress+Math.sign(diff)*Math.min(Math.abs(diff),dt/(diff>0?2800:1800)));
            if(Math.abs(target-progress)>.0001)frame=requestAnimationFrame(tick);
        }
        function sync() {
            const r=section.getBoundingClientRect(),offset=headerOffset();
            const shown=Math.max(0,Math.min(innerHeight,r.bottom)-Math.max(offset,r.top));
            const ratio=shown/Math.max(1,Math.min(r.height,innerHeight-offset));
            if(!shown){hover=false;keyFocus=false;touchLit=false;}else if(!fine.matches){if(ratio>=.42)touchLit=true;else if(ratio<.10)touchLit=false;}
            target=shown>0&&(fine.matches?(hover||keyFocus):touchLit)?1:0;
            if(reduced.matches){if(frame)cancelAnimationFrame(frame);frame=0;paint(1);return;}
            if(!frame&&Math.abs(target-progress)>.0001){last=performance.now();frame=requestAnimationFrame(tick);}
        }
        section.addEventListener('pointerenter',e=>{if(fine.matches&&e.pointerType!=='touch'){hover=true;sync();}});
        section.addEventListener('pointerleave',()=>{hover=false;sync();});
        addEventListener('keydown',e=>{if(e.key==='Tab')keyboard=true;});
        addEventListener('pointerdown',()=>{keyboard=false;keyFocus=false;sync();},{passive:true});
        section.addEventListener('focusin',()=>{if(keyboard){keyFocus=true;sync();}});
        section.addEventListener('focusout',e=>{if(!section.contains(e.relatedTarget)){keyFocus=false;sync();}});
        addEventListener('scroll',sync,{passive:true});addEventListener('resize',()=>{measure();sync();},{passive:true});
        document.addEventListener('ui:languagechange',measure);
        reduced.addEventListener('change',sync);fine.addEventListener('change',()=>{hover=false;touchLit=false;sync();});
        if('ResizeObserver' in window)new ResizeObserver(measure).observe(section);
        measure();sync();
    }
    document.querySelectorAll('[data-landing-cta]').forEach(cta);
    document.querySelectorAll('[data-landing-contact]').forEach(contact);
})();
