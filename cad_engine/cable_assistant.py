"""
==========================================================
 MANUAL EXTRACTION ASSISTANT v4 — Cable Sheet Data Vacuum
 
 Root Cause Analysis:
 - v1-v3 failed because:
   a) The SP attribute on ITEM_NUMBER blocks is NOT the 
      viewport page number (SP-1, SP-2). It is a separate 
      internal drafting counter with no consistent mapping.
   b) For 48-count segments, multiple callouts share the 
      same geographic area, so radius-based lookup assigns 
      the same spans to multiple segments.

 CORRECT APPROACH:
 - Use "Exclusive Closest Callout" assignment:
   Each span belongs to EXACTLY ONE callout — the one it is 
   geographically closest to. No span is shared.
 - This is geometrically equivalent to a Voronoi partition:
   each span is claimed by its nearest callout center.
 - Then apply a max radius cap (1800 units) to exclude spans 
   that are genuinely in unrelated areas of the map.
==========================================================
"""
import ezdxf
import math
import csv
import re
from collections import Counter
from .errors import CADExtractionError, CableAssistantError


SPLT_PROXIMITY    = 150       # Units: PROP_HH within this dist of 1x8 splitter = SPLT handhole
SPAN_HH_PROXIMITY = 150       # Units: span within this dist of a PROP_HH = attached to that HH
# ──────────────────────────────────────────────────────────


def normalize_callout_name(name: str) -> str:
    """Fix CAD typos like 'HSP.01,05.25' -> 'HSP.01.05.25'."""
    return name.replace(',', '.')


def clean_mtext(text: str) -> str:
    """Aggressively strip AutoCAD formatting codes (\\f..., \\P, \\C...) from MTEXT strings."""
    # Remove formatting blocks: {\\fMicrosoft Sans Serif|b0|i0|c0|p34; ... } -> ...
    # This regex looks for { ... ; and removes it, but keeps the text after it.
    # Actually, simpler: MTEXT codes usually look like \\P (newline), \\f...; (font), \\C...; (color).
    text = text.replace('\\P', ' ')
    text = re.sub(r'\\f[^;]+;', '', text)
    text = re.sub(r'\\C\d+;', '', text)
    text = re.sub(r'[{}]', '', text)
    return text.strip()



def parse_seg_number(name: str) -> tuple:
    parts = name.split()
    cable_size = int(parts[-1]) if parts and parts[-1].isdigit() else 999
    nums = re.findall(r'\d+', parts[0] if parts else '')
    seg_num = int(nums[-1]) if nums else 999
    return (seg_num, cable_size)


def build_full_address(bx, by, house_numbers, road_names):
    best_num  = min(house_numbers, key=lambda h: math.hypot(h[1]-bx, h[2]-by), default=None)
    best_road = min(road_names,    key=lambda r: math.hypot(r[1]-bx, r[2]-by), default=None)
    num_str   = best_num[0].strip()  if best_num  else ''
    road_str  = best_road[0].strip() if best_road else ''
    if num_str and road_str:
        return f"{num_str} {road_str}"
    return num_str or road_str or '(not found)'


