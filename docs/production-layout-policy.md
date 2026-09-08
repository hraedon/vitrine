# Production layout and response policy

The September 2026 room-selector regression was a delivery mismatch, alongside
an independent decade-card layout defect. The browser tests served plain local
HTTP, while nginx sent a Content Security Policy with `default-src 'self'`.
That policy blocked generated `style` attributes, including the selector's
`--room-count` custom property. Its CSS grid declaration consequently became
invalid and the thirteen decades occupied a single vertical column. Checking
page overflow did not detect the error.

The same policy also blocked tier colors, chart proportions, and some SVG text
alignment and glyph opacity. These are authored build outputs; the site accepts
no visitor-provided styling. The production policy now permits style attributes
with `style-src-attr 'unsafe-inline'`. This is deliberately scoped to attributes:
inline style elements and scripts remain blocked, and external stylesheets and
scripts remain restricted to the same origin by `default-src 'self'`.
The [W3C CSP Level 3 definition](https://www.w3.org/TR/CSP3/#directive-style-src-attr)
specifies this separation. Browsers without that directive's support retain the
stricter fallback, so navigation must not depend on an inline custom property.

The browser fixture reads nginx's literal `add_header` declarations and sends
those exact headers with every test response. Both enhanced and JavaScript-free
contexts explicitly enforce CSP. Tests check a generated tier chip and SVG label
against computed browser styles, and verify that allowing a style attribute does
not allow an inline style element or script. Geometry tests must inspect the
component itself: page-width checks cannot detect overflowing text inside a tile
or a selector that consumes excessive vertical space.

When changing response headers or inline rendering, run the browser suite against
the current generated site. Matching deployed HTML and CSS bytes verifies
freshness, but does not establish that the browser is permitted to apply them.
