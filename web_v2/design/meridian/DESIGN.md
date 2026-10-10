---
version: alpha
name: Meridian
description: An editorial design system for frontier AI and model infrastructure, pairing warm paper surfaces and high-contrast serif display type with a clean grotesque UI and a single pastel spectrum moment.
colors:
  primary: "#141412"
  secondary: "#6E6A5F"
  tertiary: "#1B1A16"
  neutral: "#C9C4B7"
  surface: "#F3F1E9"
  surface-raised: "#FBFAF5"
  on-surface: "#141412"
  on-inverse: "#FBFAF5"
  border: "#E1DDD1"
  focus: "#141412"
  error: "#A6432C"
  spectrum-rose: "#F3C9D8"
  spectrum-mint: "#C8E6C4"
  spectrum-sky: "#BCD9EF"
  spectrum-lilac: "#DAC9EC"
  spectrum-butter: "#F0E4B8"
typography:
  font-display: "'Fraunces', Georgia, 'Times New Roman', serif"
  font-ui: "'Inter', system-ui, -apple-system, sans-serif"
  display-xl:
    fontFamily: "{typography.font-display}"
    fontSize: "4.25rem"
    lineHeight: 1.02
    fontWeight: 400
    letterSpacing: "-0.02em"
  display-lg:
    fontFamily: "{typography.font-display}"
    fontSize: "3rem"
    lineHeight: 1.05
    fontWeight: 400
    letterSpacing: "-0.015em"
  headline-lg:
    fontFamily: "{typography.font-display}"
    fontSize: "2rem"
    lineHeight: 1.1
    fontWeight: 500
    letterSpacing: "-0.01em"
  headline-md:
    fontFamily: "{typography.font-display}"
    fontSize: "1.375rem"
    lineHeight: 1.2
    fontWeight: 500
    letterSpacing: "-0.005em"
  body-lg:
    fontFamily: "{typography.font-ui}"
    fontSize: "1.0625rem"
    lineHeight: 1.6
    fontWeight: 400
  body-md:
    fontFamily: "{typography.font-ui}"
    fontSize: "0.9375rem"
    lineHeight: 1.6
    fontWeight: 400
  body-sm:
    fontFamily: "{typography.font-ui}"
    fontSize: "0.8125rem"
    lineHeight: 1.5
    fontWeight: 400
  label-md:
    fontFamily: "{typography.font-ui}"
    fontSize: "0.875rem"
    lineHeight: 1.2
    fontWeight: 500
    letterSpacing: "0.01em"
  label-sm:
    fontFamily: "{typography.font-ui}"
    fontSize: "0.75rem"
    lineHeight: 1.2
    fontWeight: 500
    letterSpacing: "0.04em"
rounded:
  none: "0px"
  sm: "8px"
  md: "12px"
  lg: "18px"
  xl: "24px"
  band: "28px"
  full: "999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "40px"
  "2xl": "64px"
  "3xl": "96px"
  gutter: "24px"
  column: "760px"
  page: "1180px"
elevation:
  flat: "none"
  card: "0 1px 0 rgba(20,20,18,0.04), 0 1px 2px rgba(20,20,18,0.05)"
  lift: "0 1px 1px rgba(20,20,18,0.06), 0 8px 18px rgba(20,20,18,0.10), 0 22px 48px rgba(20,20,18,0.14)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-inverse}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    height: "44px"
    padding: "0 22px"
  button-primary-hover:
    backgroundColor: "#000000"
    textColor: "{colors.on-inverse}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    height: "44px"
    padding: "0 22px"
    border: "1px solid {colors.border}"
  button-icon:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-inverse}"
    rounded: "{rounded.full}"
    size: "44px"
  button-inverse:
    backgroundColor: "{colors.on-inverse}"
    textColor: "{colors.primary}"
    typography: "{typography.label-md}"
    rounded: "{rounded.full}"
    height: "40px"
    padding: "0 20px"
  input-field:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    height: "44px"
    padding: "0 14px"
    border: "1px solid {colors.border}"
  card:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.lg}"
    padding: "24px"
    border: "1px solid {colors.border}"
  card-feature:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    padding: "28px"
  checkbox:
    backgroundColor: "{colors.surface-raised}"
    rounded: "{rounded.sm}"
    size: "20px"
    border: "1px solid {colors.border}"
  checkbox-checked:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-inverse}"
    rounded: "{rounded.sm}"
  tabs-active:
    textColor: "{colors.primary}"
    border: "1px solid {colors.primary}"
  tabs-inactive:
    textColor: "{colors.secondary}"
  spectrum-band:
    rounded: "{rounded.band}"
    padding: "40px"
