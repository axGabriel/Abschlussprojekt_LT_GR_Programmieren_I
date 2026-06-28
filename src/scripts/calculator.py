import numpy as np

class TrackCalculator():
    """
    Class to perform calculations on GPS tracks.
    """
    def __init__(self, gps_track):
        """
        Initializes the calculator with a GpsTrack object.
        """
        self.gps_track = gps_track

    def calculate_total_distance(self):
        """
        Calculates the total distance of the track using the
        Haversine formula for geographic coordinates.
        """
        earth_radius_in_km = 6371.0 
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return 0.0

        latitudes = np.array([p.latitude for p in track_points])
        longitudes = np.array([p.longitude for p in track_points])

        # convert to rad
        lat_rad = np.radians(latitudes)
        lon_rad = np.radians(longitudes)

        # calc differences
        diff_lat = np.diff(lat_rad)
        diff_lon = np.diff(lon_rad)

        # for distance - haversine formula
        a = np.sin(diff_lat / 2)**2 + np.cos(lat_rad[:-1]) * np.cos(lat_rad[1:]) * np.sin(diff_lon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        
        distances = earth_radius_in_km * c
        
        return np.sum(distances)
    
    def calculate_elevation_gain(self):
        pass

    def calculate_elevation_loss(self):
        pass

    def calculate_total_time(self):
        pass

    def calculate_average_speed(self):
        pass

    def calculate_max_speed(self):
        pass