from pathlib import Path
import os
import shutil
from playwright.sync_api import sync_playwright
p=Path(__file__).resolve().parents[1]
fixture='''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="styles/motion-tokens.css"><link rel="stylesheet" href="styles/motion.css"><style>body{margin:0}section{height:120px}.spacer{height:1200px}</style><script src="scripts/scroll-trigger.js"></script></head><body><section id="hero" data-motion="reveal-left" data-scroll-trigger="load" style="--ep-motion-distance:100vw;--ep-motion-opacity:.15;--ep-motion-duration:1650ms;--ep-motion-delay:50ms">Hero</section><script>window.initialOpacity=getComputedStyle(document.querySelector('#hero')).opacity;</script><div class="spacer"></div><section id="once" data-motion="reveal-up" data-scroll-trigger="once">Once</section><div class="spacer"></div><section id="repeat" data-motion="scale-in" data-scroll-trigger="repeat">Repeat</section><div class="spacer"></div><section id="focus" data-motion="fade-in" data-scroll-trigger="once"><button>Focus</button></section><div class="spacer"></div></body></html>'''
def load(page):
    html=fixture
    for name in ['motion-tokens.css','motion.css']:
        html=html.replace(f'<link rel="stylesheet" href="styles/{name}">','<style>'+ (p/'styles'/name).read_text()+'</style>')
    html=html.replace('<script src="scripts/scroll-trigger.js"></script>','<script>'+ (p/'scripts/scroll-trigger.js').read_text()+'</script>')
    page.set_content(html)

if __name__ == '__main__':
    with sync_playwright() as pw:
        executable = os.environ.get('EP_TEST_BROWSER') or shutil.which('chromium') or shutil.which('google-chrome')
        browser=pw.chromium.launch(**({'executable_path':executable} if executable else {}),headless=True)
        page=browser.new_page(viewport={'width':1000,'height':700})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        load(page);assert page.evaluate('window.initialOpacity')=='0.15',page.evaluate('window.initialOpacity')
        page.wait_for_function("document.querySelector('#hero').dataset.epMotionState === 'visible'")
        assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
        page.locator('#once').scroll_into_view_if_needed();page.wait_for_function("document.querySelector('#once').dataset.epMotionState === 'visible'")
        page.locator('#repeat').scroll_into_view_if_needed();page.wait_for_function("document.querySelector('#repeat').dataset.epMotionState === 'visible'")
        page.evaluate('window.scrollTo(0,0)');page.wait_for_function("!document.querySelector('#repeat').hasAttribute('data-ep-motion-state')")
        assert page.locator('#once').get_attribute('data-ep-motion-state')=='visible'
        page.locator('#repeat').scroll_into_view_if_needed();page.wait_for_function("document.querySelector('#repeat').dataset.epMotionState === 'visible'")
        page.evaluate("window.EPMotion.replay(document.querySelector('#hero'))");assert page.locator('#hero').get_attribute('data-ep-motion-state')=='entering'
        page.wait_for_function("document.querySelector('#hero').dataset.epMotionState === 'visible'")
        page.locator('#focus button').focus();assert page.locator('#focus').get_attribute('data-ep-motion-state')=='visible'
        page.emulate_media(reduced_motion='reduce');page.wait_for_function("!document.documentElement.hasAttribute('data-ep-motion')")
        assert page.locator('#repeat').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
        assert not errors,errors
        print('PASS: initial style, load, scroll once, repeat/reentry, replay, focus, runtime reduced motion')
        page=browser.new_page(reduced_motion='reduce');load(page);assert page.evaluate('window.initialOpacity')=='1';assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='1';print('PASS: reduced motion on load')
        page=browser.new_page(java_script_enabled=False);load(page);assert page.locator('#hero').evaluate('(e)=>getComputedStyle(e).opacity')=='1';assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='1';print('PASS: without JavaScript')
        page=browser.new_page();page.evaluate('delete window.IntersectionObserver');load(page);assert page.evaluate('window.initialOpacity')=='1';assert page.locator('#once').evaluate('(e)=>getComputedStyle(e).opacity')=='1';print('PASS: without IntersectionObserver')
        browser.close()
