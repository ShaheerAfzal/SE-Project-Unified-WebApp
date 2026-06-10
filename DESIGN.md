# DESIGN.md — Stitch Retro Cassette Unified Interface

> **Agent Instructions — Read Before Making Any Changes**
>
> 1. **Audit before you edit.** Before writing a single line of code, open and read every existing `.html`, `.css`, and `.js` file in the project. Understand what is already there. **Do not create new files** unless one genuinely does not exist — always modify the existing files in place.
> 2. **Read the Django REST backend first — once, thoroughly.** Before touching any frontend file, do a full read-through of the Python/Django backend. This means:
>    - Read all `views.py` files to understand every API endpoint, what it expects (method, URL, request body shape, auth headers), and what it returns (response structure, status codes).
>    - Read all `serializers.py` files to understand the exact field names, types, and validation rules the backend enforces.
>    - Read all `urls.py` files (project-level and app-level) to map every URL pattern to its view.
>    - Read `models.py` to understand the data shapes flowing through the API.
>    - Read `settings.py` for CORS configuration, authentication backends, middleware, and any environment-specific flags that affect API behaviour.
>    - Identify every place in the frontend HTML/JS where `fetch()`, `XMLHttpRequest`, `axios`, or any AJAX call is made. Cross-reference each one against the backend endpoints you have read. Confirm the URL, HTTP method, headers (e.g. `Content-Type`, `X-CSRFToken`, `Authorization`), and payload shape all match exactly.
>    - **Do not proceed with any UI edits until this mapping is complete.** If any frontend call does not have a matching backend endpoint, flag it as a pre-existing issue and do not make it worse.
> 3. **No backend regressions.** After any UI change, verify that all existing API calls, event handlers, data bindings, form submissions, WebSocket connections, and JavaScript logic remain intact and error-free. If a Django REST endpoint expects a specific field name in the request body, that name must not be altered in the frontend — even if renaming it would improve readability. If a change risks breaking backend integration, add a comment in the code explaining why it is safe before applying it.
> 4. **Uniformity is mandatory.** All modules — including Shipment Engine — must share the same color tokens, typography scale, spacing units, CRT effects, and component patterns defined in this document. Divergence between modules is a bug, not a style choice. See the **Shipment Engine Alignment** section for the specific issues to fix.
> 5. **Never introduce regressions.** Run through the UI flow of every affected panel after changes. If something that worked before is now broken, revert and re-approach.

---

## 1. Brand & Aesthetic

**Theme:** Cassette Futurism — a vision of the future rendered through the tactile lens of late-1970s and 1980s industrial computing. The interface should feel like operating a hardened mainframe terminal in a high-stakes subterranean facility.

**Aesthetic pillars:**
- **Industrial Brutalism:** Hard edges, mechanical metaphors, zero softness.
- **CRT Fidelity:** Scanline overlays, phosphor glow (text-shadow), chromatic aberration tinting.
- **Hardware Metaphors:** Panels are chassis plates. Inputs are recessed ports. Buttons have mechanical travel. LEDs indicate status. Screws are visible in corners.
- **High Information Density:** Dense readouts are preferred. Whitespace is structural, not decorative.

**Target users:** Power users, developers, and operators who value lo-fi grit and data-dense environments.

---

## 2. Color Tokens

All modules share the **Unified Tools** palette (from `unified_tools_interface/DESIGN.md`). These are the canonical token values. Every file must use these — no module may deviate.

### Surface & Background

| Token | Value | Usage |
|---|---|---|
| `background` | `#131313` | Page-level background (Obsidian) |
| `surface` | `#131313` | Base surface |
| `surface-dim` | `#131313` | Dimmed surface variant |
| `surface-container-lowest` | `#0e0e0e` | Deepest recessed level (Level 2 inputs) |
| `surface-container-low` | `#1c1b1b` | Low elevation panels |
| `surface-container` | `#201f1f` | Standard panel background (Level 1 chassis) |
| `surface-container-high` | `#2a2a2a` | Elevated panel backgrounds |
| `surface-container-highest` | `#353534` | Highest contrast surface layer |
| `surface-bright` | `#3a3939` | Active/highlighted surface |
| `surface-variant` | `#353534` | Variant surface for differentiation |

