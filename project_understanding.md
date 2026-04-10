# CAD to Excel Automation: Project Understanding

## 1. Project Goal
Automate the extraction of data from AutoCAD design files ([.dxf](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/1_3_CX_04.02.2026.dxf) format) to populate a standardized Excel workbook (`CHST02-01 CX WORKBOOK.xlsx`). This automation replaces a manual process that currently takes engineers 6-8 hours per job.

## 2. Input Data & Structure
The primary source of data is an AutoCAD file (delivered natively as [.dwg](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/CHST%2002-01%20-%20CX%20DESIGN.dwg), but requires [.dxf](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/1_3_CX_04.02.2026.dxf) format for smooth Python automation). The drawing contains "Blocks" loaded with "Attributes" rather than just standard lines. We extract these blocks.

### Key AutoCAD Blocks
1. **1x8 SPLITTER Block**:
   - Contains explicit texts like `OLT01_113P__FQVRNC`.
   - Stores the Address, Name, and Fiber Allocation Port (e.g., `113`).
   - Represents the primary splitter that feeds into 1x4 splitters.
2. **ModelItem# Block (Construction Notes)**:
   - Resides on the `ITEM_LAYER`.
   - Contains precise tags like `LENGTH` (span footage), `SP`, `COND_SZ`, `COND_QTY`.
   - Used for calculating cable spans and labor sheets without measuring polyline lengths mathematically.

## 3. Strict Lumos Business Logic (Master Prompt Integration)
The client previously relied on an LLM to format Excel data. We are replacing this LLM entirely by embedding its rules mathematically into our python output:
- **8-Port Padding**: Every 1x8 splitter must output exactly 8 lines in the 1x4 sheet, regardless of whether they exist. If port 5 does not exist, row 5 must read `SPARE`. Rows cannot be zipped or collapsed.
- **T-Count Mapping**: Secondary ports deterministically map to T-Counts (Port 1 = 1-4, Port 2 = 5-8).
- **Secondary Naming**: Naming convention is `OLT{OLT_NO}_{PLACEMENT_NO}P_{SECONDARY_NO}S_{MARKET}`.
- **Mismatch Detection**: The software must trust the Feeder `PAIR_CNT` as the primary source of truth for the Secondary Port Number. If the 1x4 splitter name contradicts the `PAIR_CNT`, we must flag it but follow the Pair Count.
The automation tool must generate an Excel file featuring these populated tabs:

1. **House Count Sheet**:
   - Lists addresses mapped to service locations.
   - *Current Issue*: Client reported the master prompt logic currently used is inconsistent. We need the client to ensure uniform data hygiene for automation.
2. **1x8 Splitter Sheet** (`CABLE TO 1X8 SPLICING`):
   - Pulled directly from the 1x8 blocks. Correlates the OLT, Address, Name, and mapped Ports.
3. **1x8 to 1x4 Splitter Sheet** (`SPLICING 1X8 TO 1X4 SPLITS`):
   - Complex logic mapping: Every 1x8 splitter feeds eight 1x4 splitters. Each 1x4 splitter feeds up to 4 services (houses/businesses). The script must track these relationships.
4. **Labor Span Sheet** & **Cable Sheet**:
   - Pulled from the `ModelItem#` blocks (construction notes) leveraging tags like `LENGTH`.
5. **Material Sheet**:
   - Populated fundamentally by a `Count` function. E.g., The primary splitter value equals the total count of 1x8 blocks (minus design spares).

### Unmentioned / Structural Sheets (Likely non-automated or formula-driven)
The workbook contains 14 sheets in total. The remaining 8 are: `COVER SHEET`, `MAP`, `LABOR` (likely a formula summary of span), `TOTALS` (formula summary), `MEW`, `FINAL ADDRESS LIST` (likely references House Count), `PERMITS`, and `Ring splicing`. These generally don't require heavy DXF parsing but we will confirm with the client.

## 4. Technical Approach
1. **Language**: Python. Deliverable will be packaged as a standalone executable (`.exe`) via `PyInstaller`.
2. **Parsing**: `ezdxf` library to read [.dxf](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/1_3_CX_04.02.2026.dxf) files without requiring AutoCAD installation. Logic explicitly drops placeholder blocks (e.g., tags with `### ROAD ST` or empty items) to protect statistical integrity.
3. **Processing**: Consolidate block attributes into structured `pandas` DataFrames. We apply the strict Master Prompt padding mathematics here (Secondary positional overrides and T-count arrays).
4. **Exporting**: Use `openpyxl` to open the blank template workbook and insert data into specified cells. 
5. **Fallback Native Generation**: If the client opens the GUI application and provides ONLY a [.dxf](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/1_3_CX_04.02.2026.dxf) file without explicitly referencing a valid `CHST02-01 CX WORKBOOK.xlsx` template target, the `openpyxl` pipeline will dynamically construct a raw Excel workbook composed of the 6 data sheets with dynamically generated column headers to ensure delivery never fails.

## 5. Potential Roadblocks / Client Requirements
- **DXF Delivery**: Python cannot perfectly parse [.dwg](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/CHST%2002-01%20-%20CX%20DESIGN.dwg) without proprietary background tools. The client must supply [.dxf](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/1_3_CX_04.02.2026.dxf) formats.
- **Data Hygiene**: The script is literal. If engineers name blocks `1x8 Splitter` today and `1-8-SPLIT` tomorrow, the script breaks. Strict standardization must be enforced by the client.

## 6. Pre-Deployment Verification Checklist
Before packaging this Python project into a final executable `.exe` file for the client, the following empirical tests must be manually verified:
- **Baseline Accuracy**: Feed the [1_3_CX_04.02.2026.dxf](file:///Users/asta/Downloads/Ronnie%20Fiverr%20Automation/1_3_CX_04.02.2026.dxf) into the script and compare the output workbook side-by-side with an actual manual Excel workbook the client sent us for that exact project. 
- **Row Formats**: Ensure that `openpyxl` successfully maintains the original background colors (yellows/reds) when inserting strings directly into cells.
- **Edge Case Rejection Checklist**:
   - Make sure no blocks labeled exactly `OLT#` appear in the Splitter tables.
   - Make sure no raw strings with `### ROAD ST` appear in the House Counters.
- **Dependency Freeze**: Verify that strictly standard modules (`ezdxf`, `pandas`, `openpyxl`) are pinned securely to prevent unexpected deprecation crashes in standalone environments.
