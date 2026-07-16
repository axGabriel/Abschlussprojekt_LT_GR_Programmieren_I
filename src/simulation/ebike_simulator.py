from Abschlussprojekt_LT_GR_Programmieren_I.src.core import battery_pack as bp
from Abschlussprojekt_LT_GR_Programmieren_I.src.core import motor
from Abschlussprojekt_LT_GR_Programmieren_I.src.core import ebike_model
from Abschlussprojekt_LT_GR_Programmieren_I.src.utils import plotting_utils as plot
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

    def simulate(self, power: list[float], duration: list[float], slopes: list[float] = None, speeds: list[float] = None, rhos: list[float] = None) -> None:
        if len(power) != len(duration):
            logger.error("Power and duration profiles must have the same length.")
            raise ValueError("Power and duration profiles must have the same length.")
            
        if slopes is None:
            slopes = [0.0] * len(power)
        if speeds is None:
            speeds = [0.0] * len(power)
        if rhos is None:
            rhos = [cfg.RHO_AIR] * len(power)
            
        logger.info("Starting simulation")

        act_voltage = self.battery.voltage()
        self.voltageValues.append(act_voltage)

        for i in range(len(power)):
            if duration[i] < 0:
                logger.error(f"Duration value at index {i} is negative: {duration[i]}")
                raise ValueError("Duration values cannot be negative.")

            if self.battery.is_empty():
                # Akku ist leer → kein Strom, keine Motorleistung
                act_current = 0.0
                self.vehicle.step(0.0, duration[i], slopes[i], speeds[i], rho=rhos[i])
            else:
                try:
                    act_current = self.motor.get_current_draw(power[i], act_voltage)
                    self.battery.apply_current(act_current, duration[i])
                    act_voltage = self.battery.voltage(act_current)
                    self.vehicle.step(power[i], duration[i], slopes[i], speeds[i], rho=rhos[i])
                except RuntimeError:
                    # Akku wurde in diesem Schritt leer
                    act_current = 0.0
                    act_voltage = self.battery.voltage(0.0)
                    logger.warning(f"Akku leer ab Segment {i}")

            self.currentValues.append(act_current)
            self.voltageValues.append(act_voltage)
            self.speedValues.append(self.vehicle.v)
            self.distanceValues.append(self.vehicle.s)
            self.socValues.append(self.battery.soc)

        logger.info("Finished")
        


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    power_profile_W = [115, 420, 150, -60, 38, 300, 0.0, 435, -75, 111]
    duration_s = [300.0, 240.0, 90.0, 150.0, 120.0, 300.0, 60.0, 30.0, 120.0, 180.0]

    #Normal battery pack
    obj_battery = bp.BatteryPack(capacity_nom_Ah=10, initial_soc=0.7, Vmin=32.0, Vmax=42.0)
    obj_motor = motor.Motor(0.5)
    obj_vehicle = ebike_model.VehicleModel(mass=100.0, initial_v=0.1, initial_s=0.0)

    sim_ebike = EBikeSimulator(obj_motor, obj_battery, obj_vehicle)
    sim_ebike.simulate(power_profile_W, duration_s)

    plot.plot_power_profile(power_profile_W, duration_s)
    plot.plot_voltage_and_current_profile(sim_ebike.voltageValues, sim_ebike.currentValues, duration_s)
    plot.plot_speed_and_distance_profile(sim_ebike.speedValues, sim_ebike.distanceValues, duration_s)

    print(input("Bitte enter drücken"))