import carla
from utils.EnvParams import EnvParams
from carla_sim.exceptions.SimError import SimError

class CarlaApi():
    def __init__(self, world_cfg: dict):
        self.host = EnvParams().CARLA_HOST
        self.port = int(EnvParams().CARLA_PORT)
        self.town = world_cfg["world"].get("town", None)
        self.fixed_delta_seconds = world_cfg["world"].get("fixed_delta_seconds", None)
        self.client = None
        self.world = None
        self.original_settings = None

    def connect(self):
        try:
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(10.0)
            self.client_version = self.client.get_client_version()
            self.server_version = self.client.get_server_version()
            if self.client_version != self.server_version:
                print(f"Warning: Client version ({self.client_version}) and server version ({self.server_version}) do not match.")
            print(f"Successfully connected to Carla server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Carla server at {self.host}:{self.port} - {e}")

    def loadWorld(self):
        if self.client is None:
            print("Client is not connected.")
            return
        try:
            world = self.client.get_world()
            if self.town and not world.get_map().name.endswith(self.town):
                world = self.client.load_world(self.town)
            self.world = world
            self.original_settings = self.world.get_settings()
            self.__setSettings()
            print(f"Successfully loaded world: {self.world.get_map().name}")
        except Exception as e:
            print(f"Failed to load world - {e}")

    def disconnect(self):
        try:
            if self.world and self.original_settings:
                self.world.apply_settings(self.original_settings)
            self.client = None
            self.world = None
            self.original_settings = None
            print(f"Successfully disconnected from Carla server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to disconnect from Carla server - {e}")

    def __setSettings(self):
        if self.world is None:
            print("World is not loaded.")
            return
        try:
            settings = self.world.get_settings()
            if self.fixed_delta_seconds is not None:
                settings.fixed_delta_seconds = self.fixed_delta_seconds
            settings.synchronous_mode = True
            self.world.apply_settings(settings)
        except Exception as e:
            print(f"Failed to set world settings - {e}")

    def tick(self):
        if self.world is None:
            print("World is not loaded.")
            return
        try:
            self.world.tick()
        except Exception as e:
            print(f"Failed to tick the world - {e}")

    def getWorld(self):
        return self.world

    def getSimTime(self):
        """Simulation seconds since the world was loaded, as of the last tick."""
        if self.world is None:
            raise SimError("World is not loaded.")
        try:
            return self.world.get_snapshot().timestamp.elapsed_seconds
        except RuntimeError as e:
            raise SimError(f"Failed to read the simulation time - {e}") from e