from src.core import battery_pack as bp
from src.core import motor
from src.core import ebike_model
from src.utils import plotting_utils as plot
from src import config as cfg
import logging

logger = logging.getLogger(__name__)

class EBikeSimulator:
    """Simulator for an E-Bike. The simulator applies a power profile and records the voltage, current, speed, and distance profiles."""

    def __init__(self, motor: motor.Motor, battery: bp.BatteryPack, vehicle: ebike_model.VehicleModel) -> None:
          self.battery = battery
          self.motor = motor
          self.vehicle = vehicle
          self.currentValues = []
          self.voltageValues = []
          self.speedValues = [vehicle.v]
          self.distanceValues = [vehicle.s]
          self.socValues = [battery.soc]

    def simulate(self, power: list[float], duration: list[float], slopes: list[float] = None, speeds: list[float] = None, rhos: list[float] = None, temperatures: list[float] = None ) -> None:
        if len(power) != len(duration):
            logger.error("Power and duration profiles must have the same length.")
            raise ValueError("Power and duration profiles must have the same length.")
            
        if slopes is None:
            slopes = [0.0] * len(power)
        if speeds is None:
            speeds = [0.0] * len(power)
        if rhos is None:
            rhos = [cfg.PHYSICS.RHO_AIR_SEA_LEVEL] * len(power)
        if temperatures is None:
            temperatures = [20.0] * len(power)    

        logger.info("Starting simulation")

        act_voltage = self.battery.voltage()
        self.voltageValues.append(act_voltage)

        for i in range(len(power)):
            temp = temperatures[i]
            
            if duration[i] < 0:
                logger.error(f"Duration value at index {i} is negative: {duration[i]}")
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
            self.currentValues.append(act_current)
            self.voltageValues.append(act_voltage)
            self.speedValues.append(self.vehicle.v)
            self.distanceValues.append(self.vehicle.s)
            self.socValues.append(self.battery.soc)

        logger.info("Finished")
        


if __name__ == "__main__":
    pass