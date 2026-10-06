from carla_sim.services.CarlaApi import CarlaApi
from utils.Configurator import Configurator

class TestCarlaApi:
    def __init__(self):
        self.configurator = Configurator("carla_sim")
        self.carla_api = CarlaApi(self.configurator.fetchData(Configurator.CARLA_WORLD))

    def test_connection(self):
        try:
            self.carla_api.connect()
        except Exception as e:
            print(f"Connection failed: {e}")

    def test_load_world(self):
        try:
            self.carla_api.loadWorld()
        except Exception as e:
            print(f"Load world failed: {e}")

    def test_disconnect(self):
        try:
            self.carla_api.disconnect()
        except Exception as e:
            print(f"Disconnect failed: {e}")

if __name__ == "__main__":
    test_api = TestCarlaApi()
    test_api.test_connection()
    test_api.test_load_world()
    test_api.test_disconnect()