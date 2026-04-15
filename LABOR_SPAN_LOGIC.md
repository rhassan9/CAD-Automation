# Labor Span Sheet Automation Logic

This document defines the mathematical and visual data mapping required to accurately populate the Labor Span Sheet. The logic strictly adheres to the client's requested automation standards without corrupting any background template physics.

## Core Directives
1. **Extraction Source:** We pull data exclusively from CAD `MODELITEM` blocks, as well as anonymous dynamic blocks (`*U`) containing `ITEM#` and `LENGTH` attributes.
2. **Column Scope:** The Python automation engine will only modify **Columns A through O**.
3. **Formula Preservation:** Columns **Z through AG** contain critical pre-built `=IF()` formulas that Auto-calculate materials. These columns must remain completely untouched by the automation engine.
4. **Data Entry Start:** The first populated row of data begins on **Row 7**.
5. **Strict Extraction Principle:** The engine operates as a strict mirror of the source `.dxf`. If an attribute is left blank (e.g., Conduit Size) or incorrectly left active from a copy/paste error (e.g., Drop Flags, Cable counts), the script will output that data exactly as it exists in the CAD to enforce drafting accountability.

## Sequence Rule
The raw dictionary objects extracted from the CAD must be sequentially sorted to match the engineering standard:
* First sort by `SP` (Job Print Page) numerically.
* Then sort by `ITEM#` (Construction Note Letter) alphabetically.

## Target Column Mappings (Columns A - I)

### A. JOB PRINT PAGE #
* **Source:** The `SP` attribute parameter.
* **Logic:** Concatenate `"SP-"` with the block's numeric `SP` parameter.
* **Example:** If `SP = 1`, output is `SP-1`.

### B. Construction Note Letter Job Print
* **Source:** The `ITEM#` attribute parameter.
* **Logic:** Direct attribute conversion.
* **Example:** `A`, `B`, `C`, etc.

### C. SPAN FOOTAGE
* **Source:** The `LENGTH` attribute parameter.
* **Logic:** Due to drafting inconsistencies (e.g., `B-F 197`, `H-B 150`), the engine must utilize Regex to strip all alphabetical characters, hyphens, and whitespace. The remaining numerical value is cast directly as an Integer.

### D. NON-STANDARD CONDUIT SIZE
* **Source:** The `COND_SZ` attribute parameter.
* **Logic:** Allow standard Lumos conduit sizes (e.g., 1.25, 2, 4). Extract the numerical value and dynamically append an inch mark (`"`) if the raw CAD data does not already include it. If the CAD field is left blank, or says '0' or 'NONE', leave the cell blank (Strict Extraction).

### E. IS THIS A PARALLELING DROP CONDUIT?
* **Source:** The `DROP_FLG` attribute parameter.
* **Logic:** The engine checks for any truthy value. If `DROP_FLG` contains `'1'` or is populated, output `"yes"`. Otherwise, output `"no"`.

### F. CABLES THIS SPAN
* **Source:** The individual fiber attribute properties (`F48`, `F96`, `F144`, `F288`, `F432`).
* **Logic:** Tally the presence. If a block contains `F48 = 1` and `F144 = 1`, the script will mathematically output `2` meaning there are two distinct cables running through the span.

### G, H, I. Conduit Capacity Splits
These columns break down the true physical volume to ensure precise per-unit billing logic. Let `Q = COND_QTY`.
* **Column G (NEW CONDUIT THIS SPAN ONLY):** Absorbs maximum of 2. `min(Q, 2)`.
* **Column H (*ADDITIONAL* 3RD & 4TH CONDUIT):** Absorbs conduit count above 2. `max(0, min(Q - 2, 2))`.
* **Column I (*ADDITIONAL* 5TH CONDUIT):** Absorbs conduit count above 4. `max(0, min(Q - 4, 1))`.

## Aerial Routing Designation (Columns J - O)
**Visual Hierarchy Resolution:** Aerial vs. Buried implementations are not explicitly defined by text attributes within the `MODELITEM` block. Instead, the parser must evaluate the fundamental CAD physics (Layer and Color) of the line associated with the span.
* Per Lumos V5 drafting standards: If the associated CAD Color is **Blue** (Aerial) or **Brown** (Strand), the data must be routed to the Aerial columns. If the CAD Color is **Red** (Underground), it defaults to the Buried conduit columns.