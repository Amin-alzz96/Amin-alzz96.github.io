/* Accessible tabs with shareable section URLs and bookshelf navigation. */
const tabs = [...document.querySelectorAll('[role="tab"]')];
const panels = [...document.querySelectorAll('[role="tabpanel"]')];

function activate(name, { updateHash = true, focusTab = false } = {}) {
  // Section hashes stay separate from panel IDs to avoid native anchor scrolling.
  const selected = tabs.find((tab) => tab.dataset.tab === name) || tabs[0];
  if (!selected) return;
  name = selected.dataset.tab;
  tabs.forEach((tab) => {
    const active = tab === selected;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
  });
  panels.forEach((panel) => { panel.hidden = panel.id !== 'panel-' + name; });
  if (updateHash && location.hash !== '#' + name) {
    history.pushState(null, '', '#' + name);
  }
  if (focusTab) selected.focus({ preventScroll: true });
  selected.scrollIntoView({ inline: 'nearest', block: 'nearest', behavior: 'instant' });
  window.scrollTo({ top: 0, behavior: 'instant' });
}

tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => activate(tab.dataset.tab));
  tab.addEventListener('keydown', (event) => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    activate(tabs[next].dataset.tab, { focusTab: true });
  });
});
window.addEventListener('hashchange', () => {
  if (location.hash === '#main-content') return;
  activate(location.hash.slice(1), { updateHash: false });
});
document.addEventListener('keydown', (event) => {
  const target = event.target;
  if (target.isContentEditable || target.closest('input, textarea, select') || event.metaKey || event.ctrlKey || event.altKey) return;
  if (!/^[1-6]$/.test(event.key)) return;
  activate(tabs[Number(event.key) - 1].dataset.tab, { focusTab: true });
});
activate(location.hash.slice(1) || 'about', { updateHash: false });
const shelf = document.getElementById('shelf');
document.getElementById('shelf-prev')?.addEventListener('click', () => shelf?.scrollBy({ left: -240 }));
document.getElementById('shelf-next')?.addEventListener('click', () => shelf?.scrollBy({ left: 240 }));
