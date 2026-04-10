# Labor Span Sheet Automation Logic

This document defines the mathematical and visual data mapping required to accurately populate the Labor Span Sheet. The logic strictly adheres to the client's requested automation standards without corrupting any background template physics.

## Core Directives
1. **Extraction Source:** We pull data exclusively from CAD `MODELITEM` blocks.
2. **Column Scope:** The Python automation engine will only modify **Columns A through O**.
3. **Formula Preservation:** Columns **Z through AG** contain critical pre-built `=IF()` formulas that Auto-calculate materials. These columns must remain completely untouched by the automation engine.
4. **Data Entry Start:** The first populated row of data begins on **Row 7**.

## Sequence Rule
The raw dictionary objects extracted from the CAD must be sequentially sorted to match the engineering standard:
*   First sort by `SP` (Job Print Page) numerically.
*   Then sort by `ITEM#` (Construction Note Letter) alphabetically.

## Target Column Mappings

### A. JOB PRINT PAGE #
*   **Source:** The `SP` attribute parameter.
*   **Logic:** Concatenate `"SP-"` with the block's numeric `SP` parameter.
*   **Example:** If `SP = 1`, output is `SP-1`.

### B. Construction Note Letter Job Print
*   **Source:** The `ITEM#` attribute parameter.
*   **Logic:** Direct attribute conversion.
*   **Example:** `A`, `B`, `C`, etc.

### C. SPAN FOOTAGE
*   **Source:** The `LENGTH` attribute parameter.
*   **Logic:** Cast directly as an Integer.

### D. NON-STANDARD CONDUIT SIZE
*   **Source:** The `COND_SZ` attribute parameter.
*   **Rule:** The sheet explicitly requires this to *"ONLY UTILIZE FOR 2" OR 4" CONDUIT"*.
*   **Logic:** If `COND_SZ` is `2` or `4`, inject it. Otherwise, leave the cell dynamically blank.

### E. IS THIS A PARALLELING DROP CONDUIT?
*   **Source:** The `DROP_FLG` attribute parameter.
*   **Logic:** The engine checks for any truthy value. If `DROP_FLG` contains `'1'` or is populated, output `"yes"`. Otherwise, output `"no"`.

### F. CABLES THIS SPAN
*   **Source:** The individual fiber attribute properties (`F48`, `F96`, `F144`, `F288`, `F432`).
*   **Logic:** Tally the presence. If a block contains `F48 = 1` and `F144 = 1`, the script will mathematically output `2` meaning there are two distinct cables running through the span.

### G, H, I. Conduit Capacity Splits
These columns break down the true physical volume to ensure precise per-unit billing logic. Let `Q = COND_QTY`.
*   **Column G (NEW CONDUIT THIS SPAN ONLY):** Absorbs maximum of 2. `min(Q, 2)`.
*   **Column H (*ADDITIONAL* 3RD & 4TH CONDUIT):** Absorbs conduit count above 2. `max(0, min(Q - 2, 2))`.
*   **Column I (*ADDITIONAL* 5TH CONDUIT):** Absorbs conduit count above 4. `max(0, min(Q - 4, 1))`.

## Known Discrepancies & Client Queries
**Columns J through O** govern purely Aerial implementations (`NEW AERIAL`, `OVERLASH CABLE`, `OVERLASH MP TAIL`, etc.). Currently in the `MODELITEM` layout, there are no strict CAD parameters definitively flagging `OVERLASH`. A standing query must remain open with the LLD drafting team to identify whether they intend for these target fields to be filled manually for Aerial sites, or whether there is a raw hidden CAD layer/flag that the parser should evaluate.
