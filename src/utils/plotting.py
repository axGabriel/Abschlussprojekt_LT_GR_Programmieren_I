import matplotlib.pyplot as plt
import numpy as np
from src.gps.calculator import TrackCalculator

class TrackPlotter:
    """
    Class to visualize GPS tracks.
    """
    def __init__(self, gps_track):
        """
        Initializes the plotter with a GpsTrack object.
        """
        self.gps_track = gps_track

    def plot_track_path(self, output_path):
        """
        Creates a simple plot of the track path (Lat/Lon) and saves it.
        """
        track_points = self.gps_track.track_points
        lats = [p.latitude for p in track_points]
        lons = [p.longitude for p in track_points]

        plt.figure(figsize=(10, 6))
        plt.plot(lons, lats, marker='.', linestyle='-', color='blue')
        plt.title(f"GPS Track Visualization - {self.gps_track.dataset_name}")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid(True)
        
        # create the output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        plt.savefig(output_path)
        plt.close()
        print(f"Plot successfully saved to: {output_path}")

    def plot_elevation_profile(self, output_path):
        
        """
        Creates a plot of the elevation profile over distance.
        """

        track_points = self.gps_track.track_points
        elevations = [p.elevation for p in track_points]
        calculator = TrackCalculator(self.gps_track)
        segment_distances_km = calculator._calculate_segment_distances_m() / 1000.0
        cum_distances = np.zeros(len(track_points))
        cum_distances[1:] = np.cumsum(segment_distances_km)
        plt.figure(figsize=(10, 6))
        plt.fill_between(cum_distances, elevations, color='green', alpha=0.3)
        plt.plot(cum_distances, elevations, color='green', label='Höhenprofil', linewidth=1.5)
        
        plt.title(f"Höhenprofil - {self.gps_track.dataset_name}")
        plt.xlabel("Distanz / km")
        plt.ylabel("Höhe / m")
        plt.grid(True)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        print(f"Höhenprofil gespeichert unter: {output_path}")
        


    def plot_speed_profile(self, calculator, output_path):
        """
        Creates a plot of the speed profile over time.
        """
        
        speeds_kmh = np.array(calculator.calculate_speed_profile()) * 3.6
        durations = np.array(calculator.calculate_segment_durations())
        cum_time = np.zeros(len(durations) + 1)
        cum_time[1:] = np.cumsum(durations)
        plt.figure(figsize=(10, 6))
        plt.plot(cum_time[:-1], speeds_kmh, color='blue', linewidth=1.0)
        
        plt.title(f"Geschwindigkeitsprofil - {self.gps_track.dataset_name}")
        plt.xlabel("Zeit / s")
        plt.ylabel("Geschwindigkeit / km/h")
        plt.grid(True)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        print(f"Geschwindigkeitsprofil gespeichert unter: {output_path}")


    def plot_soc_comparison(self, sim_lipo, sim_nmc, durations, output_path):
        """
        Creates a comparison for SoC between LiPo and NMC
        """

        
        cum_time = np.zeros(len(durations) + 1)
        cum_time[1:] = np.cumsum(durations)
        soc_lipo_pct = np.array(sim_lipo.socValues) * 100.0
        soc_nmc_pct = np.array(sim_nmc.socValues) * 100.0
        plt.figure(figsize=(10, 6))
        plt.plot(cum_time, soc_lipo_pct, label="LiPo Akku", color="blue", linestyle="-", linewidth=1.5)
        plt.plot(cum_time, soc_nmc_pct, label="NMC Akku", color="red", linestyle="--", linewidth=1.5)
        plt.title("Vergleich Ladezustand (SoC) über die Zeit")
        plt.xlabel("Zeit / s")
        plt.ylabel("Ladezustand / %")
        plt.grid(True)
        plt.legend(loc="upper right")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        print(f"SoC-Vergleich gespeichert unter: {output_path}")

    
if __name__ == '__main__':
    pass