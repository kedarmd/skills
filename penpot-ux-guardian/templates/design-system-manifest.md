# Design-system manifest — <project>

> Project-owned file. Copy this template to `<project-root>/penpot.design-system.md`
> and keep it current. The skill treats this file as the contract source of
> truth when Penpot metadata is unavailable.

## Tokens

### Colors

| Token | Value | Usage |
|---|---|---|
| `color.primary-600` | `#…` | primary actions |
| `color.text-on-primary` | `#…` | text on primary |

### Spacing

| Token | Value |
|---|---|
| `spacing.xs` | `8` |
| `spacing.md` | `16` |

### Typography

| Token | Family / Size / Weight / Line-height | Usage |
|---|---|---|
| `type.label-md` | `… / 14 / 500 / 20` | button labels |

### Radii / Borders / Effects

| Token | Value | Usage |
|---|---|---|
| `radius.md` | `8` | buttons, cards |

## Components

### `btn/primary` (canonical ref: `<penpot file/page/component id>`)

- Variants/states: default, hover, pressed, disabled, loading
- Fixed: `h=40`; configurable: `width=hug (min 96)`; inherited: —
- Padding: x=`spacing.md`, gap=`spacing.xs`; label `type.label-md`,
  `color.text-on-primary`; fill `color.primary-600`; radius `radius.md`
- Composition: label-only | icon+label (16px icon); never icon-only

## Layout rules

- Page width / column gaps / grid behavior that are constraints rather
  than tokens go here.

## Exceptions

| Date | Scope | Exception | Approved by |
|---|---|---|---|
| — | — | — | — |
