
import json

from typing import List, Tuple

from pathlib import Path

import numpy as np

from munkres import Munkres

from metralabs.solution import Box

# Box = (x_1, y_1, x_2, y_2)

def area(b : Box):

    return abs(b[0] - b[2]) * abs(b[1] - b[3])

def intersection(a: Box, b: Box) -> float:
    x_left = max(a[0], b[0])
    y_top = max(a[1], b[1])
    x_right = min(a[2], b[2])
    y_bottom = min(a[3], b[3])
    
    if x_right < x_left or y_bottom < y_top:
        return 0.0  # No overlap

    return area((x_left, y_top, x_right, y_bottom))

def associate_boxes(solution : List[Box], reference: List[Box]):
    '''
    Associates each box in the solution with a box in the reference.
    Returns tuple: (IoU matrix, indices for matches).
    The indices refer to the IoU matrix. Indices smaller than the length of 
    the respective list correspond to elements in the list. Larger indices correspond to "no match". The value of the IoU matrix at these points is always zero.
    '''

    n = max(len(solution), len(reference))

    iou = np.zeros((n, n))

    for i,sol in enumerate(solution):
        for j,ref in enumerate(reference):

            int_area = intersection(sol, ref)

            union_area = area(ref) + area(sol) - int_area
            iou[i,j] = int_area/union_area

    return iou, Munkres().compute(np.zeros_like(iou) - iou)


def grade_boxes(solution : List[Box], reference: List[Box]) -> float:
    '''
    Grades the solution for one set of boxes within [0,1].
    '''

    if len(reference) == 0 or len(solution) == 0:
        return 0

    iou, indices = associate_boxes(solution, reference)

    score = 0

    for i,j in indices:
        score += iou[i,j]

    return score/len(indices)

def grade_solution(sol_labels, ref_labels) -> Tuple[float, int, int]:

    sol_labels = list(sol_labels)

    score = 0
    # total number of boxes in reference
    ref_count = 0
    # total number of boxes in solution
    sol_count = 0

    for ref in ref_labels:

        sol = next((label for label in sol_labels if label['file'] == ref['file']), None)
        
        if sol == None:
            raise Exception('Missing solution label for file ' + ref['file'])
        
        sol_labels.remove(sol)

        sol_score = grade_boxes(sol['boxes'], ref['boxes'])

        score += sol_score*len(ref['boxes'])

        ref_count += len(ref['boxes'])
        sol_count += len(sol['boxes'])

    
    return score / ref_count, sol_count, ref_count

    
def grade_solution_dir(solution_dir : Path, reference_dir : Path):

    ref_labels = (json.load(open(label_path, 'rb')) for label_path in reference_dir.glob('**/*_label.json') )
    sol_labels = (json.load(open(label_path, 'rb')) for label_path in solution_dir.glob('**/*_label.json') )
    
    return grade_solution(sol_labels, ref_labels)


if __name__ == '__main__':

    import sys

    score, sol_count, ref_count = grade_solution_dir(Path(sys.argv[1]), Path(sys.argv[2]))

    print("Labels in solution: ", sol_count)
    print("Labels in reference: ", ref_count)

    print("Your score: ", score * 42.0, "/ 42")
