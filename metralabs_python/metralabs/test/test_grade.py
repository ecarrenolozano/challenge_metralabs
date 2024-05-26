
from pathlib import Path

import numpy as np

from metralabs.grade import grade_boxes, intersection, area, associate_boxes, grade_solution_dir

def test_area():
    assert area((1, 1, 4, 4)) == 9
    assert area((0, 0, 0, 0)) == 0
    assert area((2, 3, 5, 7)) == 12

def test_intersection():
    assert intersection((1, 1, 4, 4), (2, 2, 5, 5)) == 4
    assert intersection((1, 1, 4, 4), (4, 4, 6, 6)) == 0
    assert intersection((1, 1, 4, 4), (0, 0, 2, 2)) == 1
    assert intersection( (2, 2, 4, 4),  (2, 2, 4, 4)) == area( (2, 2, 4, 4))

def test_associate_boxes_identical():
    reference = np.array([[224, 431, 600, 1080], [601, 433, 988, 1080], [959, 431, 1270, 945], [1256, 431, 1920, 861]])
    solution = reference
    iou_matrix, matches = associate_boxes(solution, reference)
    
    assert np.allclose(iou_matrix.diagonal(), np.array((1,1,1,1)))

    assert matches == [(0,0),(1,1),(2,2),(3,3)]

    assert grade_boxes(solution, reference) == 1.0

def test_wtf():

    solution = [[224, 431, 600, 1080], [601, 433, 988, 1080], [959, 431, 1270, 945], [1256, 431, 1920, 861]] 
    reference = [[224, 431, 600, 1080], [601, 433, 988, 1080], [959, 431, 1270, 945], [1256, 431, 1920, 861]]

    iou_matrix, matches = associate_boxes(solution, reference)

    assert grade_boxes(solution, reference) == 1.0

def test_associate_boxes_shuffle():
    reference = np.array([(1, 1, 3, 3), (2, 2, 4, 4), (3, 3, 5, 5)])

    idx = [2,0,1]

    solution = reference[idx]
    iou_matrix, matches = associate_boxes(solution, reference)
    
    assert matches == [(0,2),(1,0),(2,1)]


def test_grade_boxes_noisy():
    reference = np.array( [(1, 1, 3, 3), (2, 2, 4, 4), (3, 3, 5, 5)])
    reference_noisy = np.array([(1.1, 1.3, 2.8, 3), (1.8, 1.8, 4.2, 3.8), (3.1, 4, 6, 5)])

    idx = [2,0,1]

    solution = reference_noisy[idx]
    iou_matrix, matches = associate_boxes(solution, reference)
    
    assert matches == [(0,2),(1,0),(2,1)]

    score = grade_boxes(solution, reference)

    assert score < 1.0
    assert score > 0.0


def test_grade_boxes_shuffle():

    reference = np.array([(1, 1, 3, 3), (2, 2, 4, 4), (3, 3, 5, 5)])

    idx = [2,0,1]

    solution = reference[idx]

    grade = grade_boxes(solution, reference)

    assert grade == 1.0


def test_grade_boxes_missing():

    reference = np.array([(1, 1, 3, 3), (2, 2, 4, 4), (3, 3, 5, 5), (30, 30, 50, 50)])

    idx = [2,0,1]

    solution = reference[idx]
    iou_matrix, matches = associate_boxes(solution, reference)
    
    # find the match of the last solution
    last_match = next(match for match in matches if match[1] == 3)

    assert iou_matrix[last_match] == 0

    grade = grade_boxes(solution, reference)

    # the IOU of the last reference box is zero
    assert grade == 0.75

def test_grade_solution_dir():

    solution_dir = Path(__file__).parent.joinpath('data/grade/solution')

    reference_dir = Path(__file__).parent.joinpath('data/grade/reference')

    score, nsol, nref = grade_solution_dir(reference_dir, reference_dir)

    assert nref == nsol
    assert abs(score - 1.0) < 1e-6

    score, nsol, nref = grade_solution_dir(solution_dir, reference_dir)

    # solution contains two fewer labels 
    assert nref == nsol + 2

    # labels are in different order and two are missing but 
    # the rest is the same so the score is nsol/nref
    assert abs(score - nsol/nref) < 1e-6

    # submitting more labels in solution than there are in reference 
    # results in drop in the score
    score, _, _ = grade_solution_dir(reference_dir, solution_dir)
    assert score < 1.0

