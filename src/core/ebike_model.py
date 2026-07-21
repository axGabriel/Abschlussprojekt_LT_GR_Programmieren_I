import logging
import math
from src import config as cfg

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

    def step(self, power: float, duration: float, slope: float = 0.0, v_gps: float = 0.0, cw_A: float = 0.5625, rho: float = cfg.PHYSICS.RHO_AIR_SEA_LEVEL, c_r: float = cfg.SETTINGS.c_r) -> None:
        if duration < 0:
            logger.error(f"Duration cannot be negative, got {duration}")
            raise ValueError("Duration cannot be negative.")
        
        F_slope = self.mass * cfg.PHYSICS.GRAVITY_EARTH * math.sin(slope)
        F_drag = 0.5 * rho * cw_A * (v_gps ** 2)
        F_rolling = c_r * self.mass * cfg.PHYSICS.GRAVITY_EARTH * math.cos(slope)
        
        # motor force based on actual vehicle speed
        v_eff = max(0.1, self.v)
        F_motor = power / v_eff
        
        F_net = F_motor - F_slope - F_drag - F_rolling
        a = F_net / self.mass
        
        self.v = max(0.0, self.v + a * duration)
        self.s = self.s + self.v * duration