---

## Overview

Meridian treats technical infrastructure as an editorial object. The screen should feel like a well-set page from a serious print journal that happens to be interactive: a warm paper canvas, thin architectural guide rules holding a disciplined content column, a high-contrast serif carrying the voice, and a neutral grotesque running the machinery of the interface. It should read as calm, considered, and expensive. It must never feel like a bright SaaS template, a neon dashboard, or a card grid with a border around everything.

The system runs quiet by default and spends its energy in three deliberate places: the serif display headline, the ink-black pill controls, and exactly one saturated color event per view, the pastel spectrum band. Everywhere else, restraint is the rule. Type does the heavy lifting; ornament is nearly absent.

Essential traits to preserve:

- Warm paper (`#F3F1E9`) as the dominant surface, never pure white pages.
- A serif display headline where the roman text carries a single italic emphasis word.
- Ink pill buttons and circular icon actions as the only "loud" controls.
- One pastel spectrum band with a halftone dot matrix, used once, with charcoal cards overlapping it.
- Faint vertical guide rules that frame a centered content column.

What to avoid: multiple accent colors competing for attention, glassmorphism, heavy drop shadows, gradient buttons, decorative metadata clutter, and filling quiet space just because it exists.

## Colors

The palette is a warm neutral spine plus one pastel spectrum reserved for a single moment.

- **Paper `#F3F1E9`** is the primary background for every page, the preview, the cover, and metadata. Do not swap it for white.
- **Ink `#141412`** is the warm near-black used for headlines, emphasized body, and solid buttons. It is the workhorse foreground.
- **Muted `#6E6A5F`** is secondary and supporting copy: subheads, captions, inactive nav, helper text.
- **Charcoal `#1B1A16`** (lifting toward `#242320` at the top of a gradient) is the dark/inverted surface for feature cards. On-dark text is `on-inverse #FBFAF5` for headings and `neutral #C9C4B7` for body.
- **Hairline `#E1DDD1`** draws every 1px border and every architectural guide rule. It should be barely there.
- **Surface-raised `#FBFAF5`** is a faintly brighter paper for quiet cards and input fields, distinguished from the canvas by tone plus a hairline, not by shadow.
- **Spectrum hues** (rose `#F3C9D8`, mint `#C8E6C4`, sky `#BCD9EF`, lilac `#DAC9EC`, butter `#F0E4B8`) exist ONLY inside the spectrum band mesh. They are never used as button fills, text colors, icon colors, link colors, or card backgrounds. Breaking this rule collapses the whole concept.
- **White `#FFFFFF`** is reserved for pill buttons that sit on dark surfaces.
- **Error `#A6432C`** is a warm brick red for validation only; it never appears decoratively.

Contrast: Ink on Paper and `on-inverse` on Charcoal both clear WCAG AA for body text. Muted on Paper is for supporting text only, not for critical microcopy at the smallest sizes. Never place body text directly on the spectrum band; text lives on the paper above it or inside the charcoal cards over it.

## Typography

Two families, strictly divided by job.

- **Fraunces** (Google Fonts, optical-size aware) is the display serif. Use it for `display-xl`, `display-lg`, `headline-lg`, and `headline-md` only. Headlines are set in roman weight 400 to 500 with high contrast and tight-ish leading. The signature move: within a headline, set exactly ONE word in Fraunces italic (weight 400 to 500) as the emphasis word, mirroring "beat the *curve*." Never more than one italic word per headline, never all-caps display, never letter-spaced display.
- **Inter** (Google Fonts, 400/500/600) runs the entire interface: navigation, body, labels, buttons, inputs, tabs, table text. Body copy is 400; buttons and labels are 500; the rare strong UI accent is 600.

