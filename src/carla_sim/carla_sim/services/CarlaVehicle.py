from carla_sim.exceptions.SimError import SimError

class CarlaVehicle():
    def __init__(self, car_cfg: dict):
        # Configurator.fetchData returns None when the file can't be read
        if not car_cfg or "vehicle" not in car_cfg or "blueprint" not in car_cfg["vehicle"]:
            raise SimError("Car config must contain a 'vehicle' section with a 'blueprint'.")
        vehicle_cfg = car_cfg["vehicle"]
        self.blueprint = vehicle_cfg["blueprint"]
        self.spawn_index = vehicle_cfg.get("spawn_index", 0)
        self.actor = None
        self.wheel_radius = 0.35  # meters, replaced by the car's real value after spawning

    def spawn(self, world):
        if self.actor is not None:
            raise SimError("The vehicle is already spawned.")
        try:
            blueprint = world.get_blueprint_library().find(self.blueprint)
            blueprint.set_attribute("role_name", "hero")
            spawn_points = world.get_map().get_spawn_points()
            spawn_point = spawn_points[self.spawn_index % len(spawn_points)]
            self.actor = world.spawn_actor(blueprint, spawn_point)
        except (RuntimeError, IndexError) as e:
            raise SimError(f"Failed to spawn '{self.blueprint}' - {e}") from e
        self.__readWheelRadius()
        print(f"Successfully spawned {self.blueprint} (wheel radius {self.wheel_radius:.3f} m)")
        return self.actor

    def destroy(self):
        if self.actor is None:
            return
        actor, self.actor = self.actor, None
        try:
            actor.destroy()
            print(f"Successfully destroyed {self.blueprint}")
        except RuntimeError as e:
            raise SimError(f"Failed to destroy the vehicle - {e}") from e

    def __readWheelRadius(self):
        try:
            # wheels[2] is the rear-left wheel, radius is reported in cm
            self.wheel_radius = self.actor.get_physics_control().wheels[2].radius / 100.0
        except (RuntimeError, IndexError, AttributeError):
            print(f"Warning: wheel radius unavailable, assuming {self.wheel_radius} m.")