### On-Surface & Text

| Token | Value | Usage |
|---|---|---|
| `on-surface` | `#e5e2e1` | Primary readable text |
| `on-surface-variant` | `#d7c4ac` | Secondary/muted text, inactive nav items |
| `on-background` | `#e5e2e1` | Text directly on background |
| `inverse-surface` | `#e5e2e1` | Inverse text contexts |
| `inverse-on-surface` | `#313030` | Text on inverse surfaces |

### Primary — Amber Phosphor

| Token | Value | Usage |
|---|---|---|
| `primary` | `#ffd597` | Headlines, interactive text, active states |
| `on-primary` | `#432c00` | Text/icons on filled primary backgrounds |
| `primary-container` | `#ffb000` | Filled button backgrounds, active nav highlight |
| `on-primary-container` | `#6a4700` | Text on primary-container |
| `primary-fixed` | `#ffddaf` | Fixed primary variant |
| `primary-fixed-dim` | `#ffba43` | Dimmed fixed primary, LED amber glow center |
| `on-primary-fixed` | `#281800` | Text on primary-fixed |
| `on-primary-fixed-variant` | `#614000` | Variant text on primary-fixed |
| `inverse-primary` | `#805600` | Inverse primary (dark contexts) |
| `surface-tint` | `#ffba43` | Tinting overlay for elevated surfaces |

> **⚠ Shipment Engine Note:** The Shipment Engine currently sets `primary` to `#ffb000` instead of the canonical `#ffd597`. This must be corrected. Use `primary-container` (`#ffb000`) for filled/active states, and `primary` (`#ffd597`) for text and ghost interactive states.

### Secondary — Phosphor Green

| Token | Value | Usage |
|---|---|---|
| `secondary` | `#9eff8b` | Success states, data readouts, "safe" status |
| `on-secondary` | `#003a02` | Text on secondary backgrounds |
| `secondary-container` | `#00ec1c` | Filled secondary backgrounds |
| `on-secondary-container` | `#006505` | Text on secondary-container |
| `secondary-fixed` | `#76ff65` | Fixed secondary variant |
| `secondary-fixed-dim` | `#00e61b` | Dimmed fixed secondary |
| `on-secondary-fixed` | `#002201` | Text on secondary-fixed |
| `on-secondary-fixed-variant` | `#005303` | Variant text on secondary-fixed |

### Tertiary — Alert Orange

| Token | Value | Usage |
|---|---|---|
| `tertiary` | `#ffd1c0` | Tertiary readouts |
| `on-tertiary` | `#5a1c00` | Text on tertiary |
| `tertiary-container` | `#ffab8a` | Warning/alert backgrounds |
| `on-tertiary-container` | `#8a3000` | Text on tertiary-container |
| `tertiary-fixed` | `#ffdbce` | Fixed tertiary variant |
| `tertiary-fixed-dim` | `#ffb599` | Dimmed tertiary fixed |
| `on-tertiary-fixed` | `#370e00` | Text on tertiary-fixed |
| `on-tertiary-fixed-variant` | `#7f2b00` | Variant text on tertiary-fixed |

### Structural & Error

| Token | Value | Usage |
|---|---|---|
| `outline` | `#9f8e78` | Panel borders, dividers |
| `outline-variant` | `#524533` | Subtle borders, inactive separators |
| `error` | `#ffb4ab` | Error text/icons |
| `on-error` | `#690005` | Text on error backgrounds |
| `error-container` | `#93000a` | Error state backgrounds |
| `on-error-container` | `#ffdad6` | Text on error-container |

### Tailwind Config (Canonical)

All modules must include this exact Tailwind color extension in their `<script id="tailwind-config">`:

