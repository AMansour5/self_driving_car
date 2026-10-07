import carla
from abc import ABC, abstractmethod
from queue import Empty, SimpleQueue
from carla_sim.exceptions.SimError import SimError

class CarlaSensor(ABC):
    """Shared mechanics of every CARLA sensor: spawn it attached to a parent actor,
    collect its measurements in a queue and hand them out already converted.
    Subclasses must provide BLUEPRINT and implement _convert(); forgetting either
    fails when the sensor is built, not in the middle of the tick loop."""

    USE_SENSOR_TICK = True  # lets CARLA skip rendering between samples

    @property
    @abstractmethod
    def BLUEPRINT(self):
        """CARLA blueprint id, for example "sensor.lidar.ray_cast". A plain class attribute is enough."""

    def __init__(self, name: str, sensor_cfg: dict):
        for key in ("topic", "frame", "pose"):
            if key not in sensor_cfg:
                raise SimError(f"Config of sensor '{name}' is missing '{key}'.")
        self.name = name
        self.topic = sensor_cfg["topic"]
        self.frame = sensor_cfg["frame"]
        # Poses are written in ROS convention: x forward, y left, z up, angles in degrees
        self.pose = {key: float(sensor_cfg["pose"].get(key, 0.0))
                     for key in ("x", "y", "z", "roll", "pitch", "yaw")}
        self.rate_hz = sensor_cfg.get("rate_hz")
        self.attributes = dict(sensor_cfg.get("attributes") or {})
        self.actor = None
        self._queue = SimpleQueue()

    def attach(self, world, parent):
        if world is None or parent is None:
            raise SimError(f"Cannot attach '{self.name}': it needs the world and the vehicle.")
        if self.actor is not None:
            raise SimError(f"Sensor '{self.name}' is already attached.")
        actor = None
        try:
            blueprint = world.get_blueprint_library().find(self.BLUEPRINT)
            for key, value in self._blueprintAttributes().items():
                blueprint.set_attribute(key, str(value))
            self._queue = SimpleQueue()
            actor = world.spawn_actor(blueprint, self.__carlaTransform(), attach_to=parent)
            actor.listen(self._queue.put)
        except (RuntimeError, IndexError) as e:
            if actor is not None:
                self.__destroyQuietly(actor)
            raise SimError(f"Failed to attach sensor '{self.name}' ({self.BLUEPRINT}) - {e}") from e
        self.actor = actor
        print(f"Successfully attached sensor '{self.name}'")

    def detach(self):
        """Never raises: it runs during teardown, where the other cleanup must still happen."""
        if self.actor is None:
            return
        actor, self.actor = self.actor, None
        self.__destroyQuietly(actor)
        print(f"Successfully detached sensor '{self.name}'")

    def poll(self):
        """Returns every sample received since the last call, already converted."""
        samples = []
        while True:
            try:
                raw = self._queue.get_nowait()
            except Empty:
                break
            samples.extend(self._convert(raw))
        return samples

    def _blueprintAttributes(self):
        attributes = dict(self.attributes)
        if self.USE_SENSOR_TICK and self.rate_hz:
            attributes["sensor_tick"] = round(1.0 / self.rate_hz, 4)
        return attributes

    @abstractmethod
    def _convert(self, raw):
        """Turn one raw CARLA measurement into a list of finished samples (possibly empty)."""

    def __carlaTransform(self):
        # ROS (right-handed) -> CARLA (left-handed): y, pitch and yaw change sign
        p = self.pose
        return carla.Transform(carla.Location(x=p["x"], y=-p["y"], z=p["z"]),
                               carla.Rotation(roll=p["roll"], pitch=-p["pitch"], yaw=-p["yaw"]))

    def __destroyQuietly(self, actor):
        try:
            actor.stop()
            actor.destroy()
        except RuntimeError as e:
            print(f"Warning: failed to destroy sensor '{self.name}' - {e}")