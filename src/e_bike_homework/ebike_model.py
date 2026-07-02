import logging

logger = logging.getLogger(__name__)

class VehicleModel:
    def __init__(self, mass: float = 100.0, initial_v: float = 0.1, initial_s: float = 0.0) -> None:
        if mass <= 0:
            logger.error(f"Invalid mass: {mass}")
            raise ValueError("Mass must be strictly positive.")
        if initial_v <= 0.0:
            logger.warning("Initial velocity should be greater than 0; setting to 0.1.")
            initial_v = 0.1
        self.mass = mass
        self.v = initial_v
        self.s = initial_s
        logger.info(f"VehicleModel initialized with mass {self.mass}kg, initial_v {self.v}m/s")

    def step(self, power: float, duration: float) -> None:
        if duration < 0:
            logger.error(f"Duration cannot be negative, got {duration}")
            raise ValueError("Duration cannot be negative.")
        v_eff = max(0.1, self.v)
        a = power / (self.mass * v_eff)
        self.v = self.v + a * duration
        self.s = self.s + self.v * duration