```javascript
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "background": "#131313",
        "surface": "#131313",
        "surface-dim": "#131313",
        "surface-bright": "#3a3939",
        "surface-container-lowest": "#0e0e0e",
        "surface-container-low": "#1c1b1b",
        "surface-container": "#201f1f",
        "surface-container-high": "#2a2a2a",
        "surface-container-highest": "#353534",
        "surface-variant": "#353534",
        "surface-tint": "#ffba43",
        "on-surface": "#e5e2e1",
        "on-surface-variant": "#d7c4ac",
        "on-background": "#e5e2e1",
        "inverse-surface": "#e5e2e1",
        "inverse-on-surface": "#313030",
        "primary": "#ffd597",
        "on-primary": "#432c00",
        "primary-container": "#ffb000",
        "on-primary-container": "#6a4700",
        "primary-fixed": "#ffddaf",
        "primary-fixed-dim": "#ffba43",
        "on-primary-fixed": "#281800",
        "on-primary-fixed-variant": "#614000",
        "inverse-primary": "#805600",
        "secondary": "#9eff8b",
        "on-secondary": "#003a02",
        "secondary-container": "#00ec1c",
        "on-secondary-container": "#006505",
        "secondary-fixed": "#76ff65",
        "secondary-fixed-dim": "#00e61b",
        "on-secondary-fixed": "#002201",
        "on-secondary-fixed-variant": "#005303",
        "tertiary": "#ffd1c0",
        "on-tertiary": "#5a1c00",
        "tertiary-container": "#ffab8a",
        "on-tertiary-container": "#8a3000",
        "tertiary-fixed": "#ffdbce",
        "tertiary-fixed-dim": "#ffb599",
        "on-tertiary-fixed": "#370e00",
        "on-tertiary-fixed-variant": "#7f2b00",
        "error": "#ffb4ab",
        "on-error": "#690005",
        "error-container": "#93000a",
        "on-error-container": "#ffdad6",
        "outline": "#9f8e78",
        "outline-variant": "#524533"
      }
    }
  }
}
```

---

## 3. Typography

The system uses a strict monospaced-only type stack. All fonts must be loaded from Google Fonts. The canonical font load tag is:

```html
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&family=JetBrains+Mono:wght@400;700&family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet"/>
```

### Type Scale

| Role | Font | Size | Weight | Line Height | Letter Spacing | Usage |
|---|---|---|---|---|---|---|
| `headline-lg` | Space Mono | 32px | 700 | 40px | 0.05em | Page-level titles, module headers |
| `headline-md` | Space Mono | 24px | 700 | 32px | 0.02em | Panel section headers |
| `body-lg` | JetBrains Mono | 16px | 400 | 24px | — | Primary readable content, form fields |
| `body-md` | JetBrains Mono | 14px | 400 | 20px | — | Secondary content, descriptions |
| `label-caps` | Space Mono | 12px | 700 | 16px | 0.1em + UPPERCASE | Hardware labels, nav items, button text |
| `code-sm` | JetBrains Mono | 12px | 400 | 16px | — | Code snippets, terminal output, data readouts |

### Tailwind Font Config

```javascript
fontFamily: {
  "headline-lg": ["Space Mono", "monospace"],
  "headline-md": ["Space Mono", "monospace"],
  "body-lg":     ["JetBrains Mono", "monospace"],
  "body-md":     ["JetBrains Mono", "monospace"],
  "label-caps":  ["Space Mono", "monospace"],
  "code-sm":     ["JetBrains Mono", "monospace"]
},
fontSize: {
  "headline-lg": ["32px", { lineHeight: "40px", letterSpacing: "0.05em", fontWeight: "700" }],
  "headline-md": ["24px", { lineHeight: "32px", letterSpacing: "0.02em", fontWeight: "700" }],
  "body-lg":     ["16px", { lineHeight: "24px", fontWeight: "400" }],
  "body-md":     ["14px", { lineHeight: "20px", fontWeight: "400" }],
  "label-caps":  ["12px", { lineHeight: "16px", letterSpacing: "0.1em", fontWeight: "700" }],
  "code-sm":     ["12px", { lineHeight: "16px", fontWeight: "400" }]
}
```

### Typography Rules

