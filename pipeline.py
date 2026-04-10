import pandas as pd
import ezdxf
import re

def parse_dxf_data(filepath):
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()
    
    data = {
        'splitters_1x8': {},
        'splitters_1x4': [],
        'house_count': [],
        'labor_spans': [],
        'cable_spans': {}
    }
    
    splitters_1x4_raw = []
    
    temp_cable_blocks = []
    callouts = []
    
    # Pass 1: Collect entities
    for entity in msp.query('INSERT'):
        if not getattr(entity, 'attribs', None):
            continue
            
        attribs = {a.dxf.tag: a.dxf.text for a in entity.attribs if hasattr(a.dxf, 'tag')}
        name = entity.dxf.name.upper()
        
        # Labor Spans
        if 'MODELITEM' in name:
            data['labor_spans'].append(attribs)
            
        fiber_co = attribs.get('FIBER_CO', '').strip().upper()
        splitter_tag = attribs.get('SPLITTER', '').strip().upper()
        
        # Parse Cable Callouts for spatial Segment mapping
        if entity.dxf.layer.upper() == 'CABLE CALLOUT':
            fiber1 = attribs.get('FIBER_1', '').upper()
            if 'HSP' in fiber1:
                callouts.append({'text': fiber1, 'x': entity.dxf.insert.x, 'y': entity.dxf.insert.y})
        
        # Edge Case Cleanup
        if 'OLT#' in splitter_tag or 'OLT#' in fiber_co:
            continue
            
        # Parse 1x8 Primary Splitters
        if '1X8 SPLITTER' in splitter_tag:
            parts = splitter_tag.split('1X8 SPLITTER ')
            if len(parts) > 1:
                base_name = parts[1].strip()
                placement_no = attribs.get('SPLITTER_NUM', '')
                if not placement_no and '_' in base_name:
                    match = re.search(r'_(\d+)P_', base_name)
                    if match:
                        placement_no = match.group(1)
                
                data['splitters_1x8'][base_name] = {
                    'placement_no': placement_no,
                    'placement_address': attribs.get('PLACEMEN', '').strip(),
                    'base_1x8_name': base_name,
                    'x': entity.dxf.insert.x,
                    'y': entity.dxf.insert.y,
                    'ports': {} # Ports 1-8 dictionaries
                }
                
        # Parse 1x4 Secondary Splitters
        elif '1X4 SPLITTER' in fiber_co:
            attribs['X'] = entity.dxf.insert.x
            attribs['Y'] = entity.dxf.insert.y
            splitters_1x4_raw.append(attribs)
            
        # Collect items for Cable Sheet temporarily
        if entity.dxf.layer.upper() == 'ITEM_NUMBER':
            item_no = attribs.get('ITEM#')
            if item_no:
                cable_size = '48'
                if attribs.get('F96') == '1': cable_size = '96'
                elif attribs.get('F144') == '1': cable_size = '144'
                elif attribs.get('F288') == '1': cable_size = '288'
                elif attribs.get('F432') == '1': cable_size = '432'
                
                temp_cable_blocks.append({
                    'SPAN': attribs.get('LENGTH', '0'),
                    'STORAGE': attribs.get('SP', '0'),
                    'SIZE': cable_size,
                    'METHOD': 'New Conduit', # Default per logic plan
                    'X': entity.dxf.insert.x,
                    'Y': entity.dxf.insert.y
                })
            
    import math
    print("Executing geographic segment calculations...")
    
    # Build actual cable_spans by finding nearest CABLE CALLOUT
    for block in temp_cable_blocks:
        best_dist = float('inf')
        target_seg_num = 0
        
        for c in callouts:
            d = math.hypot(c['x'] - block['X'], c['y'] - block['Y'])
            if d < best_dist:
                best_dist = d
                # Extract segment number using regex on "HSP.01.03.14 48" -> "14"
                match = re.search(r'HSP\.\d{2}\.\d{2}\.(\d{2})', c['text'])
                if match:
                    target_seg_num = int(match.group(1))
                    
        if target_seg_num > 0:
            if target_seg_num not in data['cable_spans']:
                data['cable_spans'][target_seg_num] = []
            data['cable_spans'][target_seg_num].append(block)

    print("Executing geographic address calculations...")
    addresses = []
    for entity in msp.query('TEXT MTEXT'):
        if entity.dxf.layer.upper() == 'NOTES_1_FULL_ADDRESS':
            txt = entity.text if entity.dxftype() == 'MTEXT' else entity.dxf.text
            if hasattr(entity.dxf, 'insert'):
                addresses.append((entity.dxf.insert.x, entity.dxf.insert.y, txt))
                
    def get_nearest_address(bx, by):
        best_dist = float('inf')
        best_txt = ''
        for ax, ay, txt in addresses:
            d = math.hypot(ax - bx, ay - by)
            if d < best_dist:
                best_dist = d
                best_txt = txt
        return best_txt
        
    for seg_num, spans in data['cable_spans'].items():
        if not spans: continue
        
        # Determine closest address text for the first span block and the last span block
        start_x, start_y = spans[0].get('X', 0), spans[0].get('Y', 0)
        end_x, end_y = spans[-1].get('X', 0), spans[-1].get('Y', 0)
        
        spans[0]['START_ADDRESS'] = get_nearest_address(start_x, start_y)
        spans[0]['END_ADDRESS'] = get_nearest_address(end_x, end_y)

    print("Mapping True Positions...")
    temp_1x4_map = {}
    
    for s_1x4 in splitters_1x4_raw:
        pair_cnt = s_1x4.get('PAIR_CNT', '')
        
        # Strict parsing of Master Prompt 'PAIR_CNT' text
        # e.g. "IN: OLT01_113P_FQVRNC-8 OUT: 29-32"
        match = re.search(r'IN:\s*([^-\s]+)-(\d+)\s+OUT:\s*([\d-]+)', pair_cnt)
        if match:
            base_name = match.group(1)
            original_port_no = int(match.group(2))
            
            houses = []
            for i in range(1, 5):
                ad_raw = s_1x4.get(f'ST_AD_{i}', '').strip().upper()
                if ad_raw and '###' not in ad_raw:
                    # Unit parsing
                    ad_main = ad_raw
                    unit_ref = ''
                    
                    if '#' in ad_raw:
                        parts = ad_raw.split('#', 1)
                        ad_main = parts[0].strip()
                        unit_ref = '#' + parts[1].strip()
                    elif ' UNIT ' in ad_raw:
                        parts = ad_raw.split(' UNIT ', 1)
                        ad_main = parts[0].strip()
                        unit_ref = 'UNIT ' + parts[1].strip()
                        
                    full_house_addr = (ad_main + ' ' + unit_ref).strip()
                    houses.append(full_house_addr)
                    
                    data['house_count'].append({
                        'ADDRESS': ad_main,
                        'UNIT': unit_ref,
                        'FED_FROM_1X4': s_1x4.get('FIBER_CO', '')
                    })
                else:
                    houses.append('')
                    
            if base_name in data['splitters_1x8']:
                if base_name not in temp_1x4_map:
                    temp_1x4_map[base_name] = []
                    
                temp_1x4_map[base_name].append({
                    'original_port': original_port_no,
                    '1x4_name': s_1x4.get('FIBER_CO', ''),
                    'placement_address_1x4': s_1x4.get('PLACEMEN', ''),
                    'houses': houses,
                    'x': s_1x4.get('X', 0),
                    'y': s_1x4.get('Y', 0)
                })

    # Apply Reverse Top-Down Port Assignment
    t_counts = ["1-4", "5-8", "9-12", "13-16", "17-20", "21-24", "25-28", "29-32"]
    
    for base_name, splitters in temp_1x4_map.items():
        # Sort by original port index to maintain logical sequence (1S, 2S, 3S...)
        splitters.sort(key=lambda x: x['original_port'])
        
        current_port = 8
        # Assign mathematically in reverse
        for sp in reversed(splitters):
            actual_port = current_port
            
            data['splitters_1x8'][base_name]['ports'][actual_port] = {
                '1x4_name': sp['1x4_name'], # Retain the original mismatched name per client request
                't_count': t_counts[actual_port - 1],
                'placement_address_1x4': sp['placement_address_1x4'],
                'split_reference': f"{base_name}, {actual_port}",
                'houses': sp['houses']
            }
            current_port -= 1
                
    data['splitters_1x4'] = splitters_1x4_raw            
    return data

if __name__ == '__main__':
    d = parse_dxf_data("1_3_CX_04.02.2026-Final.dxf")
    import json
    
    print(f"\nTotal 1x8 Base Names detected: {len(d['splitters_1x8'])}")
    keys = list(d['splitters_1x8'].keys())
    if keys:
        print("\n--- SAMPLE MAPPED PRIMARY SPLITTER ---")
        print(json.dumps(d['splitters_1x8'][keys[0]], indent=2))
