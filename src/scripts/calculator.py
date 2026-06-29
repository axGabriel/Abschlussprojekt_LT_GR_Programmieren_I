import numpy as np

class TrackCalculator():
    """
    Class to perform calculations on GPS tracks.
    Uses the GpsTrack object to access track points (lat, lon, elevation, timestamp).
    """
    def __init__(self, gps_track):
        """
        Initializes the calculator with a GpsTrack object.
        """
        self.gps_track = gps_track

    def calculate_total_distance(self):
        """
        Calculates the total distance of the track in kilometers
        using the Haversine formula for geographic coordinates.
        Returns 0.0 if there are fewer than 2 points.
        """
        earth_radius_in_km = 6371.0
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return 0.0

        latitudes  = np.array([p.latitude  for p in track_points])
        longitudes = np.array([p.longitude for p in track_points])

        # convert to rad
        lat_rad = np.radians(latitudes)
        lon_rad = np.radians(longitudes)

        # calc differences
        diff_lat = np.diff(lat_rad)
        diff_lon = np.diff(lon_rad)

        # Haversine formula for distance calculation
        a = np.sin(diff_lat / 2)**2 + np.cos(lat_rad[:-1]) * np.cos(lat_rad[1:]) * np.sin(diff_lon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distances = earth_radius_in_km * c

        return float(np.sum(distances))

    def calculate_elevation_gain(self):
        """
        Calculates the total elevation gain (Aufstieg) in meters.
        Sums up all positive elevation differences between consecutive points.
        Returns 0.0 if elevation data is missing or fewer than 2 points exist.
        """
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return 0.0

        # collect only points that have elevation data
        elevations = [p.elevation for p in track_points if p.elevation is not None]

        if len(elevations) < 2:
            return 0.0

        elevations = np.array(elevations)
        differences = np.diff(elevations)

        # sum only positive differences (going uphill)
        total_gain = float(np.sum(differences[differences > 0]))
        return total_gain

    def calculate_elevation_loss(self):
        """
        Calculates the total elevation loss (Abstieg) in meters as a positive number.
        Sums up all negative elevation differences between consecutive points.
        Returns 0.0 if elevation data is missing or fewer than 2 points exist.
        """
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return 0.0

        # collect points that have elevation data
        elevations = [p.elevation for p in track_points if p.elevation is not None]

        if len(elevations) < 2:
            return 0.0

        elevations = np.array(elevations)
        differences = np.diff(elevations)

        # sum only negative differences
        total_loss = float(np.sum(np.abs(differences[differences < 0])))
        return total_loss

    def calculate_total_time(self):
        """
        Calculates the total duration of the track in seconds.
        Uses the timestamps of the first and last track point.
        Returns 0.0 if timestamps are missing.
        """
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return 0.0

        start_time = track_points[0].timestamp
        end_time   = track_points[-1].timestamp

        if start_time is None or end_time is None:
            return 0.0

        duration_seconds = (end_time - start_time).total_seconds()
        return float(duration_seconds)

    def calculate_average_speed(self):
        """
        Calculates the average speed of the track in km/h.
        Uses total distance divided by total time.
        Returns 0.0 if total time is zero or timestamps are missing.
        """
        total_distance_km = self.calculate_total_distance()
        total_time_s      = self.calculate_total_time()

        if total_time_s <= 0:
            return 0.0

        # convert seconds to hours
        total_time_h = total_time_s / 3600.0
        average_speed_kmh = total_distance_km / total_time_h

        return float(average_speed_kmh)

    def calculate_max_speed(self):
        """
        Calculates the maximum speed between any two consecutive track points in km/h.
        Uses Haversine distance divided by the time difference for each segment.
        Returns 0.0 if timestamps are missing or fewer than 2 points exist.
        """
        earth_radius_in_km = 6371.0
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return 0.0

        latitudes  = np.array([p.latitude  for p in track_points])
        longitudes = np.array([p.longitude for p in track_points])

        # convert to radians
        lat_rad = np.radians(latitudes)
        lon_rad = np.radians(longitudes)

        diff_lat = np.diff(lat_rad)
        diff_lon = np.diff(lon_rad)

        a = np.sin(diff_lat / 2)**2 + np.cos(lat_rad[:-1]) * np.cos(lat_rad[1:]) * np.sin(diff_lon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        segment_distances_km = earth_radius_in_km * c

        # calculate time differences between points in hours
        timestamps = [p.timestamp for p in track_points]

        if any(t is None for t in timestamps):
            return 0.0

        # time differences in hours
        time_diffs_s = np.array([(timestamps[i + 1] - timestamps[i]).total_seconds() for i in range(len(timestamps) - 1)])

        # avoid division by zero for identical timestamps
        valid = time_diffs_s > 0
        if not np.any(valid):
            return 0.0

        segment_speeds_kmh = segment_distances_km[valid] / (time_diffs_s[valid] / 3600.0)
        max_speed_kmh = float(np.max(segment_speeds_kmh))

        return max_speed_kmh
    
if __name__ == '__main__':
    pass