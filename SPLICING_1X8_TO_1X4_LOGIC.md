# SPLICING 1X8 TO 1X4 SPLITS - Logic & Formatting

This sheet maps the relationship between the 1x8 backbone and the individual 1x4 distribution splitters. It depends on data and colors captured during the `CABLE TO 1X8 SPLICING` phase.

## 1. Anchor & Header Logic
For every 1x8 splitter found in the DXF, the script locates its **Anchor Row** by searching for the `placement_no` in **Column A**.

### Header Row Updates (The Anchor Row)
| Column | Component | Instruction |
| :--- | :--- | :--- |
| **C** | **Color 1** | Apply Background Fill (HEX) of Color 1 from the 1x8 sheet. |
| **D** | **Color 2** | Apply Background Fill (HEX) of Color 2 from the 1x8 sheet. |
| **F** | **Placement Address** | Write the address of the parent 1x8 splitter. |

## 2. Row Mapping (Offset +3 from Anchor)
Each block contains 8 child rows. Data starts 3 rows below the Anchor (to skip Header, Col Headers, and Spacer).

| Port | Row Offset | Standard T-Count (Col B) |
| :--- | :--- | :--- |
| 1 | Anchor + 3 | 1-4 |
| 2 | Anchor + 4 | 5-8 |
| 3 | Anchor + 5 | 9-12 |
| 4 | Anchor + 6 | 13-16 |
| 5 | Anchor + 7 | 17-20 |
| 6 | Anchor + 8 | 21-24 |
| 7 | Anchor + 9 | 25-28 |
| 8 | Anchor + 10 | 29-32 |

## 3. Column Data Mapping
| Col | Name | DXF Data Source |
| :--- | :--- | :--- |
| **A** | **SPLITTER NAME** | Attribute `FIBER_CO` (from 1x4 block) |
| **B** | **T COUNT** | Standard Port range (see above) |
| **C** | **1X4 PLACEMENT ADDR** | Attribute `PLACEMEN` (ensure 'F ' prefix) |
| **D** | **SPLIT** | `[Parent 1x8 Name], [Port #]` |
| **E** | **SERVICING 1** | Attribute `ST_AD_1` |
| **F** | **SERVICING 2** | Attribute `ST_AD_2` |
| **G** | **SERVICING 3** | Attribute `ST_AD_3` |
| **H** | **SERVICING 4** | Attribute `ST_AD_4` |

## 4. Dynamic Block Creation (Automatic Fallback)
If the script fails to find a pre-existing Anchor Row for a placement (e.g., if Placement 115 exists in the DXF but not in the Excel template), the script must build a new section from scratch.

### Block Structure Logic:
1.  **Spacer**: Leave exactly one empty row after the previous block.
2.  **Row N+1 (Header Strip)**: 
    -   **Merge Cells A to F**.
    -   **Text**: "1X8 SPLITTER PLACEMENT" (Centered).
    -   **Style**: Background Color `#D9E1F2` (Soft Blue-Grey), Thick Outer Border.
3.  **Row N+2 (Anchor Row)**:
    -   **Col A**: Placement Number.
    -   **Col C/D**: Background Colors (Captured from 1x8 Sheet).
    -   **Col F**: Placement Address (Parent 1x8).
4.  **Rows N+3 & N+4 (Merged Column Headers)**:
    -   Cells in these two rows are **Vertically Merged** (e.g., A3+A4, B3+B4).
    -   Headers: `SPLITTER NAME`, `T COUNT`, `1X4 PLACEMENT ADDRESS`, `SPLIT`, `SERVICING`, `SERVICING`, `SERVICING`, `SERVICING`.
    -   **Style**: Bold, Centered, All-Borders applied.
5.  **Rows N+5 to N+12 (Data Rows)**:
    -   Standard 8-row distribution logic.
    -   **Style**: All-Borders applied to every cell in the frame (A to H).

## 5. Business Rules
1. **SPARE Logic (Reverse Top-Down rule)**: Ports are not filled sequentially from 1 to 8. Instead, they are assigned in reverse order (from 8 down to 1), based strictly on how many houses are actually being served. Each 1x4 handles up to 4 houses, so the number of active ports on a 1x8 depends on the total number of houses connected to that placement. The script calculates the required number of 1x4s based on the house count, assigns ports starting from 8 downward, and marks remaining lower ports as SPARE. Lower-numbered ports (1, 2, etc.) that do not receive a splitter must:
   - **Column B**: Detail the standard T-Count range for that port.
   - **Column D**: Show the word "SPARE".
   - **Other Columns**: Must be cleanly wiped.
2. **Reverse Sorting & Name Retention**: The 1x4 names imported from CAD (like `..._1S_...`) are retained exactly as they were imported, but they are systematically mapped mathematically from Port 8 downward. The original `PAIR_CNT` port reference inside the DXF is ignored if it contradicts this backward stack.
3. **Template Preservation**: Do NOT overwrite the "1X8 SPLITTER PLACEMENT" text or existing blue/grey background formatting in Row 1.
4. **Global Framing Rules**: Every single cell within a 1x8 block frame (from the Header Strip down to Port 8) must have a thin border on all four sides.
