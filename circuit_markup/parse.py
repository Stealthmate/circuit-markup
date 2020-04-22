from antlr4 import *
from circuit_markup.antlr.CircuitMarkupLexer import CircuitMarkupLexer
from circuit_markup.antlr.CircuitMarkupParser import CircuitMarkupParser
from circuit_markup.antlr.CircuitMarkupVisitor import CircuitMarkupVisitor

from pathlib import Path

import xml.etree.ElementTree as ET
import logging
from collections import namedtuple
from yaml import load

log = logging.getLogger(__name__)

class EvalError(Exception):
    pass

class TagError(Exception):
    pass

Position = namedtuple("Position", ["x", "y"])

def clean_tags(tags):
    cleaned = {}
    for t, v in tags.items():
        if 'x' not in v:
            raise TagError("Tag has no x coordinate!")
        if 'y' not in v:
            raise TagError("Tag has no x coordinate!")
        try:
            cleaned[t] = Position(float(v['x']), float(v['y']))
        except ValueError as e:
            raise TagError(e)
    return cleaned


class Evaluator(CircuitMarkupVisitor):
    def __init__(self):
        self.imported = {}
        self.nodes = {}
        self.exposed_values = {}

    def visitCoordinates(self, ctx):
        xs = ctx.NUMBER()
        return Position(*(float(x.getText()) for x in xs))

    def visitNodeAnchor(self, ctx):
        nid, attr = (x.getText() for x in ctx.ID())
        if nid not in self.nodes:
            raise EvalError(f"Node {nid} not defined (yet)")
        if attr not in self.nodes[nid]:
            raise EvalError(f"Node {nid} has no attribute {attr}")
        p = self.nodes[nid][attr]
        if not isinstance(p, Position):
            raise EvalError(f"{nid}.{attr} is not a position")
        return p

    def visitExpression(self, ctx):
        return self.visit(ctx.stringL())

    def visitAttributeAssign(self, ctx):
        res = (ctx.ID().getText(), self.visit(ctx.expression()))
        return res

    def visitAttributeAssigns(self, ctx):
        return dict(self.visit(c) for c in ctx.getChildren())

    def visitNodePlaceStatement(self, ctx):
        nid = ctx.ID().getText()
        if nid in self.nodes:
            log.warn(f"Node {nid} has already been defined and will be skipped")
            return
        pos = self.visit(ctx.position())
        attrs = self.visit(ctx.attributeAssigns())
        if 'shape' in attrs:
            k = attrs['shape']
            if k not in self.imported.keys():
                raise ValueError(f"Shape {k} not imported!")

        self.nodes[nid] = {
            **attrs,
            'x': pos[0],
            'y': pos[1],
            'center': pos
        }

    def visitUseStatement(self, ctx):
        s = self.visit(ctx.stringL())
        files = []
        dirPath = Path(s)
        filePath = Path(f"{s}.svg")
        if dirPath.is_dir():
            log.debug(f"Importing from directory {dirPath}...")
            fps = dirPath.glob("*.svg")
            files.extend([(str(f)[:-4], str(f)) for f in fps])
            pass
        elif filePath.is_file():
            files.append((s, filePath))
        else:
            raise ValueError(f"Could not import {s} - it's neither a file nor a directory!")

        for fid, fp in files:
            if fid in self.imported:
                log.warn(f"Asset {s} already imported. Skipping...")
            else:
                yp = Path(fid + ".yaml")
                if not yp.is_file():
                    yp = Path(fid + ".yml")

                log.debug(f"Importing {fp} as {fid}...")
                self.imported[fid] = {'svg': None, 'tags': {}}
                self.imported[fid]['svg'] = ET.parse(fp).getroot()
                self.imported[fid]['svg'].attrib['id'] = s

                if not yp.is_file():
                    log.debug(f"Asset {fid} has no tag file.")
                else:
                    log.debug(f"Asset {fid} has tag file {yp}")
                    tags = {}
                    with open(yp) as f:
                        tags = clean_tags(load(f))
                    self.exposed_values[fid] = tags


    def visitStringL(self, ctx):
        return ctx.QUOTED_STRING().getText()[1:-1]

def _evaluate(prog):
    lexer = CircuitMarkupLexer(prog)
    stream = CommonTokenStream(lexer)
    parser = CircuitMarkupParser(stream)
    tree = parser.program()
    visitor = Evaluator()
    visitor.visit(tree)

    print("Imported")
    for k in visitor.imported.keys():
        print("   ", k)
    print("Placed")
    for n in visitor.nodes.keys():
        print("   ", n, visitor.nodes[n]['x'], visitor.nodes[n]['y'])
    print("Exposed")
    for e, v in visitor.exposed_values.items():
        print("   ", e, ":", v)

def evaluate_file(f):
    return _evaluate(FileStream(f))
