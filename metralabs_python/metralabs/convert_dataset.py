#!/bin/env python

import xml.etree.ElementTree as ET

from typing import List

import json

import sys

from pathlib import Path

from metralabs.solution import Box

def get_boxes(file_path : str) -> List[Box]:
    ''' Get boxes from pascal voc file '''
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    boxes = []
    for obj in root.findall('object'):
        bndbox = obj.find('bndbox')
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        boxes.append([xmin, ymin, xmax, ymax])
    
    return boxes


files = Path(sys.argv[1]).glob('**/*.xml')

for file in files:
    boxes = get_boxes(file.__str__())
    
    meta = json.load(open(file.__str__().replace('.xml', '_meta.json'), 'rb'))

    filename = meta['File']

    json_dest = file.__str__().replace('.xml', '_label.json')

    print(file.__str__(), "-->", json_dest)

    json.dump(dict(file=filename, boxes=boxes), open(json_dest, 'w'))

