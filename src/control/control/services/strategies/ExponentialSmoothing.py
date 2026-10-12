from zope.interface import implementer
from control.interfaces.ISmoothing import ISmoothing

@implementer(ISmoothing)
class ExponentialSmoothing:
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha  # Smoothing factor, can be adjusted

    def smooth(self, current_value: float, target_value: float, tolerance: float = 0.01) -> float:
        """Apply exponential smoothing to the current value towards the target value.

        :param current_value: The current value to be smoothed.
        :param target_value: The target value to approach.
        :param tolerance: The tolerance within which the smoothed value is considered equal to the target value.
        :return: The smoothed value.
        """
        smoothed_value = self.alpha * target_value + (1 - self.alpha) * current_value
        if abs(smoothed_value - target_value) < tolerance:
            return target_value
        return smoothed_value