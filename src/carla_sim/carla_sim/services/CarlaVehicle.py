import math
from carla_sim.exceptions.SimError import SimError
from carla_sim.data_types.VehicleBody import VehicleBody
from carla_sim.data_types.VehicleState import VehicleState

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
        # base_link is the rear axle: its distance from the actor's origin along the car's forward
        # axis, in meters (negative = behind the origin). It comes from vehicle.yaml.
        try:
            self.rear_axle_x = float(vehicle_cfg.get("rear_axle_x", 0.0))
        except (TypeError, ValueError) as e:
            raise SimError("'rear_axle_x' in the vehicle config must be a number of meters.") from e
        if "rear_axle_x" not in vehicle_cfg:
            print("Warning: 'rear_axle_x' is not set in the vehicle config, base_link will sit at the actor origin.")

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
        self.__printGeometry()
        print(f"Successfully spawned {self.blueprint} (wheel radius {self.wheel_radius:.3f} m, "
              f"rear axle {self.rear_axle_x:+.2f} m from the actor origin)")
        return self.actor

    def getState(self, stamp: float):
        """Pose of base_link (the rear axle) in the map frame, in ROS convention.
        The map frame is CARLA's world with y flipped. The axle offset assumes the car is level."""
        if self.actor is None:
            raise SimError("The vehicle is not spawned.")
        try:
            tf = self.actor.get_transform()
        except RuntimeError as e:
            raise SimError(f"Failed to read the vehicle pose - {e}") from e
        yaw = math.radians(tf.rotation.yaw)
        x = tf.location.x + math.cos(yaw) * self.rear_axle_x
        y = tf.location.y + math.sin(yaw) * self.rear_axle_x
        return VehicleState(stamp=stamp,
                            position=(x, -y, tf.location.z),
                            rpy=(math.radians(tf.rotation.roll), -math.radians(tf.rotation.pitch), -yaw))

    def getBody(self):
        """The car's bounding box, expressed relative to base_link in ROS convention."""
        if self.actor is None:
            raise SimError("The vehicle is not spawned.")
        box = self.actor.bounding_box  # reported relative to the actor origin, in CARLA convention
        return VehicleBody(center=(box.location.x - self.rear_axle_x, -box.location.y, box.location.z),
                           size=(2 * box.extent.x, 2 * box.extent.y, 2 * box.extent.z))

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

    def __printGeometry(self):
        # Raw values, printed once at spawn so rear_axle_x can be checked against the real car
        try:
            tf = self.actor.get_transform()
            box = self.actor.bounding_box
            wheels = self.actor.get_physics_control().wheels
            positions = ", ".join(f"{name}=({w.position.x:.0f}, {w.position.y:.0f}, {w.position.z:.0f})"
                                  for name, w in zip(("FL", "FR", "RL", "RR"), wheels))
            print(f"Vehicle geometry - actor ({tf.location.x:.2f}, {tf.location.y:.2f}, {tf.location.z:.2f}) "
                  f"yaw {tf.rotation.yaw:.1f}; box center ({box.location.x:.2f}, {box.location.y:.2f}, "
                  f"{box.location.z:.2f}) extent ({box.extent.x:.2f}, {box.extent.y:.2f}, {box.extent.z:.2f}); "
                  f"wheels in cm: {positions}")
        except (RuntimeError, AttributeError):
            print("Warning: vehicle geometry unavailable.")