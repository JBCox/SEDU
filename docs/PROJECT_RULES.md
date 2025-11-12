# Project Rules & Knowledge Management

## Purpose
Keep every AI session synchronized by defining how information enters, changes, and gets archived. These rules apply to all contributors and tools (Flux, KiCad, CLI agents, etc.).

## Documentation Layers
1. **Root specs** (e.g., `New Single Board Idea.md`, `Datasheet_Notes.md`) hold the latest single-board requirements.  
2. **Working notes** belong under `docs/` using `YYYY-MM-DD_title.md` naming (example: `docs/2025-01-15_power-tree.md`). These capture in-progress analysis or calculations.  
3. **Archives** live inside `docs/archive/` once a note is superseded. Do not delete—move with a timestamp so older context never leaks forward.

## Update Rules
- Before editing, scan `docs/archive/CHANGELOG.md` (create entry if missing) to understand recent decisions.  
- When new data is introduced (pin map changes, math updates, flux outputs), cite the source file and date inside the note.  
- Every change must include a short “Why” paragraph so future sessions understand intent.  
- Never mix legacy VESC stack info into single-PCB docs; if referencing old behavior, explicitly tag sections as “Legacy Reference”.

## Tool Usage & Verification
- **Flux.ai/KiCad**: document tool version (Help → About) in the note describing its output. Re-run ERC/DRC after auto-actions.  
- **Datasheets/Math**: note revision/date; store calculations (e.g., LM5069 Rsense, buck losses) either in `Datasheet_Notes.md` or a dated note under `docs/`.  
- If a tool’s feature is uncertain (e.g., Flux autoroute status), log a “Tool Check” entry with findings before relying on it.

## Change Logging
- Maintain `docs/archive/CHANGELOG.md` with bullet entries: `YYYY-MM-DD – Short summary – Author/agent`. Include links/paths to affected files.  
- Major milestones (schematic freeze, BOM freeze, Gerber release) must be recorded in the changelog and referenced in the root specs.

## Daughter Boards & Future Work
- LCD/buttons move to a daughter board; document its requirements in a dedicated note (`docs/daughterboard_lcd.md`) when ready.  
- Cross-link daughter-board decisions back into the main spec to avoid fragmenting requirements.
