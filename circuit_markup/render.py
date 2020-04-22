from lxml import etree as ET
from lxml.etree import QName
import numpy as np

def formatID(_id):
    return _id.replace("/", "--")

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
            'stroke': 'black'
        })

    def renderEdge(self, edge):
        start = np.array(edge['start'])
        end = np.array(edge['end'])
        attr = edge
        if 'shape' not in attr:
            return self.renderLineEdge(start, end, attr)

        aid = attr['shape']
        asset = self.assets[aid]
        dim = np.array([
            asset['width'],
            asset['height']
        ])

        g = ET.Element('g')

        d = end - start
        midpoint = start + d/2
        angle = np.arctan2(d[1], d[0])
        M = np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle),  np.cos(angle)]
        ])

        edge_offset = M @ [
            (np.linalg.norm(d) - dim[0]) / 2,
            0
        ]
        enter_point = start + edge_offset
        g.append(self.renderLineEdge(start, enter_point, {}))
        exit_point = end - edge_offset
        g.append(self.renderLineEdge(exit_point, end, {}))

        comp = ET.SubElement(g, 'use')
        comp.attrib[QName(self.NS['xlink'], 'href')] = '#' + formatID(aid)
        pos = midpoint - dim/2
        print(pos)
        comp.attrib['x'] = str(pos[0])
        comp.attrib['y'] = str(pos[1])
        comp.attrib['transform'] = f'rotate({180 * angle / np.pi} {midpoint[0]} {midpoint[1]})'

        bounds = np.array([
            [-dim[0],  dim[1]],
            [-dim[0], -dim[1]],
            [ dim[0],  dim[1]],
            [ dim[0], -dim[1]]
        ]).T / 2
        r = midpoint + (M @ bounds).T
        self.updateBounds(r[0], r[1])

        return g

    def renderNode(self, nid, ninfo):
        if 'shape' not in ninfo:
            return
        sid = formatID(ninfo['shape'])
        el = ET.Element('use', attrib={
            QName(self.NS['xlink'], 'href'): f'#{sid}',
            'x': str(ninfo['x']),
            'y': str(ninfo['y'])
        })

        return el

    def renderAsset(self, aid, ainfo):
        svg = ainfo['svg']
        svg.attrib['id'] = formatID(aid)
        return svg

    def render(self, output):
        root = ET.Element('svg', nsmap=self.NS, attrib={ 'version': '1.1' })
        # ET.SubElement(root, 'rect', attrib={
        #     'x': '0',
        #     'y': '0',
        #     'width': '300',
        #     'height': '200',
        #     'fill': 'red'
        # })

        defs = ET.SubElement(root, 'defs')
        for aid, ainfo in self.assets.items():
            defs.append(self.renderAsset(aid, ainfo))

        gNet = ET.SubElement(root, 'g')

        gNodes = ET.SubElement(gNet, 'g')
        for nid, ninfo in self.nodes.items():
            gNodes.append(self.renderNode(nid, ninfo))

        gEdges = ET.SubElement(gNet, 'g')
        for edge in self.edges:
            gEdges.append(self.renderEdge(edge))

        padding = 10
        x1 = min(0, *self.bounds[0]) - padding
        y1 = min(0, *self.bounds[1]) - padding
        gNet.attrib['transform'] = f"translate({-x1} {-y1})"

        doctype = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'
        ET.ElementTree(root).write(output, doctype=doctype, pretty_print=True)
