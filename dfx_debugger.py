"""
==========================================================
 MANUAL EXTRACTION ASSISTANT — Cable Sheet Data Vacuum
 Purpose: Produces a clean, engineer-ready CSV that 
          organizes all conduit spans by their correct 
          segment (from the CABLE CALLOUT callout), 
          includes Start/End addresses, and flags 
          splitter-adjacent handholes (15ft vs 50ft).
 Usage:   python3 dfx_debugger.py
          Output: Cable_Sheet_Assistant.csv
==========================================================
"""
import ezdxf
import math
import csv
import re

# ─── CONFIGURATION ────────────────────────────────────────
TARGET_DXF    = "1_05_CX_4.2.26.dxf"
OUTPUT_CSV    = "Cable_Sheet_Assistant.csv"
SPLITTER_PROXIMITY = 50   # feet: distance to flag a span as "near a splitter"
CALLOUT_RADIUS     = 3500 # max radius to associate a span with a callout
# ──────────────────────────────────────────────────────────


def parse_seg_number(callout_name: str) -> tuple:
    """
    Extract a sortable key from a callout like 'HSP.01.05.01 144'.
    Returns (seg_int, cable_size_int) so sorting is numeric, not lexicographic.
    """
    parts = callout_name.split()
    cable_size = int(parts[-1]) if parts and parts[-1].isdigit() else 999
    nums = re.findall(r'\d+', parts[0] if parts else '')
    seg_num = int(nums[-1]) if nums else 999
    return (seg_num, cable_size)


def get_nearest_address(bx, by, house_numbers, road_names):
    """
    Build a full street address by combining:
    - Nearest house number from the ADDRESSES layer (e.g. '5932')
    - Nearest road name from the Road Names layer (e.g. 'JOHNSON POND RD')
    This matches how the DXF is structured: numbers and names are on separate layers.
    """
    best_num_dist = float('inf')
    best_num = ''
    for num, ax, ay in house_numbers:
        d = math.hypot(ax - bx, ay - by)
        if d < best_num_dist:
            best_num_dist = d
            best_num = num

    best_road_dist = float('inf')
    best_road = ''
    for road, ax, ay in road_names:
        d = math.hypot(ax - bx, ay - by)
        if d < best_road_dist:
            best_road_dist = d
            best_road = road

    if best_num and best_road:
        return f"{best_num} {best_road.strip()}"
    elif best_num:
        return best_num
    elif best_road:
        return best_road.strip()
    return '(address not found)'