- All labels and nav items: **UPPERCASE**, `font-label-caps text-label-caps`.
- Headlines use amber phosphor glow: `crt-glow-amber` class (text-shadow).
- Body text uses `on-surface` (`#e5e2e1`) by default; never raw white.
- Muted/secondary text uses `on-surface-variant` (`#d7c4ac`).
- Active/interactive text uses `primary` (`#ffd597`).
- Data readouts and terminal output use `code-sm` with `crt-glow-amber` or `crt-glow-green` depending on context (amber = input/warning, green = confirmed/output).

> **⚠ Shipment Engine Note:** The Shipment Engine defines `body-md` and `body-lg` mapped only to `Space Mono`, omitting `JetBrains Mono` and `Courier Prime`. This must be updated to match the full font stack above. All form inputs use `font-code-sm` which is correct — do not change that.

---

## 4. Spacing

All spacing is a multiple of the **4px base unit**.

| Token | Value | Usage |
|---|---|---|
| `unit` | 4px | Base grid unit |
| `gutter` | 16px | Internal panel padding, nav padding |
| `margin` | 24px | Outer margins, section separation |
| `sidebar_width` | 240px | Fixed left navigation rail width |
| `panel_padding` | 20px | Standard chassis panel inner padding |

### Tailwind Spacing Extension

```javascript
spacing: {
  "unit":          "4px",
  "gutter":        "16px",
  "margin":        "24px",
  "sidebar_width": "240px",
  "panel_padding": "20px"
}
```

### Layout Rules

- **12-column grid** on desktop (1024px+), **2-column** on tablet (600–1023px), **1-column** on mobile (< 600px).
- All panels snap to the 4px grid. Avoid arbitrary pixel values.
- Main content area begins at `left-[sidebar_width]` to account for the fixed sidebar.
- Content panels must have visible 2px solid borders (`border-2 border-outline-variant`).
- Related data points use tighter spacing; distinct hardware modules use larger margins.

---

## 5. CRT & Atmospheric Effects

These effects must be applied globally in every module. They are defined as custom CSS classes and must be present in the `<style>` block of every page.

### Required CSS Classes

```css
/* CRT Scanlines — fixed overlay, full viewport */
.crt-scanlines {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background:
    linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
    linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
  background-size: 100% 4px, 3px 100%;
  pointer-events: none;
  z-index: 100;
  opacity: 0.8;
}

/* Phosphor glow — Amber */
.crt-glow-amber { text-shadow: 0 0 6px rgba(255, 176, 0, 0.8); }

/* Phosphor glow — Green */
.crt-glow-green { text-shadow: 0 0 8px rgba(158, 255, 139, 0.9); }

/* Glow — box-shadow variants for interactive elements */
.glow-primary  { box-shadow: 0 0 10px rgba(255, 176, 0, 0.3); }
.glow-secondary { box-shadow: 0 0 10px rgba(158, 255, 139, 0.3); }
.glow-error    { box-shadow: 0 0 10px rgba(255, 180, 171, 0.3); }
```

### Required HTML (every page body, first child)

```html
<div class="crt-scanlines"></div>
```

### Body Tag

```html
<body class="bg-background text-on-surface flex font-body-md overflow-hidden h-screen selection:bg-primary selection:text-on-primary">
```

---

## 6. Shape Language

- **All corners: 0px radius** (sharp, no rounding).
- Tailwind's `rounded-*` classes must not be used on structural components.
- Exception: LED indicators (8×8px) may be circular (`rounded-full`).
- Exception: Screw-head decorations are circular with a diagonal slot.
- Optional: A single 45-degree chamfer (clipped corner) may be used on panel headers for the sci-fi hardware aesthetic.

---

## 7. Elevation & Depth

Depth is communicated via **tonal layering** and **internal bevels**, not drop shadows.

| Level | Color | Usage |
|---|---|---|
| Level 0 (Base) | `#131313` (`background`) | Page background |
| Level 1 (Chassis) | `#201f1f` (`surface-container`) | Panel surfaces |
| Level 2 (Recessed) | `#0e0e0e` (`surface-container-lowest`) | Input fields, inset readouts |

### Chassis Panel

```css
.chassis-panel {
  background-color: #1A1A1A;
  box-shadow: inset 1px 1px 0px rgba(255, 255, 255, 0.1), 2px 2px 0px rgba(0,0,0,0.5);
  border: 2px solid theme('colors.outline-variant');
}
```

