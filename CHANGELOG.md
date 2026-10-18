# Changelog

## 0.1.6 — 2026-10-18

- Require ComfortableTUI 0.1.5 to follow terminal movement without rebuilding native overlay scenes on every translation, and reject inconsistent UIA geometry during movement.
- Update the pinned dependency, bilingual installation docs and Windows runtime manifest; native/browser binaries and protocols are unchanged.


## 0.1.5 — 2026-10-18

- Fix per-core CPU bars to use an absolute 0..100% scale instead of filling the track at the busiest core's value; update English/Chinese labels and documentation.

## 0.1.4 — 2026-10-18

- Default Windows hybrid WebViews to GPU textures, with explicit CPU comparison mode and native frame diagnostics.
- Give each Top instance a separate temporary browser root so multiple instances can run concurrently.
- Require ComfortableTUI 0.1.3 and ship a matching rebuilt Windows browser/chart runtime.
- Distribute Windows x64 wheels and runtime only; withdraw Linux installation, execution and runtime builds.
- Update bilingual installation, architecture, troubleshooting and validation documentation.
