import yaml as yaml
from lxml import etree as ET
from pathlib import Path

import logging
log = logging.getLogger(__name__)

from circuit_markup import common


def load_path(path, ignore=[]):
    files = []
    dirPath = Path(path)
    filePath = Path(f"{path}.svg")
    if dirPath.is_dir():
        log.debug(f"Importing from directory {dirPath}...")
        fps = dirPath.glob("*.svg")
        files.extend([(str(f)[:-4], str(f)) for f in fps])
    elif filePath.is_file():
        files.append((path, filePath))
    else:
        raise ValueError(f"Could not import {path} - it's neither a file nor a directory!")
    return files


def load_asset_tags(fid):
    yp = Path(str(fid) + ".yaml")
    if not yp.is_file():
        yp = Path(str(fid) + ".yml")
        if not yp.is_file():
            return None
    print(yp)

    tags = {}
    with open(yp) as f:
        tags = yaml.load(f)

    cleaned = {}
    for t, v in tags.items():
        if 'x' not in v:
            raise ValueError("Tag has no x coordinate!")
        if 'y' not in v:
            raise ValueError("Tag has no x coordinate!")
        cleaned[t] = common.Position(float(v['x']), float(v['y']))
    return cleaned


def load_asset(fid, fn):
    yp = Path(fid + ".yaml")
    if not yp.is_file():
        yp = Path(fid + ".yml")

    log.debug(f"Importing {fn} as {fid}...")
    svg = ET.parse(str(fn)).getroot()
    meta = {
        'width': float(svg.attrib['width']),
        'height': float(svg.attrib['height'])
    }
    meta['enter'] = common.Position(0, meta['height']/2)
    meta['exit'] = common.Position(meta['width'], meta['height']/2)
    return svg, meta