### Recessed Input

```css
.recessed-input {
  background-color: #0e0e0e;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.8), inset 0 0 10px rgba(0,0,0,0.5);
  border: 1px solid theme('colors.outline-variant');
  border-bottom: 1px solid theme('colors.outline');
}
```

### Hardware Panel (raised)

```css
.hardware-panel {
  background-color: theme('colors.surface-container-high');
  border: 2px solid theme('colors.outline-variant');
  box-shadow:
    inset 2px 2px 0px 0px rgba(255, 255, 255, 0.05),
    inset -2px -2px 0px 0px rgba(0, 0, 0, 0.5);
  position: relative;
}
```

### Hardware Vent Texture

```css
.hardware-vent {
  background-image: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    theme('colors.surface-container-lowest') 2px,
    theme('colors.surface-container-lowest') 4px
  );
}
```

---

## 8. Components

### Navigation Sidebar

The sidebar is a **fixed left rail**, `w-sidebar_width` (240px) wide, full viewport height.

**Structure:**
1. **Header zone** — `UNIFIED TOOLS` (or module name) in `headline-lg` + `crt-glow-amber`, version string in `label-caps`, optional operator portrait (grayscale, `border-2 border-outline-variant`).
2. **Screw corner decorations** — `+` symbols at top-left and top-right of the header using `material-symbols-outlined: add`.
3. **Nav items** — stacked `<a>` or `<div>` elements, each with an icon + `label-caps` uppercase label.

**Inactive nav item:**
```html
<a class="flex items-center gap-2 text-on-surface-variant border border-outline-variant p-2 mb-2 hover:bg-primary hover:text-on-primary transition-all duration-75 active:translate-x-0.5 active:translate-y-0.5 font-label-caps text-label-caps" href="#">
  <span class="material-symbols-outlined text-[20px]">icon_name</span>
  LABEL
</a>
```

**Active nav item:**
```html
<a class="flex items-center gap-2 bg-primary-container text-on-primary-container border-2 border-primary p-2 mb-2 shadow-[0_0_10px_rgba(255,176,0,0.5)] font-label-caps text-label-caps active:translate-x-0.5 active:translate-y-0.5" href="#">
  <span class="material-symbols-outlined text-[20px]">icon_name</span>
  LABEL
  <span class="ml-auto w-2 h-2 led-amber block border border-on-primary"></span>
</a>
```

### Mechanical Buttons (`.mech-btn`)

```css
.mech-btn {
  border: 1px solid theme('colors.primary');
  background-color: #1A1A1A;
  box-shadow: inset 1px 1px 0px rgba(255,255,255,0.1), 2px 2px 0px rgba(0,0,0,0.8);
  transition: all 0.1s ease;
}
.mech-btn:hover {
  background-color: theme('colors.primary');
  color: theme('colors.on-primary');
  box-shadow: inset 1px 1px 0px rgba(255,255,255,0.3), 2px 2px 0px rgba(0,0,0,0.8);
}
.mech-btn:active {
  transform: translate(2px, 2px);
  box-shadow: none;
}
```

**Primary CTA button** (compile, generate, submit):
```html
<button class="px-8 py-2 bg-primary-container text-on-primary font-label-caps text-label-caps font-bold flex items-center shadow-[0_0_15px_rgba(255,176,0,0.6)] hover:bg-primary-fixed-dim hover:shadow-[0_0_20px_rgba(255,176,0,0.8)] transition-all border-2 border-primary">
  <span class="material-symbols-outlined mr-2 text-[18px]">icon_name</span>
  BUTTON LABEL
</button>
```

### Input Fields

All inputs use the **recessed-input** class. Labels float above the border using absolute positioning.

```html
<div class="relative recessed-input p-2 mt-4">
  <label class="absolute -top-3 left-2 bg-background px-1 font-label-caps text-[10px] text-primary-fixed-dim border border-outline-variant">
    FIELD_LABEL
  </label>
  <input class="w-full bg-transparent border-none focus:ring-0 text-primary font-code-sm py-2 px-1 focus:outline-none placeholder-outline-variant/50 crt-glow-amber"
         placeholder="Enter value..." type="text"/>
</div>
```

