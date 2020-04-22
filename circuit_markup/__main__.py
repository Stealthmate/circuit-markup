import logging
logging.basicConfig(level=logging.DEBUG, format="[%(name)s][%(levelname)s]: %(message)s")

import sys
from circuit_markup.parse import evaluate_file
from circuit_markup.render import render

assets, nodes, edges = evaluate_file(sys.argv[1])
render(assets, nodes, edges, 'output.svg')
