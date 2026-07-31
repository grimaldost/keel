# Brand assets

keel's visual identity, part of a shared house system across the project family.
The SVGs are self-contained - every glyph and shape is an outlined path, so nothing
depends on an installed font or a network fetch - and they are the source of truth:
edit them as code rather than re-exporting from a design tool.

| File | What | Where it is used |
|---|---|---|
| `keel-mark-{light,dark}.svg` | The mark alone: accent tile with the spine-over-sole figure cut out as true transparency | Favicon / avatar; anything down to 16 px |
| `keel-wordmark-{light,dark}.svg` | The wordmark alone | Inline naming |
| `keel-lockup-{light,dark}.svg` | Mark + wordmark | Headers |
| `keel-hero-{light,dark}.svg` | 1280x240 banner: framed, centered lockup | Top of [README.md](../README.md) |
| `keel-social-card.svg` / `.png` | 1280x640 dark card: lockup over a figure watermark | GitHub Settings -> Social preview (upload the PNG) |

## Embedding

GitHub renders READMEs in both light and dark; embed the theme pair with `<picture>`:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/keel-hero-dark.svg">
  <img alt="keel" src="assets/keel-hero-light.svg" width="100%">
</picture>
```

The same pattern applies to the mark and the lockup.

## Tokens and rules

- Accent (hull steel): tile `#3A73B9` on light, `#558ED6` on dark; the accent rule
  is `#255691` on light and `#558ED6` on dark. House neutrals: ink `#171B1F`, paper
  `#FBFBFA`, muted `#5C666E`, badge-label `#2A3238`.
- A solid rule sits under the wordmark. Note that keel is the one kit whose dark
  rule uses the 500 step (`#558ED6`) rather than the 300; the other kits lighten to
  their 300.
- Badges: shields.io `flat-square`, always `labelColor=2A3238`; version and meta
  badges use `255691`; CI and status badges keep shields' semantic defaults; at most
  five in the row.
- The tile is never outlined, recolored per context, or rotated; minimum mark size
  16 px.
- The assets carry no text beyond the wordmark.