### Status LEDs

```css
.led-green {
  background: radial-gradient(circle, theme('colors.secondary') 20%, #005303 100%);
  box-shadow: 0 0 8px theme('colors.secondary');
}
.led-amber {
  background: radial-gradient(circle, theme('colors.primary-fixed-dim') 20%, #6a4700 100%);
  box-shadow: 0 0 8px theme('colors.primary-fixed-dim');
}
.led-red {
  background: radial-gradient(circle, theme('colors.error') 20%, theme('colors.error-container') 100%);
  box-shadow: 0 0 8px theme('colors.error');
}
```

LED usage: `<span class="w-2 h-2 led-green rounded-none block"></span>` (note: `rounded-none` — LEDs in panel headers stay square; only standalone indicators may be circular).

### Chassis Panel Card

Every content card must have:
1. The `.chassis-panel` class.
2. A header section with a 1px bottom border containing an uppercase label in `headline-md` + `crt-glow-amber`.
3. Screw decorations in all four corners.

```html
<div class="chassis-panel p-panel_padding flex flex-col relative">
  <div class="screw tl"></div><div class="screw tr"></div>
  <div class="screw bl"></div><div class="screw br"></div>
  <div class="flex items-center justify-between border-b border-outline-variant pb-2 mb-4">
    <h3 class="font-headline-md text-[18px] font-bold text-primary crt-glow-amber uppercase">PANEL_TITLE</h3>
    <span class="font-code-sm text-code-sm text-outline">STATUS_READOUT</span>
  </div>
  <!-- panel content -->
</div>
```

### Screw Decorations

```css
.screw {
  position: absolute;
  width: 8px; height: 8px;
  background-color: theme('colors.outline-variant');
  border-radius: 50%;
  box-shadow: inset 1px 1px 2px rgba(255,255,255,0.2), inset -1px -1px 2px rgba(0,0,0,0.5);
}
.screw::after {
  content: '';
  position: absolute;
  top: 50%; left: 10%; width: 80%; height: 1px;
  background-color: theme('colors.background');
  transform: translateY(-50%) rotate(45deg);
}
.screw.tl { top: 4px; left: 4px; }
.screw.tr { top: 4px; right: 4px; }
.screw.bl { bottom: 4px; left: 4px; }
.screw.br { bottom: 4px; right: 4px; }
```

### Progress / Status Bar

Use segmented blocks, not smooth fills:

```html
<div class="font-code-sm text-code-sm text-secondary crt-glow-green">
  [|||||||---] 70%
</div>
```

### Terminal / Readout Footer

```html
<div class="mt-4 pt-4 border-t border-outline-variant flex items-center text-outline">
  <span class="font-code-sm text-code-sm">&gt; Awaiting input</span>
  <span class="blinking-cursor ml-1"></span>
</div>
```

---

## 9. Icons

Use **Material Symbols Outlined** exclusively. Load via:

```html
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
```

Icon size in nav: `text-[20px]`. Icon size in panel headers: `text-[24px]`. Icon size in hero/upload areas: `text-[32px]`. Style: `font-variation-settings: 'FILL' 0` for outlined (default); `'FILL' 1` for filled (active/selected states).

---

## 10. Scrollbars

Hide scrollbars while preserving scroll functionality:

```css
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
```

---

## 11. Module Inventory

| Module | File | Status |
|---|---|---|
| HLS Viewer / Stream Control | `hls_viewer_stream_control/code.html` | Reference implementation |
| Gate Cam / High Priority Monitor | `gate_cam_high_priority_monitor/code.html` | Reference implementation |
| Serial Tool / Terminal | `serial_tool_terminal_refined_protocol/code.html` | Reference implementation |
| HTV Tools / Mainframe Protocol | `htv_tools_mainframe_protocol_sync/code.html` | Reference implementation |
| Shipment Engine | `shipment_engine_dark_protocol_final/code.html` | **Needs alignment (see §12)** |

