#!/bin/env python
'''
This is how your solution may look like. This is just an example.
You are not bound to any structure, as long as the output has the correct format.

This solution is also quite boring because it treats each image individually, not taking 
into account any 3D spatial information, point clouds, or overlap between images.

Run: 

python run.py path/to/input/dataset path/to/your/solution/output

Note that this will create path/to/your/solution/output if it does not exist already.

'''

import sys

from pathlib import Path

from metralabs import DataFolder, Solution, MessageType

from metralabs.top_secret import find_product_boxes

# Load a data folder from command line arguments.
data = DataFolder(Path(sys.argv[1]))

# Create an output channel for the solution from command line arguments
solution = Solution(Path(sys.argv[2]))

for meta in data:

    # You only need to label the color images.
    if meta.type() == MessageType.IMAGE_COLOR:

        boxes = find_product_boxes(meta, data)

        # Be sure to use the exact value returned by meta.file_path_str()
        solution.append(meta.file_path_str(), boxes)