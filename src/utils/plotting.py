import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import pydeck as pdk
from src.gps.calculator import TrackCalculator
import logging
from src.utils import example_utils as utils

# Logging config
logger = logging.getLogger(__name__)


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
        logger.info(f"Plot successfully saved to: {output_path}")

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
        logger.info(f"Höhenprofil gespeichert unter: {output_path}")
        


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
        logger.info(f"Geschwindigkeitsprofil gespeichert unter: {output_path}")


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
        logger.info(f"SoC-Vergleich gespeichert unter: {output_path}")


    def plot_temperature_profile(self, calculator, output_path, window_size: int = 5):
        """
        Creates a plot of temperature using moving average for smoothing.
        """
        raw_temps = calculator.calculate_temperature_profile()
        
        # Apply moving average smoothing
        smoothed_temps = utils.moving_average(raw_temps, window_size=window_size)
        
        durations = np.array(calculator.calculate_segment_durations())
        cum_time_sec = np.zeros(len(durations) + 1)
        cum_time_sec[1:] = np.cumsum(durations)
        
        # Convert cumulative seconds to minutes
        cum_time_min = cum_time_sec / 60.0
        
        plt.figure(figsize=(10, 6))
        
        # Plot raw data slightly transparent in the background
        plt.plot(cum_time_min[:-1], raw_temps, color='gray', alpha=0.4, linestyle=':', label="Raw Data")
        
        # Plot smoothed data in the foreground
        plt.plot(cum_time_min[:-1], smoothed_temps, color='orange', linewidth=2.0, label=f"Smoothed (Moving Avg, w={window_size})")
        
        plt.title(f"Temperature Profile - {self.gps_track.dataset_name}")
        plt.xlabel("Time / min")
        plt.ylabel("Temperature / °C")
        plt.grid(True)
        plt.legend(loc="upper right")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Smoothed temperature profile saved to: {output_path}")


    def plot_pace_profile(self, calculator, output_path):
        """
        Creates a bar chart of the pace (min/km) for each kilometer.
        """
        pace_profile = calculator.calculate_pace_profile()
        if not pace_profile:
            logger.warning("No pace data available for plotting.")
            return
            
        kilometers = list(range(1, len(pace_profile) + 1))
        
        plt.figure(figsize=(10, 6))
        # Draw as a bar chart (typical for pace profiles in running/cycling apps)
        plt.bar(kilometers, pace_profile, color='purple', alpha=0.7, edgecolor='indigo', width=0.8)
        
        # Draw average pace as a red dashed line
        avg_pace = calculator.calculate_average_pace()
        avg_min = int(avg_pace)
        avg_sec = int(round((avg_pace - avg_min) * 60))
        if avg_sec == 60:
            avg_min += 1
            avg_sec = 0
            
        plt.axhline(y=avg_pace, color='red', linestyle='--', linewidth=1.5, 
                    label=f"Avg: {avg_min}:{avg_sec:02d} min/km")
        
        plt.title(f"Pace per Kilometer - {self.gps_track.dataset_name}")
        plt.xlabel("Kilometer")
        plt.ylabel("Pace (min/km)")
        
        # Format Y-axis labels as MM:SS
        def format_y_labels(y_val, *args):
            minutes = int(y_val)
            seconds = int(round((y_val - minutes) * 60))
            if seconds == 60:
                minutes += 1
                seconds = 0
            return f"{minutes}:{seconds:02d}"
            
        from matplotlib.ticker import FuncFormatter
        plt.gca().yaxis.set_major_formatter(FuncFormatter(format_y_labels))
        
        plt.grid(axis='y', linestyle=':', alpha=0.6)
        # Label the X-axis with numbers only every 5 km
        ticks = [k for k in kilometers if k % 5 == 0]
        plt.xticks(ticks)
        plt.legend(loc="upper right")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Pace profile saved to: {output_path}")    


    def plot_interactive_3d_map(self, calculator: TrackCalculator, output_path):
        """
        Creates an interactive 3D map of the GPS route using pydeck (HTML output).
        """
        track_points = self.gps_track.track_points
        if not track_points:
            logger.warning("No GPS data available for pydeck map visualization.")
            return

        # 1. Convert track points into a pandas DataFrame
        data = []
        for p in track_points:
            data.append({
                'lat': p.latitude,
                'lon': p.longitude,
                'elevation': p.elevation if p.elevation is not None else 0.0
            })
        df = pd.DataFrame(data)

        # 2. Calculate actual route statistics from TrackCalculator
        speeds_mps = calculator.calculate_speed_profile()
        max_speed = round(float(np.max(speeds_mps)) * 3.6, 1) if speeds_mps else 0.0
        avg_speed = round(float(np.mean(speeds_mps)) * 3.6, 1) if speeds_mps else 0.0
        total_dist = round(calculator.calculate_total_distance(), 2)

        # 3. Prepare 3D geometry (vertical elevation multiplier = 5.0 for visual clarity)
        elevation_multiplier = 5.0
        min_elev = df['elevation'].min()
        max_elev = df['elevation'].max()
        elev_diff = max_elev - min_elev if (max_elev - min_elev) > 0 else 1.0

        vertical_lines = []
        top_path_segments = []

        for i in range(len(df)):
            p = df.iloc[i]
            current_relative_h = (p['elevation'] - min_elev) * elevation_multiplier
            ratio = (p['elevation'] - min_elev) / elev_diff
            color = [int(255 * ratio), 50, int(255 * (1 - ratio)), 150]

            vertical_lines.append({
                'start': [p['lon'], p['lat'], 0],
                'end': [p['lon'], p['lat'], current_relative_h],
                'color': color,
                'real_elev': round(p['elevation'], 2),
                'rel_elev': round(p['elevation'] - min_elev, 2)
            })

        for i in range(len(df) - 1):
            p1 = df.iloc[i]
            p2 = df.iloc[i + 1]
            h1 = (p1['elevation'] - min_elev) * elevation_multiplier
            h2 = (p2['elevation'] - min_elev) * elevation_multiplier
            ratio = (p1['elevation'] - min_elev) / elev_diff
            color = [int(255 * ratio), 50, int(255 * (1 - ratio)), 255]

            top_path_segments.append({
                'path': [[p1['lon'], p1['lat'], h1], [p2['lon'], p2['lat'], h2]],
                'color': color,
                'real_elev': round(p1['elevation'], 2),
                'rel_elev': round(p1['elevation'] - min_elev, 2)
            })

        # 4. Define pydeck layers for vertical pillars and top path
        curtain_layer = pdk.Layer(
            "LineLayer",
            data=pd.DataFrame(vertical_lines),
            get_source_position="start",
            get_target_position="end",
            get_color="color",
            get_width=3,
            pickable=True
        )

        top_layer = pdk.Layer(
            "PathLayer",
            data=pd.DataFrame(top_path_segments),
            get_path="path",
            get_color="color",
            get_width=10,
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=df['lat'].iloc[0], longitude=df['lon'].iloc[0],
            zoom=15.5, pitch=65, bearing=45
        )

        info_html = f"""
        <div style="background: rgba(255,255,255,0.85); padding: 15px; border-radius: 8px; font-family: Arial; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h3 style="margin-top:0; color: #333;">Track Statistics ({self.gps_track.dataset_name})</h3>
            <b>Max Speed:</b> {max_speed} km/h<br>
            <b>Avg Speed:</b> {avg_speed} km/h<br>
            <b>Total Distance:</b> {total_dist} km
        </div>
        """

        deck = pdk.Deck(
            layers=[curtain_layer, top_layer],
            initial_view_state=view_state,
            map_provider='carto',
            map_style=pdk.map_styles.LIGHT,
            tooltip={"text": "Absolute Elevation: {real_elev} m\nRelative Elevation: {rel_elev} m"},
            description=info_html
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        deck.to_html(str(output_path))
        logger.info(f"Interactive 3D map successfully saved to: {output_path}")

        

    
if __name__ == '__main__':
    pass