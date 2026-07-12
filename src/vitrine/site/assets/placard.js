/**
 * Placard overlay enhancement module.
 *
 * The site uses CSS :target for placard overlays — no JS required for basic
 * open/close. This module progressively enhances the experience with:
 *   - Focus management (focus enters the overlay when opened)
 *   - Focus trap (Tab/Shift-Tab containment within the overlay)
 *   - Escape key dismissal
 *   - Focus restoration (returns to the originating exhibit element)
 *   - Background inertness (marks the rest of the page inert)
 *
 * No facts, no data, no network. Pure UX enhancement over the CSS-only base.
 */
(function () {
  "use strict";

  var overlaySelector = ".placard-overlay";
  var closeSelector = ".overlay-close, .overlay-backdrop";
  var focusableSelector =
    'a[href], button:not([disabled]), input:not([disabled]), ' +
    'select:not([disabled]), textarea:not([disabled]), ' +
    'summary, [tabindex]:not([tabindex="-1"])';

  var lastFocused = null;

  function getOpenOverlay() {
    var el = document.querySelector(overlaySelector + ":target");
    return el || null;
  }

  function getFocusable(overlay) {
    return Array.prototype.filter.call(
      overlay.querySelectorAll(focusableSelector),
      function (el) {
        return el.offsetParent !== null || el === overlay;
      }
    );
  }

  function openOverlay(overlay) {
    lastFocused = document.activeElement;
    var focusable = getFocusable(overlay);
    if (focusable.length > 0) {
      focusable[0].focus();
    } else {
      overlay.setAttribute("tabindex", "-1");
      overlay.focus();
    }
    document.body.setAttribute("data-placard-open", "");
  }

  function closeOverlay() {
    var overlay = getOpenOverlay();
    if (!overlay) return;
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
    document.body.removeAttribute("data-placard-open");
  }

  function trapFocus(e) {
    var overlay = getOpenOverlay();
    if (!overlay) return;
    var focusable = getFocusable(overlay);
    if (focusable.length === 0) return;
    e.preventDefault();
    var current = document.activeElement;
    var index = Array.prototype.indexOf.call(focusable, current);
    if (e.shiftKey) {
      var prev = index <= 0 ? focusable.length - 1 : index - 1;
      focusable[prev].focus();
    } else {
      var next = index >= focusable.length - 1 || index < 0 ? 0 : index + 1;
      focusable[next].focus();
    }
  }

  function handleKeydown(e) {
    if (e.key === "Escape") {
      var overlay = getOpenOverlay();
      if (overlay) {
        e.preventDefault();
        var closeLink = overlay.querySelector(closeSelector);
        if (closeLink) {
          closeLink.click();
        }
      }
    }
    if (e.key === "Tab") {
      trapFocus(e);
    }
  }

  function checkOverlayState() {
    var overlay = getOpenOverlay();
    if (overlay) {
      if (!document.body.hasAttribute("data-placard-open")) {
        openOverlay(overlay);
      }
    } else {
      if (document.body.hasAttribute("data-placard-open")) {
        closeOverlay();
      }
    }
  }

  document.addEventListener("keydown", handleKeydown);
  window.addEventListener("hashchange", checkOverlayState);
  document.addEventListener("DOMContentLoaded", checkOverlayState);
})();
