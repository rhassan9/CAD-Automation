# CABLE SHEET - Logic & Formatting Specifications (V3 - Final)

## 1. Top Global Tables (Rows 1-7)
The top section contains three fixed calculation tables:
* **New Conduit** (B2:D7)
* **Aerial** (G2:I7)
* **Existing Conduit** (L2:N7)

**Rule:** DO NOT OVERWRITE OR MODIFY. These cells contain pre-built Excel `=SUMIF()` formulas that dynamically calculate total footage based on the data populated in the SEG tables below.

## 2. Segment Identification & Sizing (The "Callout Truth" Rule)
Due to CAD data hygiene issues (e.g., draftsmen leaving incorrect `F96` checkboxes ticked on `144-count` lines), the parser/extractor must **never** trust the internal checkboxes of an `ITEM_NUMBER` block to determine cable size.
* **Source:** The `CABLE CALLOUT` text block ONLY (e.g., `HSP.01.05.01 144`).
* **Logic:** The string must be parsed to extract two absolute values:
    1.  **Segment ID:** The fourth integer group (e.g., `01` = SEG 1).
    2.  **Cable Size:** The standalone integer at the end of the string (e.g., `144`).
* **Enforcement:** A CAD span block can *only* be associated with a Segment if it is physically contiguous to the Callout, ignoring its internal size checkboxes entirely.

## 3. Segment Table Layout (Rows 9+ / Horizontal Distribution)
There are 25 tables distributed horizontally. Each table represents a single `SEG` (Cable Segment) from the CAD drawing.
Tables jump by **5 columns** horizontally.

* **SEG 1**: Labels in **Col B**, Data in **Cols C, D, E**. Spacer in **F**.
* **SEG 2**: Labels in **Col G**, Data in **Cols H, I, J**. Spacer in **K**.
* **SEG 3**: Labels in **Col L**, Data in **Cols M, N, O**. Spacer in **P**.
* ... repeating across to SEG 25.

### Table Structure (Example: SEG 1)
| Cell/Range | Value Content | Format Rule | Extraction Logic |
| :--- | :--- | :--- | :--- |
| **B9** | `SEG 1` | Label (Static) | N/A |
| **C9:E9** | Method | Merged. Dropdown value: `New Conduit`, `Aerial`, or `Existing Conduit`. | **V5 Color Rule:** Blue/Brown = `Aerial`, Red = `New Conduit`, Black/Gray = `Existing Conduit`. (Spelling must be exact). |
| **B10** | `START` | Label (Static) | N/A |
| **C10:E10** | Start Address | Merged. e.g., `6913 OLD MILLS RD` | Geographically calculated nearest `NOTES_1_FULL_ADDRESS` to the first coordinate of the segment. |
| **B11** | `END` | Label (Static) | N/A |
| **C11:E11** | End Address | Merged. e.g., `4700 BENTCREEK DR` | Geographically calculated nearest `NOTES_1_FULL_ADDRESS` to the final coordinate of the segment. |
| **B12** | `CABLE SIZE` | Label (Static) | N/A |
| **C12:E13** | Cable Count | Merged. Dropdown value: e.g., `48`. | Extracted exclusively from the `CABLE CALLOUT` text (See Section 2). |
| **B13** | `TOTAL` | Label (Static) | N/A |
| **C13:E13** | Total Distance | **DO NOT TOUCH.** Contains `=SUM(C15:E199)` formula. | N/A |
| **C14, D14, E14**| Column Headers | `SPAN`, `STORAGE`, `RISER` | N/A |

## 4. Data Population & Routing (Rows 15 and below)
The sequence of the cable lines pulled from AutoCAD populates starting on Row 15. The extraction must follow strict End-to-End geometric tracing, stopping at designated junctions.

### A. Row 15 (The Anchor Node Initialization)
Every segment's data trace must begin with an Anchor Node to establish the starting slack.
* **SPAN:** Always hardcoded to `0`.
* **STORAGE:** Evaluates the environment/hardware at the starting coordinate:
    * If nearest hardware is a Splice/1x8 Splitter (within 25 units): `15`.
    * If the Method is Aerial: `200`.
    * Default / Standard Handhole: `50`.

### B. Row 16+ (Iterative Span Rows)
* **SPAN:** Extracted from the `LENGTH` attribute in the `ITEM_NUMBER` block.
    * *Regex Rule:* Strip all alphabetical characters (e.g., "B-F 457" becomes `457`).
* **STORAGE:** Extracted based on the environment of that specific block's coordinates:
    * If block is near a Splice/1x8 Splitter (within 25 units): `15`.
    * If the Method is Aerial: `200`.
    * Default / Standard Handhole: `50`.
* **RISER:** Leave blank unless a specific riser flag is present in the CAD attributes.

### C. The Junction Stopper Rule
Segments are not infinite. When tracing the physical line of blocks from the Start Address to the End Address, the trace must **hard stop** the moment the line intersects a Splice Box or 1x8 Splitter. This prevents the extraction from bleeding into the next segment at network junction points.

## 5. Visual Formatting Requirements
* All data must align perfectly within the predefined borders.
* Merged cells at the top of each block (`C9:E9`, `C10:E10`, `C11:E11`, `C12:E12`) must remain merged. If openpyxl attempts to overwrite a merged cell format, only target the top-left cell (e.g., `C9`) to prevent un-merging.
* All data entered in the Segment Tables must be center-aligned to match the template style.