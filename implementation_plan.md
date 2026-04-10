# Cable Sheet Implementation Plan

## Overview
This plan details the automation of the `CABLE SHEET`, which requires reading `<ModelItem#>` blocks from the DXF to sequentially list distance (SPAN) and slack (STORAGE) values for individual cable segments.

## 1. Segment Mapping & Loop Construction (`excel_writer.py`)
- **Letter to SEG Mapping**: The CAD utilizes an alphabetical `ITEM#` ID (`A`, `B`, `C`... `AA`, `AB`). I will map these mathematically to numeric segment values (`SEG 1`, `SEG 2`, `SEG 3`... `SEG 27`, `SEG 28`). 
- **Horizontal Insertion Logic**: The Excel writer will loop through columns mathematically per segment (Jump +5 columns for every new segment increment).
  - `SEG 1` = Col 3 (C)
  - `SEG 2` = Col 8 (H)
  - `SEG n` = `3 + ((n-1) * 5)`

## 2. DXF Data Extraction (`pipeline.py`)
- Locate all blocks named `ModelItem#` or `*U...` residing on the `ITEM_NUMBER` layer.
- Extract `ITEM#`, `LENGTH` (Span), `SP` (Storage), and `F48`/`F96`/`F144` attributes.
- **Group & Sort**: Group all blocks structurally by their `ITEM#`. Sort the items within each group geographically if possible, or leave as native CAD-drawn order.
- **Method Inference**: Cross-check the layer of the block against the Lumos standard. E.g., if drawn on an `AERIAL` or `STRAND` designated layer, default the Dropdown to "Aerial". Otherwise, default to "New Conduit".

## 3. Top-of-Block Header Population
- **Address Bounding**: For the `START` and `END` address blocks, the tool will perform a spatial search logic (using the `ezdxf.math` bounding boxes) to find the closest `TEXT` or `MTEXT` element representing a street address. If a definitive address cannot be confidently determined algorithmically, the fields will be left blank for the engineer to fill quickly, avoiding data contamination.
- **Cable Size**: Extract the size directly from the CAD block's flag (`F48=1` -> Size 48).

## 4. Row 15+ Engineering Rules implementation
- Row 15 will correctly inherit `SPAN: 0` and pull the starting `STORAGE` from the first item.
- Rows 16+ will sequentially list the subsequent Spans and Storage values pulled from the CAD, leaving `RISER` blank unless specifically flagged by a riser block. 

> [!CAUTION]
> Geographic ordering of the `SPAN` sub-elements relies heavily on the order they were drafted in the CAD file. The CAD file does not link them strictly in a line. We will attempt a spatial point algorithm to trace them in a logical path.