---

## 12. Shipment Engine Alignment Checklist

The Shipment Engine (`shipment_engine_dark_protocol_final/code.html`) is functionally complete but visually diverges from the other modules. The following must be corrected. **Fix these in the existing file — do not create a new one. Verify all JavaScript (form logic, `app.*`, `ui.*` functions, DOCX preview) continues to function after each change.**

### 12.1 — Primary Color Token (`primary`)
- **Problem:** `"primary": "#ffb000"` — this is the `primary-container` value, not `primary`.
- **Fix:** Change `"primary"` to `"#ffd597"`. Keep `"primary-container": "#ffb000"`. Update any hardcoded `#ffb000` used as *text* color to `text-primary` (which will now resolve to `#ffd597`). The filled CTA button background should use `bg-primary-container`, not `bg-primary`.

### 12.2 — Typography: Missing Fonts
- **Problem:** The font load tag includes only `Space Mono`. `JetBrains Mono` and `Courier Prime` are missing.
- **Fix:** Replace the single-font `<link>` with the full canonical three-family import (see §3). Update the Tailwind `fontFamily` config to include all three families per the type scale in §3.

### 12.3 — Body/Content Font
- **Problem:** `body-md` and `body-lg` are mapped to `Space Mono` in the Tailwind config, conflicting with the system-wide `JetBrains Mono` assignment.
- **Fix:** Update `fontFamily.body-md` and `fontFamily.body-lg` to `["JetBrains Mono", "monospace"]`.

### 12.4 — `crt-glow-amber` Amber Value
- **Problem:** `crt-glow-amber` uses `rgba(255, 213, 151, 0.8)` (the `primary` soft warm value) in HTV Tools but `rgba(255, 176, 0, 0.8)` (a harder amber) in Shipment Engine.
- **Fix:** Standardize across all modules. Use the value from `htv_tools_mainframe_protocol_sync`: `text-shadow: 0 0 6px rgba(255, 213, 151, 0.8)` for `crt-glow-amber`.

### 12.5 — Navigation Active Item LED
- **Problem:** The active nav item in the Shipment Engine uses `led-amber` with a border but other modules use `led-amber` without extra border styling on the indicator dot.
- **Fix:** Match the pattern from `htv_tools_mainframe_protocol_sync`: `<span class="ml-auto w-2 h-2 led-amber block border border-on-primary"></span>`. This is already consistent — keep it.

### 12.6 — Surface Background Depth
- **Problem:** The Shipment Engine `body` uses `bg-surface-container-lowest` while other modules use `bg-background`. These tokens currently resolve to the same value (`#131313` vs `#0e0e0e`) but produce a slight tonal mismatch.
- **Fix:** Set `<body>` to use `bg-background` consistently. The inline `body { background-color: #0e0e0e; }` override in the `<style>` block can remain as a depth anchor for the chassis panels.

---

## 13. Do's and Don'ts

| Do | Don't |
|---|---|
| Always use design token class names (`text-primary`, `bg-surface-container`) | Hardcode arbitrary hex colors in `class=""` attributes |
| Keep all corners sharp (`rounded-none` or no rounding) | Add `rounded`, `rounded-md`, `rounded-lg` to any structural element |
| Use `font-label-caps text-label-caps uppercase` for all labels and nav | Mix casing — labels must always be uppercase |
| Apply `crt-scanlines` as the first child of `<body>` | Omit the scanline overlay in any module |
| Check JS functions compile and run after any HTML structural change | Assume JavaScript will survive DOM changes without verification |
| Match the sidebar structure exactly across all modules | Redesign the sidebar layout per-module |
| Use `active:translate-x-0.5 active:translate-y-0.5` on all clickable items | Omit the mechanical-travel effect from interactive elements |
| Reuse existing `.mech-btn`, `.chassis-panel`, `.recessed-input` CSS classes | Define new one-off classes that duplicate existing ones |
| Test the UI at 1024px+, 600–1023px, and <600px after changes | Only test at a single breakpoint |

---

*Last updated: 2026-06-10. Generated from analysis of `stitch_retro_cassette_unified_interface` source files.*
