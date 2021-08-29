import pytest
from ESP_filestructure.functions import transform_bytearray


@pytest.mark.parametrize("input_array, output_array",
                         [
                              (bytearray([0, 0, 0]), bytearray([255, 128, 64])),
                              (bytearray([255, 128, 64]), bytearray([0, 0, 0])),
                              (bytearray([233, 101, 53]), bytearray([233, 101, 53])),
                              (bytearray([255, 0, 111]), bytearray([17, 238, 111])),
                         ])
def test_transform_bytearray(input_array, output_array):
    dim_return = transform_bytearray(input_array, output_array)
    for item in dim_return:
        pass
    assert item == output_array
