/*
 * Responsibility: Demonstrate the canonical send-state API on the isolated Style Guide.
 * Boundaries: No form transport, preferences, shared UI logic, or simulated network confirmation.
 */
(() => {
    'use strict';
    const showColors = () => document.querySelectorAll('[data-guide-color]').forEach(node => { node.textContent = getComputedStyle(document.documentElement).getPropertyValue(node.dataset.guideColor).trim(); });
    showColors();
    document.addEventListener('ui:themechange',showColors);
    const root = document.querySelector('[data-guide-send-demo]');
    if (!root || root.closest('form') || root.querySelector('form')) return;
    const choice = root.querySelector('[data-guide-send-choice]');
    const send = root.querySelector('[data-ui-send]');
    const update = () => {
        UI.actions.setSendState(send, 'idle');
        if (choice.value === 'success') UI.actions.setSendState(send, 'pending');
        // Local fixture acknowledgement only; no transport exists in this isolated demo.
        UI.actions.setSendState(send, choice.value, choice.value === 'success' ? {confirmed:true} : {});
    };
    choice.addEventListener('change', update);
    send.querySelector('button').addEventListener('click', event => {
        event.preventDefault(); choice.value = 'pending'; update();
    });
})();
