from pathlib import Path
from src.scripts.gps_classes import GpsTrack
from src.scripts.calculator import TrackCalculator
from src.utils.plotting import TrackPlotter

from src.e_bike_homework.battery_pack import LiPoBatteryPack
from src.e_bike_homework.battery_pack import NmcBatteryPack
from src.e_bike_homework.motor import Motor
from src.e_bike_homework.ebike_model import VehicleModel
from src.e_bike_homework.ebike_simulator import EBikeSimulator

def main():
    data_path = Path("data/final_project_input_data.csv")
    plot_path = Path("results/track_plot.png")

    try:
        # Load data from CSV into GpsTrack object
        my_track = GpsTrack("Hauptroute", data_path)

        # Make calcualtions unsing TrackCalculator
        calculator = TrackCalculator(my_track)
        distance = calculator.calculate_total_distance()
        print(f"Total distance of the track: {distance:.2f} km")

        
        # Plot the track using TrackPlotter
        plotter = TrackPlotter(my_track)
        plotter.plot_track_path(plot_path)

        # calculate Profiles from GPS data
        power_profile = calculator.calculate_power_profile()
        durations = calculator.calculate_segment_durations()

        # Simulate LiPo battery
        print("---LiPo-Battery Simulation---")
        battery_lipo = LiPoBatteryPack(
            capacity_nom_Ah=10,
            internal_resistance_mOhm= 80.0,
            initial_soc=1.0,
            Vmin=32.0,
            Vmax=42.0
        )
        
        # simulation
        motor_lipo = Motor(efficiency=0.85)
        vehicle_lipo = VehicleModel(mass=80.0, initial_v=0.1)
        sim_lipo = EBikeSimulator(motor_lipo, battery_lipo, vehicle_lipo)
            
        # start simulation with error handling
        try:
            sim_lipo.simulate(power_profile, durations)
            print(f"Finale Akku-Ladung: {battery_lipo.soc * 100:.1f}%")
            print(f"Endgeschwindigkeit: {vehicle_lipo.v:.2f} m/s")
        except RuntimeError as e:
            print(f"Simulation abgebrochen: {e}")
            print(f"Akku-Ladung bei Abbruch: {battery_lipo.soc * 100:.1f}%")


        # Simulate Nmc battery
        print("---Nmc-Battery Simulation---")
        battery_nmc = NmcBatteryPack(
            capacity_nom_Ah=10,
            internal_resistance_mOhm= 70.0,
            initial_soc=1.0,
            Vmin=32.0,
            Vmax=42.0
        ) 

        # simulation
        motor_nmc = Motor(efficiency=0.85)
        vehicle_nmc = VehicleModel(mass=80.0, initial_v=0.1)
        sim_nmc = EBikeSimulator(motor_nmc, battery_nmc, vehicle_nmc)

        # start simulation with error handling
        try:
            sim_nmc.simulate(power_profile, durations)
            print(f"Finale Akku-Ladung: {battery_nmc.soc * 100:.1f}%")
        except RuntimeError as e:
            print(f"Simulation abgebrochen: {e}")
            print(f"Akku-Ladung bei Abbruch: {battery_nmc.soc * 100:.1f}%")


    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
