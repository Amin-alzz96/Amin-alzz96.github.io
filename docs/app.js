/* Tab navigation with URL-hash deep linking + bookshelf scrolling. */

const tabs = document.querySelectorAll(".tab");
const panels = document.querySelectorAll(".panel");

function activate(tabName, updateHash = true) {
  // Panel ids are namespaced ("panel-books") so the URL hash ("#books") never
  // matches a DOM id — otherwise the browser's native anchor-scroll fights the tabs.
  const valid = [...panels].some((p) => p.id === "panel-" + tabName);
  if (!valid) tabName = "about";

  tabs.forEach((t) => {
    const active = t.dataset.tab === tabName;
    t.setAttribute("aria-selected", String(active));
    if (active) t.scrollIntoView({ inline: "center", block: "nearest" });
  });
  panels.forEach((p) => (p.hidden = p.id !== "panel-" + tabName));

  if (updateHash) history.replaceState(null, "", "#" + tabName);
  window.scrollTo({ top: 0, behavior: "instant" });
}

tabs.forEach((t) => t.addEventListener("click", () => activate(t.dataset.tab)));

window.addEventListener("hashchange", () => activate(location.hash.slice(1), false));

// Keyboard shortcuts 1-6 switch tabs (ignored while typing in inputs)
document.addEventListener("keydown", (e) => {
  if (e.target.matches("input, textarea") || e.metaKey || e.ctrlKey || e.altKey) return;
  const idx = parseInt(e.key, 10) - 1;
  if (idx >= 0 && idx < tabs.length) activate(tabs[idx].dataset.tab);
});

// Initial tab from URL hash
activate(location.hash.slice(1) || "about", false);

// Bookshelf prev/next scrolling
const shelf = document.getElementById("shelf");
document.getElementById("shelf-prev")?.addEventListener("click", () => shelf.scrollBy({ left: -240 }));
document.getElementById("shelf-next")?.addEventListener("click", () => shelf.scrollBy({ left: 240 }));
