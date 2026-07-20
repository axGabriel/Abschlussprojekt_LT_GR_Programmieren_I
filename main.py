import logging
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from src.gps.gps_classes import GpsTrack
from src.gps.calculator import TrackCalculator
from src.utils.plotting import TrackPlotter

from src.core.battery_pack import LiPoBatteryPack
from src.core.battery_pack import NmcBatteryPack
from src.core.motor import Motor
from src.core.ebike_model import VehicleModel
from src.simulation.ebike_simulator import EBikeSimulator
from src import config as cfg



# Logging config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



# source data can be picked from exploerer
def select_input_file(default_path: Path) -> Path:
    """Öffnet ein Windows-Explorer-Fenster zur Auswahl einer CSV-Datei."""
    root = tk.Tk()
    root.withdraw() 
    
    selected_file = filedialog.askopenfilename(
        title="Wähle die GPS-Daten (CSV) für die Simulation aus",
        initialdir=default_path.parent if default_path.exists() else Path.cwd(),
        filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")]
    )
    
    root.destroy()
    
    if selected_file:
        return Path(selected_file)
    else:
        logger.info(f"Keine Datei ausgewählt. Nutze Standarddatei: {default_path}")
        return default_path


def main():
    default_data_path = Path("data/final_project_input_data.csv")
    data_path = select_input_file(default_data_path)
    logger.info(f"Nutze Datensatz von: {data_path}")
    plot_path = Path("results/track_plot.png")
    elevation_plot_path = Path("results/elevation_profile.png")
    speed_plot_path = Path("results/speed_profile.png")
    soc_comparison_path = Path("results/soc_comparison.png")
    interactive_map_path = Path("results/interactive_map.html")

    try:
        # Load data from CSV into GpsTrack object
        my_track = GpsTrack("Hauptroute", data_path)

        # Make calculations using TrackCalculator
        calculator = TrackCalculator(my_track)
        distance = calculator.calculate_total_distance()

        # Plot the track using TrackPlotter
        plotter = TrackPlotter(my_track)
        plotter.plot_track_path(plot_path)

        # Plot the hight and speed proflile using track plotter
        plotter.plot_elevation_profile(elevation_plot_path)
        plotter.plot_speed_profile(calculator, speed_plot_path)


        # Generate interactive 3D map (HTML)
        plotter.plot_interactive_3d_map(calculator, interactive_map_path)

        # calculate Profiles from GPS data
        power_profile = calculator.calculate_power_profile()
        durations = calculator.calculate_segment_durations()
        slopes = calculator.calculate_slope_profile()
        speeds = calculator.calculate_speed_profile()
        rhos = calculator.calculate_air_density_profile()

        # Simulate LiPo battery
        logger.info("---LiPo-Battery Simulation---")
        battery_lipo = LiPoBatteryPack(
            capacity_nom_Ah=10,
            internal_resistance_mOhm= 80.0,
            initial_soc=1.0,
            Vmin=32.0,
            Vmax=42.0
        )
        
        # simulation
        motor_lipo = Motor(efficiency=0.85)
        vehicle_lipo = VehicleModel(mass=cfg.SETTINGS.mass_rider_kg + cfg.SETTINGS.mass_bike_kg, initial_v=0.1)
        sim_lipo = EBikeSimulator(motor_lipo, battery_lipo, vehicle_lipo)
            
        # start simulation with error handling
        sim_lipo.simulate(power_profile, durations, slopes, speeds, rhos)
        logger.info(f"Finale Akku-Ladung: {battery_lipo.soc * 100:.1f}%")
        logger.info(f"Endgeschwindigkeit: {vehicle_lipo.v:.2f} m/s")


        # Simulate Nmc battery
        logger.info("---Nmc-Battery Simulation---")
        battery_nmc = NmcBatteryPack(
            capacity_nom_Ah=10,
            internal_resistance_mOhm= 70.0,
            initial_soc=1.0,
            Vmin=32.0,
            Vmax=42.0
        ) 

        # simulation
        motor_nmc = Motor(efficiency=0.85)
        vehicle_nmc = VehicleModel(mass=cfg.SETTINGS.mass_rider_kg + cfg.SETTINGS.mass_bike_kg, initial_v=0.1)
        sim_nmc = EBikeSimulator(motor_nmc, battery_nmc, vehicle_nmc)

        # start simulation with error handling
        sim_nmc.simulate(power_profile, durations, slopes, speeds, rhos)
        logger.info(f"Finale Akku-Ladung: {battery_nmc.soc * 100:.1f}%")
        logger.info(f"Endgeschwindigkeit: {vehicle_nmc.v:.2f} m/s")


        # save comparison plot 
        plotter.plot_soc_comparison(sim_lipo, sim_nmc, durations, soc_comparison_path)

        # calorie report
        energy_report = calculator.calculate_energy_and_calories(sim_lipo)
        logger.info("--- Calorie & Energy Report (LiPo Run) ---")
        logger.info(f"Total Route Work: {energy_report['total_work_wh']:.2f} Wh")
        logger.info(f"Motor Share: {energy_report['motor_work_wh']:.2f} Wh ({energy_report['motor_share_pct']:.1f}%)")
        logger.info(f"Rider Share: {energy_report['rider_work_wh']:.2f} Wh ({energy_report['rider_share_pct']:.1f}%)")
        logger.info(f"Estimated Calories Burned by Rider: {energy_report['calories_burned_kcal']:.0f} kcal")

    except Exception as error:
        logger.error(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
