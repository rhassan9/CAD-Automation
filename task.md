# Cable Sheet - Execution Checklist

- `[x]` **Phase 1: Pipeline Extraction (`pipeline.py`)**
  - `[x]` Extract `ModelItem#` blocks on layer `ITEM_NUMBER`.
  - `[x]` Parse attributes (`ITEM#`, `LENGTH`, `SP`, `F48`/`F96`/`F144`).
  - `[x]` Infer `Method` via physical layer (Aerial/Strand vs Underground).
  - `[x]` Convert alphabetical `ITEM#` to numeric Segments.
  - `[x]` Geographically infer Start/End Addresses via nearest `MTEXT`.
  - `[x]` Sequence block spans to prepare for injection.
- `[x]` **Phase 2: Excel Writer Engine (`excel_writer.py`)**
  - `[x]` Map numeric `SEG` values to dynamic Horizontal Offsets (Cols C, H, M...).
  - `[x]` Inject the Address strings into the top section.
  - `[x]` Output Dropdowns (Cable Size, Method).
  - `[x]` Inject physical span sequencing logic starting at Row 15.
- `[x]` **Phase 3: Verification & Walkthrough**
  - `[x]` Run end-to-end tests against `1_3_CX_04.02.2026-Final.dxf`.
  - `[x]` Validate the math (`0` span row + shifting slack values).
  - `[x]` Finalize walkthrough artifact.
