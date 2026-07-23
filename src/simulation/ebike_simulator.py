from src.core import battery_pack as bp
from src.core import motor
from src.core import ebike_model
from src import config as cfg
import logging

logger = logging.getLogger(__name__)

class EBikeSimulator:
    """Simulator for an E-Bike. Applies a power profile and records voltage, current, speed, and distance profiles."""

    def __init__(self, motor: motor.Motor, battery: bp.BatteryPack, vehicle: ebike_model.VehicleModel) -> None:
        self.battery = battery
        self.motor = motor
        self.vehicle = vehicle
        
        # PEP 8: snake_case variables instead of camelCase
        self.current_values = []
        self.voltage_values = []
        self.speed_values = [vehicle.v]
        self.distance_values = [vehicle.s]
        self.soc_values = [battery.soc]

    def simulate(
        self, 
        power: list[float], 
        duration: list[float], 
        slopes: list[float] = None, 
        speeds: list[float] = None, 
        rhos: list[float] = None, 
        temperatures: list[float] = None
    ) -> None:
        """Runs the simulation segment by segment. Verifies that all provided lists have the same length to prevent IndexErrors."""
        
        n_segments = len(power)
        
        # 1. Safety Checks (IndexError Prevention)
        if len(duration) != n_segments:
            raise ValueError("Power and duration profiles must have the same length.")
        
        if slopes is None:
            slopes = [0.0] * n_segments
        elif len(slopes) != n_segments:
            raise ValueError("Slopes profile must match power profile length.")
            
        if speeds is None:
            speeds = [0.0] * n_segments
        elif len(speeds) != n_segments:
            raise ValueError("Speeds profile must match power profile length.")
            
        if rhos is None:
            rhos = [cfg.PHYSICS.RHO_AIR_SEA_LEVEL] * n_segments
        elif len(rhos) != n_segments:
            raise ValueError("Rhos profile must match power profile length.")
            
        if temperatures is None:
            temperatures = [20.0] * n_segments    
        elif len(temperatures) != n_segments:
            raise ValueError("Temperatures profile must match power profile length.")

        logger.info("Starte Simulation...")

        act_voltage = self.battery.voltage()
        self.voltage_values.append(act_voltage)

        for i in range(n_segments):
            temp = temperatures[i]
            
            if duration[i] < 0:
                logger.error(f"Dauer an Index {i} ist negativ: {duration[i]}")
                raise ValueError("Duration values cannot be negative.")
                
            if self.battery.is_empty():
                act_current = 0.0
                self.vehicle.step(0.0, duration[i], slopes[i], speeds[i], rho=rhos[i])
            else:
                try:
                    act_current = self.motor.get_current_draw(power[i], act_voltage)
                    self.battery.apply_current(act_current, duration[i], temperature_celsius=temp)
                    act_voltage = self.battery.voltage(act_current, temperature_celsius=temp)
                    self.vehicle.step(power[i], duration[i], slopes[i], speeds[i], rho=rhos[i])
                except RuntimeError:
                    act_current = 0.0
                    act_voltage = self.battery.voltage(0.0, temperature_celsius=temp)
                    logger.warning(f"Akku leer ab Segment {i}")
                    
            self.current_values.append(act_current)
            self.voltage_values.append(act_voltage)
            self.speed_values.append(self.vehicle.v)
            self.distance_values.append(self.vehicle.s)
            self.soc_values.append(self.battery.soc)

        logger.info("Simulation beendet.")