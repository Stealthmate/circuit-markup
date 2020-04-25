from lxml import etree as ET
from lxml.etree import QName
import numpy as np

def formatID(_id):
    return _id.replace("/", "--")

def rotMat(a):
    return np.array([
        [np.cos(a), -np.sin(a)],
        [np.sin(a), np.cos(a)]
    ])

def vecAngle(a, b):
    return np.arctan2(a[1], a[0]) - np.arctan2(b[1], b[0])

class Renderer:
    def __init__(self, assets, nodes, edges):
        self.assets = assets
        self.nodes = nodes
        self.edges = edges
        self.NS = {
            'xlink': 'http://www.w3.org/1999/xlink',
            None: 'http://www.w3.org/2000/svg'
        }

        self.bounds = ([], [])

    def updateBounds(self, xs=[], ys=[]):
        self.bounds[0].extend(xs)
        self.bounds[1].extend(ys)

    def renderLineEdge(self, start, end, attr):
        self.updateBounds([start[0], end[0]], [start[1], end[1]])
        return ET.Element('line', attrib={
            'x1': str(start[0]),
            'y1': str(start[1]),
            'x2': str(end[0]),
            'y2': str(end[1]),
            'stroke-width': '3',
            'stroke': 'black',
            'stroke-linejoin': 'miter',
            'stroke-linecap': 'round'
        })

    def renderEdge(self, edge):
        start = np.array(edge['start'])
        end = np.array(edge['end'])
        print("From", start, "To", end)
        attr = edge
        if 'shape' not in attr:
            return self.renderLineEdge(start, end, attr)

        g = ET.Element('g')
        aid = attr['shape']
        asset = self.assets[aid]
        penter = np.array(asset['enter'])
        pexit = np.array(asset['exit'])

        edge_d = end - start
        edge_mid = start + edge_d/2

        el_d = pexit - penter
        el_mid = penter + el_d/2

        edge_el_d = edge_d - el_d
        angle = vecAngle(edge_d, el_d)
        M = rotMat(angle)

        pos = edge_mid - M @ el_mid

        comp = ET.SubElement(g, 'use')
        comp.attrib[QName(self.NS['xlink'], 'href')] = '#' + formatID(aid)
        comp.attrib['x'] = str(pos[0])
        comp.attrib['y'] = str(pos[1])
        comp.attrib['transform'] = f'rotate({180 * angle / np.pi} {pos[0]} {pos[1]})'

        bounds = np.array([
            [0, 0],
            [0, asset['width']],
            [asset['height'], 0],
            [asset['width'], asset['height']]
        ]).T
        r = pos + (M @ bounds).T
        self.updateBounds(r[:,0], r[:,1])

        comp_offset = M @ (el_d)
        # enter_point = start + edge_offset
        g.append(self.renderLineEdge(start, edge_mid - comp_offset/2, {}))
        g.append(self.renderLineEdge(edge_mid + comp_offset/2, end, {}))
        # exit_point = end - edge_offset
        # g.append(self.renderLineEdge(exit_point, end, {}))

        return g

    def renderNode(self, nid, ninfo):

        g = ET.Element('g')

        if 'shape' in ninfo:
            sid = formatID(ninfo['shape'])
            el = ET.SubElement(g, 'use', attrib={
                QName(self.NS['xlink'], 'href'): f'#{sid}',
                'x': str(ninfo['x']),
                'y': str(ninfo['y'])
            })

        if 'label' in ninfo:
            label = ninfo['label']
            x = ninfo['x']
            y = ninfo['y']
            txt = ET.SubElement(g, 'text', attrib={
                'x': str(x),
                'y': str(y),
                'dominant-baseline': 'middle',
                'text-anchor': 'middle'
            })
            txt.text = label

        return g

    def renderAsset(self, aid, ainfo):
        svg = ainfo['svg']
        svg.attrib['id'] = formatID(aid)
        return svg

    def render(self, output):
        root = ET.Element('svg', nsmap=self.NS, attrib={ 'version': '1.1' })

        defs = ET.SubElement(root, 'defs')
        for aid, ainfo in self.assets.items():
            defs.append(self.renderAsset(aid, ainfo))

        gNet = ET.SubElement(root, 'g')

        gNodes = ET.SubElement(gNet, 'g')
        for nid, ninfo in self.nodes.items():
            el = self.renderNode(nid, ninfo)
            if el:
                gNodes.append(el)

        gEdges = ET.SubElement(gNet, 'g')
        for edge in self.edges:
            gEdges.append(self.renderEdge(edge))

        padding = 10
        x1 = min(0, *self.bounds[0]) - padding
        y1 = min(0, *self.bounds[1]) - padding
        gNet.attrib['transform'] = f"translate({-x1} {-y1})"

        root.attrib['width'] = str(max(*self.bounds[0]) + padding - x1)
        root.attrib['height'] = str(max(*self.bounds[1]) + padding - y1)

        doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        ET.ElementTree(root).write(output, doctype=doctype, pretty_print=True)
