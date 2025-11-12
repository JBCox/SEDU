# Add the SEDU placeholder symbol library to KiCad

- Open KiCad → Preferences → Manage Symbol Libraries.
- Click the Project Specific Libraries tab, then Add (folder icon).
- Nickname: `SEDU`  
  Library path: `hardware/lib/SEDU_Placeholders.kicad_sym`
- Save. You can now place symbols as `SEDU:LM5069-1`, `SEDU:DRV8873-Q1`, `SEDU:DRV8353RS`.

Notes
- These are minimal placeholders to speed placement. We will swap to exact vendor symbols (or refine pins) before final ERC/DRC.
- If KiCad flags missing pin types later, we’ll update the placeholders to match the chosen packages/pinouts.
