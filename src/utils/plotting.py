import matplotlib.pyplot as plt

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

    def plot_elevation_profile(self):
        """
        Creates a plot of the elevation profile over distance.
        """
        pass

    def plot_speed_profile(self):
        """
        Creates a plot of the speed profile over time.
        """
        pass