from utils.Configurator import Configurator

class TestConfigurator:
    def __init__(self):
        self.carla_configurator = Configurator("carla_sim")
        self.general_configurator = Configurator()

    def test_fetch_carla_world_config(self):
        carla_world_config = self.carla_configurator.fetchData(Configurator.CARLA_WORLD)
        print(carla_world_config) 

    def test_fetch_general_config(self):
        general_config = self.general_configurator.fetchData(Configurator.BUTTONS)
        print(general_config)

if __name__ == "__main__":
    test_api = TestConfigurator()
    test_api.test_fetch_carla_world_config()
    test_api.test_fetch_general_config()