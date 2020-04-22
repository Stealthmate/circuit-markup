import logging
logging.basicConfig(level=logging.DEBUG, format="[%(name)s][%(levelname)s]: %(message)s")

import sys
from circuit_markup.parse import evaluate_file

r = evaluate_file(sys.argv[1])
print(r)
