# Email signature

**Status: Concept.** The standard signature for every `first.last@joinoasa.org` address, from the founder's design (2026-10-28).

![Signature preview](signature-preview.png)

## Make yours

Use the generator: **[joinoasa.org/email-signature/](https://joinoasa.org/email-signature/)**. Fill in your details, click **Copy signature**, paste it into Gmail. Don't build a signature by hand.

## What's in it

- The OASA logo beside a gold divider.
- Name, title and email. Phone is optional; when set, it shares a second line with the joinoasa.org link.
- Icons: GitHub and Discord by default. YouTube and X are available under **Advanced** and become defaults once OASA has those accounts. LinkedIn waits for LinkedIn's official icon.
- The tagline and the four-color bar, always on.

## Files

| Path | What |
|---|---|
| `source/signature-logo.svg` | The logo with the name on two lines (source of the hosted PNG) |
| `source/color-bar.svg` | The four-color bar |
| `hosted/` | Copies of the PNGs served from `joinoasa.org/email/sig/`. The website repo holds the live copies; change them there. |

Icons: GitHub, Discord, YouTube and X from [Simple Icons](https://simpleicons.org) (CC0); mail, phone and link from [Lucide](https://lucide.dev) (ISC). The platform icons are their owners' trademarks, used only to link to OASA's accounts.

## Why it's built this way

- **Tables and inline styles:** Gmail and Outlook strip most other styling.
- **PNG images, hosted on joinoasa.org:** mail apps won't show SVG or embedded images reliably.
- **The logo has a white background** so it stays visible in dark mode.
- **Text is real text** (selectable, crisp); it shows in each reader's system font, since mail apps ignore custom fonts.
