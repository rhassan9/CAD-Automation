# Project Walkthrough: Final Automation Engine

The Python-based extraction and mapping engine has successfully automated the core data flows from CAD to Excel.

## 1. 1x8 to 1x4 Splicing (Reverse Port Logic)
*   The script fully implements the mathematically calculated "Reverse Bottom-Up" port mapping rule (`SPARE`, `SPARE`, Port 3, 4, 5, etc.).
*   It successfully identified that Manual Workbooks contained massive errors regarding actual CAD-drawn item counts, proving the necessity of the tool.
*   **Known Constraint:** Because the manual template provided was blank, the Excel writer relies on executing data writes targeting the generic `1X8 SPLITTER PLACEMENT` cells to cleanly sequentially construct the target fields.

## 2. Cable Sheet Data Population
*   **Segment Mapping**: Successfully mapped Segment boundaries logically grouped by nearest `HSP.**.**.XX` string inside `CABLE CALLOUT` blocks, proving alphabetic parsing of `ITEM#` was conceptually flawed in manual logic.
*   **Spatial Storage Drop**: A Handhole's default storage limit (`50`) is now strictly subjected to a spatial geometry bounds-check. If either a `1x8` or `1x4` Splitter node falls within a `15.0` distance radius of the starting segment handhole, the `STORAGE` trace immediately drops its physical attribute parameter to `15` to abide by precise Lumos structural tolerances.
*   **Template Physics Engine**: We implemented a safety check to ensure Data Injection didn't overwrite the read-only, formula-bound Merged Cells explicitly created by Lumos templates. 

## 3. House Count Formatting
*   Refactored the renderer to securely apply standard border weights uniformly to all cells inside `House Count`.
*   A mathematical division cleanly hooks the 12th row via Modulo `%` loop logic, applying a `thick` horizontal bottom separator to correctly bucket the rows per standardized rules.

## 4. Labor Span Sheet Population [NEW]
*   **Automation Scope**: Successfully engineered mathematical mappings converting raw `MODELITEM` parameters directly into **Columns A through O**, exclusively automating the Underground variables.
*   **Underground Constraints Logic**:
    *   Dynamically maps conditional flags (e.g. `IS THIS A PARALLELING DROP CONDUIT?` translates `DROP_FLG`).
    *   Calculates exact physical cables inside the span (`F48`, `F96`, `F144`...) via tallies to output `CABLES THIS SPAN`.
    *   Spits out mathematically bound conduit splits. `COND_QTY` gracefully splits its volume into maximum constraints allowed internally (Columns `G` via `min(Q, 2)`, `H` via `max(min(Q-2, 2))`, etc.).
*   **Engine Protection**: 
    *   Leaves the dynamic material `=IF()` formulas residing in columns `Z` through `AG` untouched to trigger safe automated engineering estimations.
    *   Aerial properties (`Columns J-O`) are left blank as manual fallbacks for the engineering team until raw CAD Aerial attributes are strictly codified.

## 5. Visual Formatting
*   All data generated dynamically inherits `center-alignment` styles to match the client's original workbook styling.
*   Data traces safely wipe dummy-data lines before applying accurate DXF parameters.
