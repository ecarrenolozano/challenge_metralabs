
from pathlib import Path

import numpy as np

from metralabs import DataFolder


def test_data_folder():

    test_data_dir = Path(__file__).parent.joinpath('data')

    data = DataFolder(test_data_dir)

    meta = list(data)

    assert len(meta) == 6

    # grabbing a specific message to check if values are loaded correctly
    test_image_meta = next(m for m in meta if m.file_path().__str__() == 'cam2/ColorImage/1715584017539594000.PNG')

    # TODO: get real data
    assert np.isclose(test_image_meta.pose().trans_,  np.array([0,0,0])).all()

    assert np.isclose(test_image_meta.pose().rot_.as_euler('xyz'), np.array([0,0,0])).all()