Alignment: hero headlines and their single supporting subtitle are centered under the mark. In dense contexts (feature cards, forms, tables, docs), body text is left-aligned. One subtitle per heading block, maximum. Small labels use Inter medium at restrained tracking (`label-sm` at `0.04em`); never stack tiny labels to fake richness.

## Layout

Meridian is built on a centered editorial column framed by architectural guide rules.

- **Page frame:** max page width `1180px` (`spacing.page`), centered, with generous side gutters. Two faint vertical `Hairline` rules run the full height of the viewport, positioned just inside the page edges, to frame the content. These rules are structural, not decorative dividers; keep them at 1px and low contrast.
- **Content column:** primary reading and hero content sits in a narrower `760px` (`spacing.column`) centered column. This is where headlines, subtitles, and primary CTAs live.
- **Vertical rhythm:** sections breathe. Use `spacing.3xl` (96px) between major sections, `spacing.2xl` (64px) around the hero, and `spacing.xl` (40px) inside dense blocks. Let empty regions stay empty.
- **Header/nav pattern:** a tri-part bar. Left = a small cluster of text nav links (Inter medium, Muted, Ink on hover). Center = the Meridian quatrefoil mark at ~22 to 26px. Right = an auth cluster (a text "Log in" link plus an ink "Sign Up" pill). The nav is borderless on paper; separation comes from spacing, not a boxed bar.
- **Hero pattern:** centered serif headline (with its one italic word), one centered Muted subtitle, then a centered control row combining a primary ink pill and a circular icon button. No eyebrow, no tag, no label above the headline; lead with the headline itself.
- **Signature band section:** a full-width `spectrum-band` (rounded 28px) sits below the hero as the single color event. Charcoal feature cards overlap the band, straddling its top edge so roughly the lower two-thirds of each card floats over the mesh. Use a 2-up card layout on desktop.
- **Feature cards:** each charcoal card is left-aligned with a circular/inline Lucide icon at the top, a `headline-md` heading, a short Muted-on-dark body, and an inverse pill CTA at the bottom.
- **Forms and dense UI:** left-aligned, single-column, labels above fields, comfortable 44px control height. Group related controls with `spacing.md`; separate groups with `spacing.xl`.
- **Responsive:** below ~720px, guide rules retract to the viewport edges or fade out, the content column becomes full-width with `spacing.lg` gutters, feature cards stack to 1-up and stop overlapping the band (they sit fully below it), and display sizes step down one level.

Use strict centering for hero and marketing moments; switch to disciplined left alignment the instant content becomes dense or functional. Never wrap every element in a bordered card. Prefer whitespace and type hierarchy to separate content.

## Elevation & Depth

Depth is earned, not decorative. The default state of every surface is flat on paper.

- **Guide rules** provide structural depth without shadow: the vertical hairlines and the framing of the content column do the spatial work.
- **Quiet paper cards** use only the `elevation.card` token, a near-invisible two-layer shadow, plus a hairline border. They should feel seated on the page, not floating.
- **Charcoal feature cards** are the one place real lift is allowed, and only because they overlap the spectrum band. They use the multi-layer `elevation.lift` token (three stacked ultra-subtle shadows), never a single heavy drop shadow.
- **Ink pill buttons** read as flat solid objects with no shadow.
- Forbidden: glassmorphism / `backdrop-filter` blur, single muddy drop shadows, and large elevation jumps on hover. Hover changes color or opacity by a small amount instead of lifting.

## Shapes

Pills and soft rectangles, on a consistent radius scale.

- **Radius scale:** `sm 8px`, `md 12px`, `lg 18px`, `xl 24px`, `band 28px`, `full 999px`.
- **Buttons and small labels:** full-radius pills (`999px`).
- **Icon buttons:** perfect circles (`full` radius on a square).
- **Cards:** large soft radius, `lg` (18px) for quiet cards, up to `xl` (24px) for the largest feature cards.
- **Inputs:** gently rounded `md` (12px).
- **Checkboxes:** square-ish `sm` (8px).
- **Spectrum band:** wide rounded `band` (28px).
- **Borders:** always 1px `Hairline`. There are no thick or brutalist borders in this system.

