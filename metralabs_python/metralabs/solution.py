
import json

from typing import List, Tuple

from pathlib import Path


# x_min,y_min,x_max,y_max
Box = Tuple[int,int,int,int]


def labels_to_dict(file : str, boxes : List[Box]):
    '''
    Create a dict from a list of boxes which can be stored as a .json file.
    '''
    return dict(file=file, boxes=list(boxes))

class Solution:
    '''
    This class helps you in writing your solution to disk in the correct format.
    '''
    def __init__(self, path : Path):

        self.path_ = path.absolute()

    def resolve(self, path):

        return self.path_.joinpath(path)

    def append(self, file : str, boxes : List[Box]):
        
        label_path = self.resolve(file).absolute().with_suffix('').__str__() + '_sol_label.json'
        
        Path(label_path).parent.mkdir(parents=True, exist_ok=True)

        json.dump(labels_to_dict(file, boxes), open(label_path, 'w'))
