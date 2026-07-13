/**
 * Progressive interaction enhancements for the static museum.
 *
 * The HTML remains the source of truth and CSS :target remains the no-script
 * fallback. This module owns interaction state only: focus, Escape dismissal,
 * background inertness, and returning visitors to the exhibit they opened.
 */
(() => {
  "use strict";

  const overlaySuffix = "--modal";
  const page = document.querySelector(".wrap");
  let active = null;
  let origin = null;

  const focusableSelector = [
    "a[href]",
    "button:not([disabled])",
    "details > summary:first-of-type",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  function focusableElements(overlay) {
    return [...overlay.querySelectorAll(focusableSelector)].filter(
      (element) => !element.hasAttribute("inert") && element.getClientRects().length > 0,
    );
  }

  function closeOverlay({ restoreFocus = true } = {}) {
    if (!active) return;

    const closing = active;
    active = null;
    closing.removeAttribute("aria-modal");
    closing.removeEventListener("keydown", containFocus);
    if (page) page.inert = false;

    if (restoreFocus && origin?.isConnected) origin.focus();
    origin = null;
  }

  function dismissOverlay() {
    // closeOverlay() first: removes aria-modal, de-inerts .wrap, and restores
    // focus to the originating trigger. Then a real same-document hash
    // navigation updates CSS :target (pushState does not — :target only
    // recalculates on fragment navigation, so the overlay would stay
    // display:flex after Escape/close/backdrop). The hashchange this fires
    // is a no-op in syncWithHash (active is null).
    closeOverlay();
    location.hash = "#dismissed";
  }

  function containFocus(event) {
    if (event.key === "Escape") {
      event.preventDefault();
      dismissOverlay();
      return;
    }
    if (event.key !== "Tab" || !active) return;

    const elements = focusableElements(active);
    if (!elements.length) {
      event.preventDefault();
      active.focus();
      return;
    }
    const first = elements[0];
    const last = elements[elements.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  function openOverlay(overlay) {
    if (active === overlay) return;
    closeOverlay({ restoreFocus: false });

    active = overlay;
    overlay.setAttribute("aria-modal", "true");
    overlay.addEventListener("keydown", containFocus);
    if (page) page.inert = true;

    const closeButton = overlay.querySelector(".overlay-close");
    (closeButton || overlay).focus();
  }

  function syncWithHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = id.endsWith(overlaySuffix) ? document.getElementById(id) : null;
    if (target?.classList.contains("placard-overlay")) {
      openOverlay(target);
    } else {
      closeOverlay({ restoreFocus: false });
    }
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");
    if (!link) return;
    const href = link.getAttribute("href") || "";
    if (href.startsWith("#") && href.endsWith(overlaySuffix)) origin = link;
    if (active && (link.classList.contains("overlay-close") || link.classList.contains("overlay-backdrop"))) {
      event.preventDefault();
      dismissOverlay();
    }
  });

  window.addEventListener("hashchange", syncWithHash);
  window.addEventListener("popstate", syncWithHash);
  syncWithHash();
})();
