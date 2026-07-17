from src.utils import example_utils as utils
import logging
import numpy as np

logger = logging.getLogger(__name__)
class BatteryPack:
    """
    Simple model of a battery pack as a single cell.
    The battery is modeled as an ideal voltage source (open circuit voltage) in series with an internal resistance.
    The open circuit voltage is a linear function of the state of charge (SoC).
    The SoC is updated based on the applied current and duration.
    """

    def __init__(
        self,
        capacity_nom_Ah: float,
        internal_resistance_mOhm: float = 80.0,
        initial_soc: float = 1.0,
        Vmin: float = 3.0,
        Vmax: float = 4.2,
    ):
        if capacity_nom_Ah <= 0:
            logger.error("Capacity must be greater than zero.")
            raise ValueError("Capacity must be greater than zero.")
        if Vmin >= Vmax:
            logger.error(f"Vmin ({Vmin}) must be less than Vmax ({Vmax}).")
            raise ValueError("Vmin must be less than Vmax.")
        if internal_resistance_mOhm < 0:
            logger.error("Internal resistance cannot be negative.")
            raise ValueError("Internal resistance cannot be negative.")

        self.capacity_nom_As = capacity_nom_Ah * 3600
        self.internal_resistance_mOhm = internal_resistance_mOhm
        self.initial_soc = initial_soc
        self.soc = utils.clamp(self.initial_soc, 0.0, 1.0) 
        self.Vmin = Vmin
        self.Vmax = Vmax

    def apply_current(self, current: float, duration: float) -> None:
        """Modify the SoC based on the applied current & duration"""
        #(I * dt / C_nom)
        delta_soc = (current * duration) / self.capacity_nom_As
        new_soc = self.soc - delta_soc
        
        if utils.is_less_equal_in_tol(new_soc, 0.0):
            self.soc = 0.0
            logger.warning("Akku leer")
            raise RuntimeError("Akku leer")
        elif utils.is_greater_equal_in_tol(new_soc, 1.0):
            self.soc = 1.0
            logger.info("Akku voll")
        else:
            self.soc = new_soc

    def is_empty(self) -> bool:
        """Returns true if battery is empty"""
        return utils.is_less_equal_in_tol(self.soc, 0.0)

    def is_full(self) -> bool:
        """Returns true if battery is full"""
        return utils.is_greater_equal_in_tol(self.soc, 1.0)

    def voltage(self, current: float = 0.0) -> float:
        """Return the current voltage of the battery at the SoC and the given current flow"""
        return self.Vmin + (self.Vmax - self.Vmin) * self.soc - (self.internal_resistance_mOhm / 1000.0) * current

    def __str__(self):
        return f"BatteryPack(SoC={self.soc * 100:.1f}%, V={self.voltage():.2f} V)"

class LiPoBatteryPack(BatteryPack):
    """Lithium polymer battery pack, inherits from BatteryPack class"""
    # characteristic curve from task description (page 20)
    _soc_table = [0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
    _ocv_table = [32.00, 35.87, 36.85, 37.56, 37.87, 38.28, 38.81, 39.05, 39.55, 40.27, 40.70, 41.16, 41.65, 42.00]
    
    def voltage(self, current: float = 0.0) -> float:
        """Return the current voltage of the battery"""
        ocv = np.interp(self.soc, self._soc_table, self._ocv_table)

        #calc voltage loss via internal res.

        return ocv - (self.internal_resistance_mOhm / 1000.0) * current

class NmcBatteryPack(BatteryPack):
    """Nickel mangan coblt battery pack, inherrits from BatteryPack class"""
    # charakteristic curve from task description
    _soc_table = [0.00, 0.04, 0.09, 0.13, 0.17, 0.21, 0.26, 0.30, 0.40, 0.52, 0.64, 0.76, 0.88, 1.00]
    _ocv_table = [32.00, 32.61, 33.17, 33.85, 34.24, 34.66, 35.39, 35.65, 36.65, 37.64, 38.91, 40.14, 41.08, 42.00]
    
    # interpolate voltage between table values
    def voltage(self, current: float = 0.0) -> float:
        """calculates the act voltage of the NMC Battery Pack"""
        ocv = np.interp(self.soc, self._soc_table, self._ocv_table)

        #calc voltage loss via internal res.

        return ocv - (self.internal_resistance_mOhm / 1000) * current

class ColdWeatherBattery(BatteryPack):
    def apply_current(self, current: float, duration: float) -> None:
        """Modify the SoC based on the applied current & duration"""
        #(I * dt / C_nom)
        modifier = 1.2 if current > 0.0 else 1.0
        delta_soc = ((current * duration) / self.capacity_nom_As) * modifier #Modifier for cold weather battery
        new_soc = self.soc - delta_soc
        
        if utils.is_less_equal_in_tol(new_soc, 0.0):
            self.soc = 0.0
            logger.warning("Akku leer")
            raise RuntimeError("Akku leer")
        elif utils.is_greater_equal_in_tol(new_soc, 1.0):
            self.soc = 1.0
            logger.info("Akku voll")
        else:
            self.soc = new_soc