## Components

- **Buttons.** Primary = ink pill (`button-primary`) with `on-inverse` text; hover deepens toward black. Secondary = transparent/paper pill (`button-secondary`) with Ink text and a hairline border; hover fills to `surface-raised`. Icon = circular ink button (`button-icon`) holding a single Lucide glyph such as `arrow-up-right`. On dark surfaces, CTAs invert to white pills with Ink text (`button-inverse`). All buttons are 44px tall (40px inverse), Inter medium, no shadow.
- **Inputs.** Paper `surface-raised` field, hairline border, Ink text, Muted placeholder, `md` radius, 44px tall. Focus draws a 2px Ink ring (via focus outline/box-shadow), never a colored glow. Labels sit above the field in `label-md`.
- **Cards.** Two families. Quiet paper cards (`card`): `surface-raised`, hairline border, `card` elevation, for neutral content. Charcoal feature cards (`card-feature`): `tertiary` background with a subtle top-lift toward `#242320`, `on-inverse` heading, `neutral` body, top icon, inverse pill CTA, `lift` elevation, designed to overlap the spectrum band.
- **Checkboxes.** 20px square, `sm` radius, hairline border on `surface-raised`. Checked state fills Ink with a white Lucide `check`. No custom SVG paths beyond the Lucide glyph.
- **Tabs.** Text tabs in Inter medium. Inactive = Muted. Active = Ink text with a thin Ink underline (or an Ink pill on the active item in compact bars). Only one active tab; no colored indicators.
- **Nav.** Tri-part as described in Layout. Links are Muted, Ink on hover; the mark recolors via `currentColor` (Ink on paper, `on-inverse` on dark); the right cluster ends in an ink Sign Up pill.
- **Spectrum band.** The signature element: a wide rounded band (`band` radius) filled with a soft multi-hue pastel mesh (rose/mint/sky/lilac/butter via layered radial gradients) overlaid by a regular halftone dot matrix (a repeating radial-gradient dot pattern in translucent white). Use it once per view as the only saturated moment. Charcoal cards overlap it; no body text sits directly on it.

**Icon library:** Lucide (https://lucide.dev/, ISC license). The preview loads Lucide via its browser script and renders glyphs with `data-lucide` attributes, colored through `currentColor` on the icon container. Icons are utility-sized (16 to 24px, never scaled up as illustrations) and used for nav actions, the circular icon button, feature-card marks, checkboxes, and inline affordances. Use exactly this one library; do not mix icon sets or invent SVG paths.

## Do's and Don'ts

**Do**

- Keep Paper `#F3F1E9` as the canvas on every surface, including the cover and metadata background.
- Set every headline in Fraunces roman with exactly one Fraunces italic emphasis word.
- Reserve the pastel spectrum strictly for the mesh inside the spectrum band.
- Use ink pills and circular icon buttons as the primary loud controls, kept flat.
- Frame content with faint vertical guide rules and a centered `760px` reading column.
- Let charcoal feature cards overlap the spectrum band using multi-layer subtle shadows.
- Center hero content; switch to left alignment for dense, functional content.
- Keep borders at 1px hairline and depth nearly flat.

**Don't**

- Don't use any spectrum hue as a button fill, text color, icon color, or card background.
- Don't introduce a second accent color or a purple/blue SaaS gradient.
- Don't set headlines in all-caps, letter-spaced, or with more than one italic word.
- Don't wrap every element in a bordered, rounded card; use whitespace and type to separate.
- Don't use glassmorphism, heavy single-layer drop shadows, or large hover elevation jumps.
- Don't scatter decorative metadata, coordinates, volume/issue tags, timestamps, or all-caps monospace micro-labels.
- Don't place body text directly on the spectrum band.
- Don't scale Lucide icons up as hero illustrations or mix in a second icon set.
