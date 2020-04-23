from antlr4 import *
from circuit_markup.antlr.CircuitMarkupLexer import CircuitMarkupLexer
from circuit_markup.antlr.CircuitMarkupParser import CircuitMarkupParser
from circuit_markup.antlr.CircuitMarkupVisitor import CircuitMarkupVisitor

from pathlib import Path

from lxml import etree as ET
import logging
from yaml import load
log = logging.getLogger(__name__)

from circuit_markup import asset, common

class EvalError(Exception):
    pass

class Evaluator(CircuitMarkupVisitor):
    def __init__(self):
        self.imported = {}
        self.nodes = {}
        self.exposed_values = {}
        self.edges = []

    def visitCoordinates(self, ctx):
        xs = ctx.NUMBER()
        return common.Position(*(float(x.getText()) for x in xs))

    def visitNodeAnchor(self, ctx):
        nid, attr = (x.getText() for x in ctx.ID())
        if nid not in self.nodes:
            raise EvalError(f"Node {nid} not defined (yet)")
        if attr not in self.nodes[nid]:
            raise EvalError(f"Node {nid} has no attribute {attr}")
        p = self.nodes[nid][attr]
        if not isinstance(p, common.Position):
            raise EvalError(f"{nid}.{attr} is not a position")
        return p

    def visitExpression(self, ctx):
        return self.visit(ctx.stringL())

    def visitAttributeAssign(self, ctx):
        res = (ctx.ID().getText(), self.visit(ctx.expression()))
        return res

    def visitAttributeAssigns(self, ctx):
        return dict(self.visit(c) for c in ctx.getChildren())

    def visitEdgeChainStatement(self, ctx):
        edges = self.visit(ctx.edgeChain())
        for (start, attrs, end) in edges:
            self.edges.append({
                'start': start,
                'end': end,
                **attrs
            })


    def visitEdge(self, ctx):
        if not ctx.attributeAssigns():
            return {}
        else:
            return self.visit(ctx.attributeAssigns())

    def visitEdgeChain(self, ctx):
        start = self.visit(ctx.position()[0])
        attrs = self.visit(ctx.edge())

        if not ctx.edgeChain():
            end = self.visit(ctx.position()[1])
            return [(start, attrs, end)]
        tail = self.visit(ctx.edgeChain())
        return [(start, attrs, tail[0][0]), *tail]

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
        files = asset.load_path(s)
        for fid, fn in files:
            if fid in self.imported:
                log.warn(f"Asset {s} already imported. Skipping...")
                continue

            tags = asset.load_asset_tags(fid)
            if not tags:
                log.debug(f"Asset {fid} has no tag file.")
                tags = {}
            else:
                log.debug(f"Loaded tags for asset {fid}")

            svg, meta = asset.load_asset(fid, fn)
            self.imported[fid] = {
                **meta,
                **tags,
                'svg': svg
            }

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
    print("Edges")
    for e in visitor.edges:
        print(e)
    return visitor.imported, visitor.nodes, visitor.edges

def evaluate_file(f):
    return _evaluate(FileStream(f))
