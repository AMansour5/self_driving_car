from utils.Dispatcher import Dispatcher

def test_get_smoothing_strategy():
    strategy = Dispatcher.get_smoothing_strategy()
    print(strategy)
    assert strategy is not None

if __name__ == "__main__":
    test_get_smoothing_strategy()