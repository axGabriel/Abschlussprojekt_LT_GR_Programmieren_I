import unittest
from src.core.battery_pack import BatteryPack
from src.core.ebike_model import VehicleModel
from src.core.battery_pack import LiPoBatteryPack, NmcBatteryPack
from src.utils.example_utils import moving_average
from src.core.motor import Motor
from src.gps.calculator import TrackCalculator
from src.gps.gps_classes import GpsTrack

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
         BatteryPack(capacity_nom_Ah=10.0, v_min=42.0, v_max=32.0)

    def test_battery_depletion_raises_runtime_error(self):
        """Check if a RuntimeError ('Akku leer') is raised when the SoC drops to 0 or below."""
        battery = BatteryPack(capacity_nom_Ah=1.0, initial_soc=0.1)  # 1 Ah battery pack at 10% initial SoC
        
        # Draw 10 Amperes for 3600 seconds -> battery must deplete and raise a RuntimeError!
        with self.assertRaises(RuntimeError):
            battery.apply_current(current=10.0, duration=3600.0)
        
        self.assertTrue(battery.is_empty())
        self.assertEqual(battery.soc, 0.0)

    def test_nmc_cold_temperature_discharges_faster(self):
        """Check if drawing current from NMC battery at 0°C consumes more SoC than at 20°C."""
        nmc_warm = NmcBatteryPack(capacity_nom_Ah=10.0, initial_soc=1.0)
        nmc_cold = NmcBatteryPack(capacity_nom_Ah=10.0, initial_soc=1.0)
        
        nmc_warm.apply_current(current=5.0, duration=600.0, temperature_celsius=20.0)
        nmc_cold.apply_current(current=5.0, duration=600.0, temperature_celsius=0.0)
        
        self.assertLess(nmc_cold.soc, nmc_warm.soc)



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



class TestBatteryTemperature(unittest.TestCase):
    """Tests for temperature-dependent battery behavior."""
    def test_cold_temperature_increases_voltage_drop(self):
        """Check if voltage under current draw is lower at 0°C than at 20°C due to higher internal resistance."""
        lipo = LiPoBatteryPack(capacity_nom_Ah=10.0, internal_resistance_mOhm=80.0)
        
        v_warm = lipo.voltage(current=10.0, temperature_celsius=20.0)
        v_cold = lipo.voltage(current=10.0, temperature_celsius=0.0)
        
        self.assertLess(v_cold, v_warm)
    def test_cold_temperature_discharges_faster(self):
        """Check if drawing current at 0°C consumes more SoC than at 20°C."""
        lipo_warm = LiPoBatteryPack(capacity_nom_Ah=10.0, initial_soc=1.0)
        lipo_cold = LiPoBatteryPack(capacity_nom_Ah=10.0, initial_soc=1.0)
        lipo_warm.apply_current(current=5.0, duration=600.0, temperature_celsius=20.0)
        lipo_cold.apply_current(current=5.0, duration=600.0, temperature_celsius=0.0)
        self.assertLess(lipo_cold.soc, lipo_warm.soc)

class TestUtils(unittest.TestCase):
    """Tests for utility functions."""
    def test_moving_average_constant_values(self):
        """Check if moving average of a constant list returns the same values."""
        data = [10.0, 10.0, 10.0, 10.0]
        result = moving_average(data, window_size=3)
        self.assertEqual(result, [10.0, 10.0, 10.0, 10.0])
    def test_moving_average_smoothing(self):
        """Check if peak values are smoothed correctly."""
        data = [0.0, 10.0, 0.0]
        result = moving_average(data, window_size=2)
        # i=0: [0.0] -> avg 0.0
        # i=1: [0.0, 10.0] -> avg 5.0
        # i=2: [10.0, 0.0] -> avg 5.0
        self.assertEqual(result, [0.0, 5.0, 5.0])

class TestMotor(unittest.TestCase):
    """Tests for the Motor class."""
    def test_invalid_efficiency_raises_error(self):
        """Check if invalid efficiency values raise a ValueError."""
        with self.assertRaises(ValueError):
            Motor(efficiency=1.5)
        with self.assertRaises(ValueError):
            Motor(efficiency=-0.1)
    def test_current_draw_calculation(self):
        """Check if current draw calculation matches formula P / (U * eff)."""
        motor = Motor(efficiency=0.85)
        current = motor.get_current_draw(power=340.0, voltage=40.0)
        # 340 / (40 * 0.85) = 340 / 34 = 10.0 A
        self.assertAlmostEqual(current, 10.0)


class TestTrackCalculator(unittest.TestCase):
    """Test cases for the TrackCalculator class."""
    
    def setUp(self):
        #dummy calculator with an empty track to test edge cases
        dummy_track = GpsTrack.__new__(GpsTrack)
        dummy_track.track_points = []
        self.calc = TrackCalculator(dummy_track)

    def test_empty_track_distance(self):
        """Check if an empty track returns 0.0 distance."""
        self.assertEqual(self.calc.calculate_total_distance(), 0.0)

    def test_empty_track_power_profile(self):
        """Check if an empty track returns an empty power profile."""
        self.assertEqual(self.calc.calculate_power_profile(), [])

    def test_empty_track_air_density(self):
        """Check if air density calculation handles empty tracks securely."""
        self.assertEqual(self.calc.calculate_air_density_profile(), [])

    def test_calories_zero_work(self):
        """Check if 0 mechanical work correctly results in 0 burned calories."""
        report = self.calc.calculate_energy_and_calories(sim=None)
        self.assertEqual(report["calories_burned_kcal"], 0.0)


if __name__ == '__main__':
    unittest.main()