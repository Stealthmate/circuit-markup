from lxml import etree as ET
from lxml.etree import QName

def render(assets, nodes, output):
    nsmap = {
        'xlink': 'http://www.w3.org/1999/xlink',
        None: 'http://www.w3.org/2000/svg'
    }
    doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
    root = ET.Element('svg', nsmap=nsmap)
    defs = ET.SubElement(root, 'defs')
    for key, asset in assets.items():
        svg = asset['svg']
        svg.attrib['id'] = key.replace('/', '--')
        defs.append(svg)
    for nid, ninfo in nodes.items():
        if 'shape' not in ninfo:
            continue
        sid = ninfo['shape'].replace('/', '--')
        el = ET.Element('use', attrib={ QName(nsmap['xlink'], 'href'): f'#{sid}' })
        root.append(el)
    ET.ElementTree(root).write(output, doctype=doctype)
