"""Responsibility: verify motion first paint, triggers, replay and fallbacks."""
from support import load_page, launch_browser, new_page
from playwright.sync_api import sync_playwright
fixture='''<section id="hero" data-motion="reveal-left" data-scroll-trigger="load" style="--ui-motion-distance:100vw;--ui-motion-opacity:.15;--ui-motion-duration:1650ms;--ui-motion-delay:50ms">Hero</section><script>window.initialOpacity=getComputedStyle(document.querySelector('#hero')).opacity;</script><div class="spacer"></div><section id="once" data-motion="reveal-up" data-scroll-trigger="once">Once</section><div class="spacer"></div><section id="repeat" data-motion="scale-in" data-scroll-trigger="repeat">Repeat</section><div class="spacer"></div><section id="focus" data-motion="fade-in" data-scroll-trigger="once"><button>Focus</button></section><div class="spacer"></div>'''
def load(page):
    load_page(page, fixture, css='body{margin:0}section{height:120px}.spacer{height:1200px}')

if __name__ == '__main__':
    with sync_playwright() as pw:

        browser=launch_browser(pw)
        page=new_page(browser, viewport={'width':1000,'height':700})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        load(page);assert page.evaluate('window.initialOpacity')=='0.15',page.evaluate('window.initialOpacity')
        page.wait_for_function("document.querySelector('#hero').dataset.uiMotionState === 'visible'")
        assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
        page.locator('#once').scroll_into_view_if_needed();page.wait_for_function("document.querySelector('#once').dataset.uiMotionState === 'visible'")
        page.locator('#repeat').scroll_into_view_if_needed();page.wait_for_function("document.querySelector('#repeat').dataset.uiMotionState === 'visible'")
        page.evaluate('window.scrollTo(0,0)');page.wait_for_function("!document.querySelector('#repeat').hasAttribute('data-ui-motion-state')")
        assert page.locator('#once').get_attribute('data-ui-motion-state')=='visible'
        page.locator('#repeat').scroll_into_view_if_needed();page.wait_for_function("document.querySelector('#repeat').dataset.uiMotionState === 'visible'")
        page.evaluate("window.UI.motion.replay(document.querySelector('#hero'))");assert page.locator('#hero').get_attribute('data-ui-motion-state')=='entering'
        page.wait_for_function("document.querySelector('#hero').dataset.uiMotionState === 'visible'")
        page.locator('#focus button').focus();assert page.locator('#focus').get_attribute('data-ui-motion-state')=='visible'
        page.emulate_media(reduced_motion='reduce');page.wait_for_function("!document.documentElement.hasAttribute('data-ui-motion')")
        assert page.locator('#repeat').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
        assert not errors,errors
        print('PASS: initial style, load, scroll once, repeat/reentry, replay, focus, runtime reduced motion')
        page=new_page(browser, reduced_motion='reduce');load(page);assert page.evaluate('window.initialOpacity')=='1';assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='1';print('PASS: reduced motion on load')
        page=new_page(browser, java_script_enabled=False);load(page);assert page.locator('#hero').evaluate('(e)=>getComputedStyle(e).opacity')=='1';assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='1';print('PASS: without JavaScript')
        page=new_page(browser);page.add_init_script('delete window.IntersectionObserver');load(page);assert page.evaluate('window.initialOpacity')=='1';assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='1';print('PASS: without IntersectionObserver')
        browser.close()
