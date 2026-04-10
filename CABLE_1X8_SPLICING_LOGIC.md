# CABLE TO 1X8 SPLICING - Logic & Formatting

## 1. Sheet Overview
This sheet acts as the primary index for the 1x8 splitters. Every splitter extracted from the CAD drawing must be mapped to a specific pre-defined row in the template based on its **Placement Number**.

## 2. Template Structure (Columns)
| Column | Name | Purpose |
| :--- | :--- | :--- |
| **A** | **OLT / Index** | The primary search column. Contains numbers (1, 2, 3...). We match our `placement_no` against this. |
| **B** | **Color 1** | Pre-assigned fiber color code. To be recorded/preserved during mapping. |
| **C** | **Color 2** | Secondary pre-assigned fiber color code. To be recorded/preserved during mapping. |
| **D** | **EXTRACTED #** | The space where we write the `placement_no` to confirm the alignment. |
| **E** | **ADDRESS** | The `placement_address` extracted from the CAD block. |
| **F** | **1X8 SPLITTER NAME** | The `base_1x8_name` (e.g., `OLT01_106P_FQVRNC`). |
| **G - N** | **PORT 1 - 8** | The specific port associations or the string "SPARE" if unused. |

## 3. The Extraction & Mapping Workflow
1.  **Extract & Sort**: 
    *   Extract all `1x8 SPLITTER` blocks from the DXF.
    *   Sort the resulting data by `placement_no` in ascending order.
2.  **Sequential Lookup**:
    *   For each splitter in the sorted list, iterate through the template's **Column A**.
    *   Once a match is found (e.g., Template row says `106` and our extracted `placement_no` is `106`):
        *   **Record** the color values in B and C for internal validation/logging.
        *   **Write** data into columns D, E, F, and G-N.
3.  **Data Integrity**:
    *   If a `placement_no` is found in the DXF but missing in the Template's Column A, it should be flagged as an anomaly.
    *   **Reverse Top-Down Port Logic**: Ports are strictly loaded starting from Port 8 downward based on total load capacity (N). Ports 1 through (8-N) are forcefully marked as `SPARE`. The DXF's explicit port definitions are computationally overridden.

## 4. Visual Formatting Requirements
*   **Text Alignment**: All injected data should be center-aligned to match the engineering standard.
*   **Merge Persistence**: The header rows (Rows 1-4) utilize merged cells. The mapping engine must start writing specifically from **Row 5** downward and avoid overwriting merged headers.
*   **Sorting**: The final generated sheet MUST show splitters in numerical order by their indices in Column A.
