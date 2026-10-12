from zope.interface import implementer
from control.interfaces.ISmoothing import ISmoothing

@implementer(ISmoothing)
class LinearSmoothing:
    def __init__(self,  smoothing_factor: float = 0.1):
        self.smoothing_factor = smoothing_factor

    def smooth(self, current_value: float, target_value: float, tolerance: float = 0.01) -> float:
        """Apply linear smoothing to the current value towards the target value.

        :param current_value: The current value to be smoothed.
        :param target_value: The target value to approach.
        :param tolerance: The tolerance within which the smoothed value is considered equal to the target value.
        :return: The smoothed value.
        """
        smoothed_value = current_value + self.smoothing_factor * (target_value - current_value)
        if abs(smoothed_value - target_value) < tolerance:
            return target_value
        return smoothed_value