def generate_cable_assistant(dxf_filepath: str, output_csv_path: str):
    print(f"\n{'='*60}")
    print(f"  Cable Sheet Manual Extraction Assistant")
    print(f"  Loading: {dxf_filepath}")
    print(f"{'='*60}")

    try:
        doc = ezdxf.readfile(dxf_filepath)
        msp = doc.modelspace()
    except Exception as e:
        print(f"ERROR: {e}")
        return

    callouts      = []
    spans         = []
    splitters     = []   # 1x8 splitter INSERT blocks
    prop_hh       = []   # proposed handholes (PROP_HH layer)
    house_numbers = []
    road_names    = []
    bore_labels   = []

    print("Stage 1/4: Extracting blocks and detecting Job Prefix...")
    
    # Pre-scan to dynamically determine JOB_PREFIX across blocks AND text
    prefixes = []
    
    # 1. Check native INSERT blocks
    for entity in msp.query('INSERT'):
        if entity.dxf.layer.upper() == 'CABLE CALLOUT':
            if not getattr(entity, 'attribs', None): continue
            attribs = {a.dxf.tag: getattr(a.dxf, 'text', '') for a in entity.attribs if hasattr(a.dxf, 'tag')}
            name = attribs.get('FIBER_1', '').strip().upper()
            match = re.search(r'[A-Z]+[.\s]*(\d{2}[.,]\d{2})', name)
            if match:
                prefixes.append(match.group(1).replace(',', '.'))
                
    # 2. Check native MTEXT arrays (specifically for CHST routing)
    if not prefixes:
        for entity in msp.query('MTEXT TEXT'):
            text = entity.text if entity.dxftype() == 'MTEXT' else entity.dxf.text
            clean = clean_mtext(text).upper()
            match = re.search(r'[A-Z]+[.\s]*(\d{2}[.,]\d{2})', clean)
            if match and 'SP-' not in clean and len(clean) < 150:
                prefixes.append(match.group(1).replace(',', '.'))
                
    if not prefixes:
        raise CableAssistantError(
            "CRITICAL: No valid CABLE CALLOUT blocks or text found with a recognized '[PREFIX].XX.XX' structure.\n"
            "The Cable Sheet cannot compute its dynamically detected Job Prefix and will abort."
        )
        

    JOB_PREFIX = Counter(prefixes).most_common(1)[0][0]
    print(f"  Detected Primary Job Prefix: {JOB_PREFIX} (Filtering out cross-job bounds)")

    for entity in msp.query('INSERT'):
        layer = entity.dxf.layer.upper()
        bx, by = entity.dxf.insert.x, entity.dxf.insert.y
        if not getattr(entity, 'attribs', None):
            continue
        attribs = {a.dxf.tag: getattr(a.dxf, 'text', '') for a in entity.attribs if hasattr(a.dxf, 'tag')}

        if layer == 'CABLE CALLOUT':
            name = attribs.get('FIBER_1', '').strip()
            name = normalize_callout_name(name)  # Fix any commas in the name
            if JOB_PREFIX in name:
                sort_key = parse_seg_number(name)
                parts = name.split()
                cable_size_str = parts[-1] if parts and parts[-1].isdigit() else 'UNK'
                callouts.append({
                    'name': name, 'cable_size': cable_size_str,
                    'sort_key': sort_key, 'x': bx, 'y': by
                })

        elif layer == 'PROP_HH':
            # Proposed handholes — used to determine SPLT vs standard storage
            hh_type = attribs.get('HH_TYPE', '?')
            prop_hh.append({'type': hh_type, 'x': bx, 'y': by, 'is_splt': False})

        elif layer == 'ITEM_NUMBER':
            item_no = attribs.get('ITEM#', '').strip()
            length_raw = attribs.get('LENGTH', '0').strip()
            if not item_no:
                continue
            m = re.search(r'\d+', length_raw)
            length_num = int(m.group()) if m else 0
            ticked = [s for s in ['48','96','144','288','432'] if attribs.get(f'F{s}') == '1']
            spans.append({
                'item': item_no, 'length_raw': length_raw, 'length': length_num,
                'sp_attr': attribs.get('SP', '').strip(),
                'ticked': ','.join(ticked) if ticked else 'BLANK',
                'x': bx, 'y': by
            })

        elif '1X8 SPLITTER' in attribs.get('SPLITTER', '').upper():
            splitters.append({'name': attribs.get('SPLITTER',''), 'x': bx, 'y': by})
    print("Stage 2/4: Extracting text labels...")
    for entity in msp.query('TEXT MTEXT'):
        layer = entity.dxf.layer.upper()
        try:
            txt = entity.text if entity.dxftype() == 'MTEXT' else getattr(entity.dxf, 'text', '')
            clean_txt = clean_mtext(txt)
            x, y = entity.dxf.insert.x, entity.dxf.insert.y
            if not clean_txt: continue
            
            # Extract MTEXT callouts for boundary framing (Stage 2 part B)
            if JOB_PREFIX in clean_txt.replace(',', '.'):
                match = re.search(r'[A-Z]+[.\s]*(\d{2}[.,]\d{2}[.,]\d{2,3})', clean_txt)
                if match:
                    # Dynamically rebuild strict callout naming form
                    rebuilt_name = f"{JOB_PREFIX}.{match.group(1)}".replace(',', '.')
                    sort_key = parse_seg_number(rebuilt_name)
                    # Try to regex cable size next to it, e.g. "CHES... 48"
                    size_match = re.search(r'\b(48|96|144|288|432)\b', clean_txt)
                    cable_size_str = size_match.group(1) if size_match else 'UNK'
                    
                    callouts.append({
                        'name': rebuilt_name, 'cable_size': cable_size_str,
                        'sort_key': sort_key, 'x': x, 'y': y
                    })

            if layer == 'ADDRESSES':
                house_numbers.append((clean_txt, x, y))
            elif layer == 'ROAD NAMES':
                road_names.append((clean_txt, x, y))
            elif 'BORE' in layer or 'DIREC' in layer:
                if re.match(r'^[A-Z]-[A-Z]\s+\d+', clean_txt):
                    bore_labels.append({'label': clean_txt.replace("'","").strip(), 'x': x, 'y': y})
        except:
            pass

    # Flag SPLT handholes: any PROP_HH within SPLT_PROXIMITY of a 1x8 splitter
    for hh in prop_hh:
        hh['is_splt'] = any(
            math.hypot(hh['x'] - s['x'], hh['y'] - s['y']) < SPLT_PROXIMITY
            for s in splitters
        )
    splt_hh   = [hh for hh in prop_hh if hh['is_splt']]
    std_hh    = [hh for hh in prop_hh if not hh['is_splt']]

    # Deduplicate callouts — keep only one per name (the closest one to SP-1 makes no sense here, just keep first)
    seen = set()
    unique_callouts = []
    for c in sorted(callouts, key=lambda x: x['sort_key']):
        if c['name'] not in seen:
            seen.add(c['name'])
            unique_callouts.append(c)
    callouts = unique_callouts
    print(f"  {len(callouts)} unique callouts | {len(spans)} spans | {len(splitters)} splitters | "
          f"{len(splt_hh)} SPLT handholes | {len(std_hh)} standard handholes")

    # ── EXCLUSIVE VORONOI ASSIGNMENT ───────────────────────
    # Each span goes to exactly one callout — the nearest one.
    # Cap at MAX_RADIUS so isolated spans don't travel across the whole map.
    print("Stage 3/4: Voronoi-assigning spans to callouts...")
    for span in spans:
        nearest_callout = None
        nearest_dist    = float('inf')
        for c in callouts:
            d = math.hypot(span['x'] - c['x'], span['y'] - c['y'])
            if d < nearest_dist:
                nearest_dist    = d
                nearest_callout = c
        span['callout'] = nearest_callout if nearest_dist <= 1800 else None

        # SPLT storage: is this span's nearest PROP_HH a SPLT type?
        if prop_hh:
            nearest_hh = min(prop_hh, key=lambda h: math.hypot(h['x']-span['x'], h['y']-span['y']))
            span['near_splt'] = nearest_hh['is_splt']
        else:
            span['near_splt'] = False

    orphans = sum(1 for s in spans if s['callout'] is None)
    print(f"  {len(spans)-orphans} spans assigned | {orphans} orphans (too far from any callout)")

    # ── BUILD OUTPUT ROWS ──────────────────────────────────
    print("Stage 4/4: Building output table...")
    rows = []
    for callout in callouts:
        seg_spans = [s for s in spans if s.get('callout') and s['callout']['name'] == callout['name']]
        seg_spans.sort(key=lambda s: s['item'])

        start_addr = build_full_address(callout['x'], callout['y'], house_numbers, road_names)
        if seg_spans:
            farthest = max(seg_spans, key=lambda s: math.hypot(s['x']-callout['x'], s['y']-callout['y']))
            end_addr = build_full_address(farthest['x'], farthest['y'], house_numbers, road_names)
        else:
            end_addr = '(no spans found)'

        # Anchor row — always SPAN=0, STORAGE=50, Method=New Conduit
        rows.append({
            'Segment'       : callout['name'],
            'Cable Size'    : callout['cable_size'],
            'Method'        : 'New Conduit',
            'Start Address' : start_addr,
            'End Address'   : end_addr,
            'Item #'        : 'ANCHOR',
            'Span (ft)'     : 0,
            'Bore Label'    : '–',
            'Storage (ft)'  : 50,
            'SP Attr'       : '–',
            'QC (Checkbox)' : '–',
            'Notes'         : 'ANCHOR — SPAN=0, STORAGE=50 always'
        })

        for s in seg_spans:
            # Bore label: nearest PROPOSED_DIREC_BORE text annotation
            if bore_labels:
                nb    = min(bore_labels, key=lambda b: math.hypot(b['x']-s['x'], b['y']-s['y']))
                nb_d  = math.hypot(nb['x']-s['x'], nb['y']-s['y'])
                bore  = nb['label'] if nb_d < 300 else '–'
            else:
                bore = '–'

            # Storage: 15 if nearest handhole is SPLT, else 50
            storage = 15 if s['near_splt'] else 50

            qc_note = ''
            if s['ticked'] not in ['BLANK', callout['cable_size']]:
                qc_note = f"⚠️ checkbox={s['ticked']} expected={callout['cable_size']}"

            rows.append({
                'Segment'       : callout['name'],
                'Cable Size'    : callout['cable_size'],
                'Method'        : 'New Conduit',
                'Start Address' : start_addr,
                'End Address'   : end_addr,
                'Item #'        : s['item'],
                'Span (ft)'     : s['length'],
                'Bore Label'    : bore,
                'Storage (ft)'  : storage,
                'SP Attr'       : s['sp_attr'],
                'QC (Checkbox)' : s['ticked'],
                'Notes'         : qc_note
            })

    if not rows:
        raise CADExtractionError("WARNING: No valid Cable Sheet spans were successfully geometrically matched to Callouts. Result is empty.")

    headers = list(rows[0].keys())
    with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    span_rows = len(rows) - len(callouts)
    print(f"\n✅ SUCCESS: {output_csv_path}")
    print(f"   Segments: {len(callouts)} | Span rows: {span_rows}")