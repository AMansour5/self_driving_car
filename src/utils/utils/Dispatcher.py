from utils.Configurator import Configurator

class Dispatcher:

    @staticmethod
    def get_smoothing_strategy() -> object:
        """Dynamically fetch and instantiate the smoothing strategy based on configuration.
        Returns:
            object: An instance of the selected smoothing strategy."""
        smoothing_dict = Configurator().fetchData(Configurator.SMOOTHING_STRATEGY)
        smoothing_strat = smoothing_dict["smoothing_strategy"]
        if smoothing_strat == "LinearSmoothing":
            from control.services.strategies.LinearSmoothing import LinearSmoothing
            factor = smoothing_dict["linear_factor"]
            return LinearSmoothing(factor)
        elif smoothing_strat == "ExponentialSmoothing":
            from control.services.strategies.ExponentialSmoothing import ExponentialSmoothing
            factor = smoothing_dict["exponential_factor"]
            return ExponentialSmoothing(factor)
        else:
            raise ValueError(f"Unknown smoothing strategy: {smoothing_strat}")