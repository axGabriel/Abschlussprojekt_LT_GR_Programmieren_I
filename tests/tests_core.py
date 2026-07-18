import unittest
from src.core.battery_pack import BatteryPack
from src.core.ebike_model import VehicleModel


class TestBatteryPack(unittest.TestCase):
    """Test cases for the BatteryPack class."""

    def test_invalid_capacity_raises_error(self):
        """Check if a ValueError is raised for negative or zero nominal capacity."""
        with self.assertRaises(ValueError):
            BatteryPack(capacity_nom_Ah=-5.0)
        
        with self.assertRaises(ValueError):
            BatteryPack(capacity_nom_Ah=0.0)

    def test_invalid_voltage_range_raises_error(self):
        """Check if a ValueError is raised when Vmin >= Vmax."""
        with self.assertRaises(ValueError):
            BatteryPack(capacity_nom_Ah=10.0, Vmin=42.0, Vmax=32.0)

    def test_battery_depletion_raises_runtime_error(self):
        """Check if a RuntimeError ('Akku leer') is raised when the SoC drops to 0 or below."""
        battery = BatteryPack(capacity_nom_Ah=1.0, initial_soc=0.1)  # 1 Ah battery pack at 10% initial SoC
        
        # Draw 10 Amperes for 3600 seconds -> battery must deplete and raise a RuntimeError!
        with self.assertRaises(RuntimeError):
            battery.apply_current(current=10.0, duration=3600.0)
        
        self.assertTrue(battery.is_empty())
        self.assertEqual(battery.soc, 0.0)


class TestVehicleModel(unittest.TestCase):
    """Test cases for the VehicleModel class."""

    def test_invalid_mass_raises_error(self):
        """Check if a ValueError is raised for negative or zero vehicle mass."""
        with self.assertRaises(ValueError):
            VehicleModel(mass=0.0)
        
        with self.assertRaises(ValueError):
            VehicleModel(mass=-20.0)

    def test_negative_duration_raises_error(self):
        """Check if a ValueError is raised when step() is called with a negative duration."""
        vehicle = VehicleModel(mass=80.0)
        with self.assertRaises(ValueError):
            vehicle.step(power=250.0, duration=-10.0)


if __name__ == '__main__':
    unittest.main()