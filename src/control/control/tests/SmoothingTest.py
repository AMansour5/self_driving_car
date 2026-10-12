from control.services.strategies.LinearSmoothing import LinearSmoothing
from control.services.strategies.ExponentialSmoothing import ExponentialSmoothing

class TestSmoothing:
    def __init__(self):
        self.current_value = 0
        self.target_value = 10
        self.linear_smoother = LinearSmoothing()
        self.exponential_smoother = ExponentialSmoothing()
        self.linear_smoothing_result = None
        self.exponential_smoothing_result = None

    def test_linear_smoothing(self):
        try:
            while self.current_value != self.target_value:
                self.linear_smoothing_result = self.linear_smoother.smooth(self.current_value, self.target_value)
                self.current_value = self.linear_smoothing_result
                print(f"Linear smoothing result: {self.linear_smoothing_result}")
        except Exception as e:
            print(f"An error occurred during linear smoothing: {e}")


    def test_exponential_smoothing(self):
        try:
            while self.current_value != self.target_value:
                self.exponential_smoothing_result = self.exponential_smoother.smooth(self.current_value, self.target_value)
                self.current_value = self.exponential_smoothing_result
                print(f"Exponential smoothing result: {self.exponential_smoothing_result}")
        except Exception as e:
            print(f"An error occurred during exponential smoothing: {e}")

if __name__ == "__main__":
    test = TestSmoothing()
    test.test_linear_smoothing()
    test.current_value = 0  # Reset current value before testing exponential smoothing
    test.test_exponential_smoothing()

