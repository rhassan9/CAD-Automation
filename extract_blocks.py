import sys
import ezdxf
from collections import Counter

def main():
    print("Loading DXF...")
    doc = ezdxf.readfile("1_3_CX_04.02.2026.dxf")
    msp = doc.modelspace()
    
    counts = Counter()
    
    print("Scanning all INSERT entities...")
    for entity in msp.query('INSERT'):
        try:
            for att in entity.attribs:
                if 'OLT' in str(att.dxf.text).upper():
                    attribs = {a.dxf.tag: a.dxf.text for a in entity.attribs if hasattr(a.dxf, 'tag')}
                    print(f"Found OLT in block '{entity.dxf.name}': {attribs}")
                    break
        except AttributeError:
            pass


if __name__ == '__main__':
    main()
