from functions import transform_bytearray


class WakeUp:

    def __init__(self, color_array: bytearray, goal_array: bytearray):
        self.color_array = color_array
        self.goal_array = goal_array
        self.iterator = transform_bytearray(color_array=color_array, goal_array=goal_array, number_of_steps=200)