def generate_cable_assistant(dxf_filepath: str, output_csv_path: str):
    print(f"\n{'='*60}")
    print(f"  Manual Extraction Assistant")
    print(f"  Loading: {dxf_filepath}")
    print(f"{'='*60}")

    try:
        doc = ezdxf.readfile(dxf_filepath)
        msp = doc.modelspace()
    except Exception as e:
        print(f"ERROR loading DXF: {e}")
        return

    # ── Stage 1: Collect all data buckets ──────────────────
    callouts     = []   # cable segment callouts
    spans        = []   # ITEM_NUMBER conduit blocks
    splitters    = []   # 1x8 splitter locations (for 15ft storage flag)
    house_numbers = []  # ADDRESSES layer: just the house number (e.g. '5932')
    road_names    = []  # Road Names layer: just the street name (e.g. 'JOHNSON POND RD')

    print("Stage 1/4: Extracting INSERT blocks...")
    for entity in msp.query('INSERT'):
        layer = entity.dxf.layer.upper()
        bx, by = entity.dxf.insert.x, entity.dxf.insert.y

        if not getattr(entity, 'attribs', None):
            continue
        attribs = {a.dxf.tag: getattr(a.dxf, 'text', '') for a in entity.attribs if hasattr(a.dxf, 'tag')}

        # --- Cable Callouts (source of truth for segment ID & cable size) ---
        if layer == 'CABLE CALLOUT':
            name = attribs.get('FIBER_1', '').strip()
            if 'HSP' in name.upper():
                sort_key = parse_seg_number(name)
                parts = name.split()
                cable_size_str = parts[-1] if parts[-1].isdigit() else 'UNK'
                callouts.append({
                    'name': name,
                    'cable_size': cable_size_str,
                    'sort_key': sort_key,
                    'x': bx, 'y': by
                })

        # --- Conduit Span blocks ---
        elif layer == 'ITEM_NUMBER':
            item_no = attribs.get('ITEM#', '').strip()
            length_raw = attribs.get('LENGTH', '0').strip()
            if not item_no:
                continue
            # Regex extract numeric length (strips prefixes like "B-F 54")
            m = re.search(r'\d+', length_raw)
            length_num = int(m.group()) if m else 0
            # Flag which cable sizes the draftsman ticked (for QC warning column)
            ticked = [s for s in ['48', '96', '144', '288', '432'] if attribs.get(f'F{s}') == '1']
            spans.append({
                'item'   : item_no,
                'length_raw': length_raw,
                'length' : length_num,
                'sp'     : attribs.get('SP', '').strip(),
                'ticked' : ','.join(ticked) if ticked else 'BLANK',
                'x': bx, 'y': by
            })

        # --- 1x8 Splitters ---
        elif '1X8 SPLITTER' in attribs.get('SPLITTER', '').upper():
            splitters.append({'name': attribs.get('SPLITTER', ''), 'x': bx, 'y': by})

    # --- Street Addresses (house numbers + road names on separate layers) ---
    print("Stage 2/4: Extracting address labels...")
    for entity in msp.query('TEXT MTEXT'):
        layer = entity.dxf.layer.upper()
        try:
            txt = entity.text if entity.dxftype() == 'MTEXT' else getattr(entity.dxf, 'text', '')
            txt = txt.strip()
            x, y = entity.dxf.insert.x, entity.dxf.insert.y
            if not txt:
                continue
            if layer == 'ADDRESSES':
                house_numbers.append((txt, x, y))
            elif layer == 'ROAD NAMES':
                road_names.append((txt, x, y))
        except:
            pass

    # Sort callouts numerically (SEG 1, 2, 3... not 1, 10, 11, 2...)
    # Deduplicate: CAD sometimes has duplicate callout blocks for the same segment
    seen_callout_names = set()
    unique_callouts = []
    for c in sorted(callouts, key=lambda x: x['sort_key']):
        if c['name'] not in seen_callout_names:
            seen_callout_names.add(c['name'])
            unique_callouts.append(c)
    callouts = unique_callouts
    print(f"  Found {len(callouts)} callouts | {len(spans)} spans | {len(splitters)} splitters | {len(house_numbers)} house numbers | {len(road_names)} road names")

    # ── Stage 2: Map each span to its closest callout ──────
    print("Stage 3/4: Mapping spans to closest segment callout...")
    for span in spans:
        best_callout = None
        min_dist = float('inf')
        for c in callouts:
            d = math.hypot(span['x'] - c['x'], span['y'] - c['y'])
            if d < min_dist and d < CALLOUT_RADIUS:
                min_dist = d
                best_callout = c
        span['callout'] = best_callout
        span['near_splitter'] = any(
            math.hypot(span['x'] - s['x'], span['y'] - s['y']) < SPLITTER_PROXIMITY
            for s in splitters
        )

    # ── Stage 3: Build per-segment output rows ─────────────
    print("Stage 4/4: Building output table...")
    rows = []
    for callout in callouts:
        seg_spans = [s for s in spans if s.get('callout') and s['callout']['name'] == callout['name']]
        seg_spans.sort(key=lambda s: s['item'])  # alphabetical A, B, C...

        # Compute Start/End address for this segment.
        # Per video: Start = address at the callout position (where cable begins).
        #            End   = address at the span physically FARTHEST from callout
        #                    (where the cable dies at the splice block).
        start_addr = get_nearest_address(callout['x'], callout['y'], house_numbers, road_names)
        if seg_spans:
            farthest_span = max(seg_spans, key=lambda s: math.hypot(s['x'] - callout['x'], s['y'] - callout['y']))
            end_addr = get_nearest_address(farthest_span['x'], farthest_span['y'], house_numbers, road_names)
        else:
            end_addr = '(no spans found)'

        # Anchor row (Row 15 in Excel) — always SPAN=0, STORAGE=50
        rows.append({
            'Segment'          : callout['name'],
            'Cable Size'       : callout['cable_size'],
            'Start Address'    : start_addr,
            'End Address'      : end_addr,
            'Item # (A/B/C…)'  : 'ANCHOR',
            'Span (ft)'        : 0,
            'Length (raw)'     : '–',
            'Storage (ft)'     : 50,
            'SP Page'          : '–',
            'CAD Checkbox (QC)': '–',
            'Notes'            : 'Row 15 anchor — SPAN always 0, STORAGE always 50'
        })

        # Data rows
        for s in seg_spans:
            storage = 15 if s['near_splitter'] else 50
            rows.append({
                'Segment'          : callout['name'],
                'Cable Size'       : callout['cable_size'],
                'Start Address'    : start_addr,
                'End Address'      : end_addr,
                'Item # (A/B/C…)'  : s['item'],
                'Span (ft)'        : s['length'],
                'Length (raw)'     : s['length_raw'],
                'Storage (ft)'     : storage,
                'SP Page'          : s['sp'],
                'CAD Checkbox (QC)': s['ticked'],
                'Notes'            : '⚠️ CHECKBOX MISMATCH' if s['ticked'] not in ['BLANK', callout['cable_size']] else ''
            })

    # ── Stage 4: Write CSV ─────────────────────────────────
    if not rows:
        print("WARNING: No data rows generated. Check DXF file and layer names.")
        return

    headers = list(rows[0].keys())
    with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as f:  # utf-8-sig for Excel compatibility
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ SUCCESS")
    print(f"   Output:    {output_csv_path}")
    print(f"   Segments:  {len(callouts)}")
    print(f"   Data Rows: {len(rows) - len(callouts)} span rows + {len(callouts)} anchor rows")
    print(f"\n   Open Cable_Sheet_Assistant.csv in Excel.")
    print(f"   Each segment shows: ANCHOR row first, then spans A/B/C...")
    print(f"   ⚠️  CHECKBOX MISMATCH rows = spans where draftsman ticked wrong size.")


if __name__ == '__main__':
    generate_cable_assistant(TARGET_DXF, OUTPUT_CSV)