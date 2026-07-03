# worldcup -- Style Guide & Cheatsheet

Use this to replicate the project's visual language across all UI work.

**Direction:** dark, stadium-at-night feel — near-black background, gold accent (the trophy), team flags/crests as the main splash of color. Matches the reference image for the radial bracket. Styling is plain CSS (CSS modules or a single stylesheet) — no UI framework, no Tailwind. The radial bracket is hand-rolled SVG.

---

## Color Palette

### Primary
| Token       | Hex       | Use                              |
|-------------|-----------|----------------------------------|
| primary.50  | `#{{HEX}}` | Light backgrounds, hover states  |
| primary.100 | `#{{HEX}}` | Subtle highlights                |
| primary.200 | `#{{HEX}}` | Borders, dividers                |
| primary.300 | `#{{HEX}}` | Secondary buttons                |
| primary.400 | `#{{HEX}}` | Links, active states             |
| primary.500 | `#{{HEX}}` | **Primary buttons, key actions** |
| primary.600 | `#{{HEX}}` | Dark accents, active nav         |
| primary.700 | `#{{HEX}}` | Dark accents                     |
| primary.800 | `#{{HEX}}` | Very dark accents                |
| primary.900 | `#{{HEX}}` | Near-black                       |

### Accent (gold — proposed, tune during development)
| Token       | Hex       | Use                              |
|-------------|-----------|----------------------------------|
| accent.50   | `#{{HEX}}` | Light highlight background       |
| accent.300  | `#{{HEX}}` | Badges, tags                     |
| accent.500  | `#D4AF37`  | **Winner paths, active tab, LIVE badge** (proposed trophy gold) |
| accent.700  | `#{{HEX}}` | Dark accent text                 |

<!--
  Add more color groups as needed:
  - Semantic (success green, error red, warning amber)
  - Bracket-specific: eliminated-team dim overlay, connector-line grey, winner-path gold
-->

### Grays (dark theme — invert the usual roles)
| Usage                | Token        |
|----------------------|--------------|
| Page background      | near-black `#111` (proposed) |
| Card background      | `#1c1c1e` (proposed) |
| Card borders         | `#2c2c2e` (proposed) |
| Muted text           | `gray.500`   |
| Secondary text       | `gray.400`   |
| Body text            | `gray.300`   |
| Headings             | `gray.100`   |

---

## Typography

**Font stack:**
```
{{FONT_FAMILY}}, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

| Element              | Size    | Weight     | Color       |
|----------------------|---------|------------|-------------|
| Page heading (h1)    | `2xl`   | `bold`     | gray.100    |
| Section heading (h2) | `lg`    | `bold`     | gray.100    |
| Card heading (h3)    | `md`    | `semibold` | gray.100    |
| Body text            | `sm`    | `normal`   | gray.300    |
| Muted / helper text  | `xs`    | `normal`   | gray.500    |
| Scores               | `xl`    | `bold`     | gray.100 (tabular numerals) |

<!--
  Sizes are placeholders — set concrete px/rem values when the first components land.
-->

---

## Spacing & Layout

| Concept              | Value   | Notes                          |
|----------------------|---------|--------------------------------|
| Page padding         | `16px`  | mobile-first                   |
| Card padding         | `16px`  |                                |
| Gap between cards    | `12px`  |                                |
| Gap between sections | `24px`  |                                |
| Border radius (cards)| `12px`  |                                |
| Tab bar height       | `56px`  | fixed bottom on mobile         |

<!--
  Add layout constants relevant to this project:
  - Group card width (full viewport minus padding, for the swipe carousel)
  - Radial bracket: viewBox size, ring radii per round, node diameter
-->

---

## Component Patterns

<!--
  Document the reusable component patterns as they are built. Planned components:

  ### TabBar
  Two tabs: "Groups" / "Bracket". Active tab in accent gold, fixed to bottom on mobile.

  ### GroupCard (one per group, swipeable)
  Standings table + match list. Full-width card; carousel with snap points
  (CSS scroll-snap or pointer-event drag). Indicator dots A–L below.

  ### RadialBracket (SVG)
  - viewBox square, trophy image/glyph at center
  - One ring per round; 32 nodes on the outer ring
  - Node: circle with team crest, grey/dimmed when eliminated
  - Connector lines between match slots; winner path in accent gold
  - Popover on node tap: score, status, kickoff in Spain time (Europe/Madrid, zone shown)

  ### LiveBadge
  Small pulsing gold dot + "LIVE" label on in-play matches.
-->

---

## Page Backgrounds

| Context              | Background  |
|----------------------|-------------|
| App background       | near-black `#111` |
| Cards / panels       | `#1c1c1e`   |
| Radial bracket area  | radial gradient: subtle warm glow behind the trophy, fading to background |

---

## Borders & Shadows

| Element              | Border                         | Shadow   |
|----------------------|--------------------------------|----------|
| Cards                | `1px solid #2c2c2e`            | none (dark theme — rely on surface contrast) |
| Popovers             | `1px solid #2c2c2e`            | `0 8px 24px rgba(0,0,0,.5)` |
| Active tab           | top `2px solid` accent gold    | none     |

---

## Responsive Breakpoints

| Breakpoint | Width    | What changes                                   |
|------------|----------|------------------------------------------------|
| base       | 0px+     | Single group card per view, bottom tab bar, bracket scales to width |
| md         | 768px+   | Two group cards visible, bracket larger        |
| lg         | 1024px+  | Groups in grid (swipe optional), bracket at full size, top tab bar |

---

## Accessibility Checklist

- Skip-to-content link
- Semantic landmarks: `<header>`, `<main>`, `<nav>` (tab bar)
- All interactive elements keyboard-accessible — group carousel must respond to arrow keys, bracket nodes focusable
- Color contrast: minimum 4.5:1 ratio (careful with gold-on-dark for small text)
- `aria-label` on icon-only elements (bracket nodes: "France vs Norway, quarter final, 2-1")
- Focus visible on all interactive elements
- Swipe carousel: also provide prev/next buttons (not gesture-only)

---

## Quick Reference: Framework Usage

Plain CSS + hand-rolled SVG. No component framework, no Tailwind, no chart libs (see CLAUDE.md — any new UI library needs an analysis doc first).

| Use plain CSS for...           | Use SVG for...               |
|--------------------------------|------------------------------|
| Layout, cards, tabs, tables    | The radial bracket, connector lines, winner paths |
| Scroll-snap group carousel     | Trophy glyph at center       |
| Transitions (tab switch, card snap) | Node states (dim, highlight) |
