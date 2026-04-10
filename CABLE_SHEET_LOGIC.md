# CABLE SHEET - Logic & Formatting Specifications

## 1. Top Global Tables (Rows 1-7)
The top section contains three fixed calculation tables:
*   **New Conduit** (B2:D7)
*   **Aerial** (G2:I7)
*   **Existing Conduit** (L2:N7)

These summarize total cable by size and installation method. **DO NOT OVERWRITE OR MODIFY.** These cells contain pre-built Excel formulas (e.g., SUMIF functions) that dynamically calculate based on the data in the SEG tables below.

## 2. Engineering Logic ("The 3-Line Message")
Cells Q2:Q4 contain a highly critical engineering note printed in red/yellow:
*   `15 FOR SPLT`
*   `50 FOR ALL ELSE`
*   `FIRST ROW 0 AND THE HANDHOLE STORAGE OF HH IT STARTS FROM`

**What it means:**
1.  **Storage Value Logic**: Slack loops stored in Handholes are standardly **50 feet**. However, if that handhole contains a Splice/Splitter enclosure, the storage shrinks to **15 feet**.
2.  **Row 1 Initialization**: Every segment's data trace must begin with an "Anchor Node". 
    *   The `SPAN` (distance) for this first node is always `0`.
    *   The `STORAGE` for this first node is the slack value from the handhole where the cable segment begins.

## 3. Segment Table Layout (Rows 9+ / Horizontal Distribution)
There are 25 tables distributed horizontally. Each table represents a single `SEG` (Cable Segment) from the CAD drawing.
Tables jump by **5 columns** horizontally.

*   **SEG 1**: Labels in **Col B**, Data in **Cols C, D, E**. Spacer in **F**.
*   **SEG 2**: Labels in **Col G**, Data in **Cols H, I, J**. Spacer in **K**.
*   **SEG 3**: Labels in **Col L**, Data in **Cols M, N, O**. Spacer in **P**.
*   ... repeating across to SEG 25.

### Table Structure (Example: SEG 1)
| Cell/Range | Value Content | Format Rule |
| :--- | :--- | :--- |
| **B9** | `SEG 1` | Label (Static) |
| **C9:E9** | Method | Merged. Dropdown value: `New Conduit`, `Aerial`, or `Existing Conduit`. |
| **B10** | `START` | Label (Static) |
| **C10:E10** | Start Address | Merged. e.g., `6913 OLD MILLS RD` |
| **B11** | `END` | Label (Static) |
| **C11:E11** | End Address | Merged. e.g., `4700 BENTCREEK DR` |
| **B12** | `CABLE SIZE` | Label (Static) |
| **C12:E13** | Cable Count | Merged. Dropdown value: e.g., `48`. (Matches F48 property in CAD) |
| **B13** | `TOTAL` | Label (Static) |
| **C13:E13** | Total Distance | **DO NOT TOUCH**. Contains `=SUM(C15:E199)` formula. |
| **C14, D14, E14**| Column Headers | `SPAN`, `STORAGE`, `RISER` |

## 4. Data Population (Rows 15 and below)
The actual sequence of the cable lines pulled from AutoCAD populate starting on Row 15.

*   **Row 15 (First Row):**
    *   `SPAN` must be hardcoded to `0`.
    *   `STORAGE` must be extracted from the starting handhole (or fallback to logic rules: 50 / 15).
*   **Row 16 and subsequent rows:**
    *   `SPAN` = The length of the CAD Polyline/Line segment. (Corresponds to `LENGTH` attribute in `ModelItem#` blocks).
    *   `STORAGE` = The storage at that specific point. (Corresponds to `SP` attribute in `ModelItem#` blocks).
    *   `RISER` = Typically empty unless specified by a riser block flag.

## 5. Visual Formatting Requirements
*   All data must align perfectly within the predefined borders.
*   Merged cells at the top of each block must remain merged.
*   Data entered must be center-aligned to match the template style.
