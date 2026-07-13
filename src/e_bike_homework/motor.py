from src.e_bike_homework import battery_pack as bp
import logging

logger = logging.getLogger(__name__)

class Motor():
    def __init__(self, efficiency:float) -> None:
        if 0.0 <= efficiency <= 1.0:
            self.efficiency = efficiency
            logger.info(f"Motor initialized with efficiency {efficiency:.2f}")
        else:
            logger.error(f"Invalid efficiency value: {efficiency}")
            raise ValueError("Invalid efficiency. Must be between 0.0 and 1.0")

    def get_current_draw(self, power:float, voltage:float):
        if voltage <= 0.0:
            logger.error(f"Voltage must be greater than 0, got {voltage}")
            raise ValueError("Voltage must be greater than 0 to calculate current draw.")
            
        if power >= 0.0:
            return power / (voltage * self.efficiency)
        else:
            return (power * self.efficiency) / voltage