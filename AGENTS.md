# Repository Guidelines

## Project Structure & Module Organization
- Root contains design references (`New Single Board Idea.md`, `Component_Report.md`), legacy wiring docs, and datasheets.  
- Generated notes live beside source docs (`Original_Schematic_Translation.md`, `Datasheet_Notes.md`).  
- Hardware assets (images, PDFs) stay in the root; prefer linking rather than duplicating. Keep any future CAD/KiCad files under `hardware/` (create if needed) and firmware under `firmware/`.

## Build, Test, and Development Commands
- Documentation-first workflow: no build system yet.  
- Use standard CLI tools for validation: `rg "<term>"` to locate references, `markdownlint file.md` if available, and `python -m http.server` to preview rendered docs locally. Document any new scripts in their directory README.

## Coding Style & Naming Conventions
- Markdown: ATX headings, 80–100 char soft wrap, ordered lists only when sequence matters.  
- File naming: `Camel_Snake.md` for human-readable specs; use lowercase-with-dashes for directories (`hardware/`, `firmware/`).  
- Add purposeful comments when editing embedded code blocks—avoid boilerplate explanations. Stick to ASCII unless a datasheet symbol truly requires otherwise.

## Testing Guidelines
- Treat doc updates like code: validate tables render, pin maps remain consistent, and cross-check values against datasheets before submission.  
- When scripts/tests are introduced, colocate unit tests under `tests/` mirroring the script tree and provide a one-line command (e.g., `pytest tests/`).

## Commit & Pull Request Guidelines
- Commits should be focused: one logical change per commit, subject format `component: short summary` (e.g., `docs: note LM5069 dv/dt math`).  
- Pull requests must describe intent, list affected files, mention verification steps (simulations, calculations, previews), and link any tracking issues. Include screenshots for visual artifacts (schematics, UI mockups) when feasible.

## Architecture & Safety Notes
- Maintain parity with the legacy positive-feed drill behavior: same operator states, safety interlocks, and power domains.  
- Highlight any deviation from original wiring in both the schematic notes and BOM updates. Keep RF keep-outs, hot-swap math, and actuator ILIM calculations up to date as the design evolves.
