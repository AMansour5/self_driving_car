from zope.interface import Interface

class ISmoothing(Interface):
    
    def smooth(current_value: float, target_value: float, tolerance: float = 0.01) -> float:
        """Apply smoothing to the given data and return the smoothed value.

        :param current_value: The current value to be smoothed.
        :param target_value: The target value to approach.
        :param tolerance: The tolerance within which the smoothed value is considered equal to the target value.
        :return: The smoothed value.
        """