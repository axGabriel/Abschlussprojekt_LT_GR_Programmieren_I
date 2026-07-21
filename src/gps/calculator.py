import numpy as np
from src import config as cfg
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
        track_points = self.gps_track.track_points
        if len(track_points) < 2:
            return 0.0

        lat_rad = np.radians([p.latitude for p in track_points])
        lon_rad = np.radians([p.longitude for p in track_points])

        # calc differences
        diff_lat = np.diff(lat_rad)
        diff_lon = np.diff(lon_rad)

        # Haversine formula for distance calculation
        a = np.sin(diff_lat / 2)**2 + np.cos(lat_rad[:-1]) * np.cos(lat_rad[1:]) * np.sin(diff_lon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distances = cfg.PHYSICS.EARTH_RADIUS_KM * c

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
        end_time = track_points[-1].timestamp

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
        total_time_s = self.calculate_total_time()

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
        segment_distances_km = cfg.PHYSICS.EARTH_RADIUS_KM * c

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

    def _calculate_segment_distances_m(self):
        """
        Internal helper: returns a numpy array of Haversine distances in meters
        for each pair of track points.
        Returns an empty array if fewer than 2 points exist.
        """
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return np.array([])

        lat_rad = np.radians(np.array([p.latitude  for p in track_points]))
        lon_rad = np.radians(np.array([p.longitude for p in track_points]))

        diff_lat = np.diff(lat_rad)
        diff_lon = np.diff(lon_rad)

        a = np.sin(diff_lat / 2)**2 + np.cos(lat_rad[:-1]) * np.cos(lat_rad[1:]) * np.sin(diff_lon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        return cfg.PHYSICS.EARTH_RADIUS_M * c

    def _calculate_segment_times_s(self):
        """
        Internal helper: returns a numpy array of time differences in seconds
        for each pair of track points.
        Returns None if any timestamp is missing.
        """
        track_points = self.gps_track.track_points
        timestamps = [p.timestamp for p in track_points]

        if any(t is None for t in timestamps):
            return None

        return np.array([
            (timestamps[i + 1] - timestamps[i]).total_seconds()
            for i in range(len(timestamps) - 1)
        ])

    def calculate_speed_profile(self):
        """
        Calculates the speed for each GPS segment in m/s.
        """
        distances_m = self._calculate_segment_distances_m()
        time_diffs_s = self._calculate_segment_times_s()

        if time_diffs_s is None or len(distances_m) == 0:
            return []

        # avoid division by zero: segments with del_t=0 get speed 0
        valid = time_diffs_s > 0
        speeds = np.zeros(len(distances_m))
        speeds[valid] = distances_m[valid] / time_diffs_s[valid]

        return speeds.tolist()

    def calculate_acceleration_profile(self):
        """
        Calculates the acceleration for each GPS segment in m/s^2.
        """
        speeds = self.calculate_speed_profile()
        time_diffs_s = self._calculate_segment_times_s()

        if not speeds or time_diffs_s is None:
            return []

        speeds_arr = np.array(speeds)
        # acceleration between segment i and i+1
        # first segment: no speed  a = 0
        accelerations = np.zeros(len(speeds_arr))
        del_t = time_diffs_s[1:]    # time of segments 1..n-1
        del_v = np.diff(speeds_arr) # speed change between segments

        valid = del_t > 0
        accelerations[1:][valid] = del_v[valid] / del_t[valid]

        return accelerations.tolist()

    def calculate_slope_profile(self):
        """
        Calculates the slope angle for each GPS segment in radians.
        """
        track_points = self.gps_track.track_points

        if len(track_points) < 2:
            return []

        elevations = [p.elevation for p in track_points]
        if any(e is None for e in elevations):
            return []

        distances_m = self._calculate_segment_distances_m()
        if len(distances_m) == 0:
            return []

        delta_h = np.diff(np.array(elevations, dtype=float))

        # avoid division by zero for zero-length horizontal segments
        slopes = np.zeros(len(distances_m))
        valid = distances_m > 0
        slopes[valid] = np.arctan(delta_h[valid] / distances_m[valid])

        return slopes.tolist()

    def calculate_air_density_profile(self):
        """
        Uses elevation and temperature from the GPS data to get air density.
        Returns a list of air density values in kg/m^3.
        """
        track_points = self.gps_track.track_points
        if not track_points:
            return []
        
        # exponent for barometric formula
        exponent = (cfg.PHYSICS.GRAVITY_EARTH * cfg.ATMOSPHERE.M_MOLAR_MASS_AIR) / (cfg.ATMOSPHERE.R_U_IDEAL_GAS * cfg.ATMOSPHERE.L_TEMP_LAPSE_RATE)
        R_spec = cfg.ATMOSPHERE.R_U_IDEAL_GAS / cfg.ATMOSPHERE.M_MOLAR_MASS_AIR
        
        densities = []
        for p in track_points:
            h = p.elevation if p.elevation is not None else 0.0
            temp_c = p.temperature if p.temperature is not None else 20.0
            
            T_kelvin = temp_c + 273.15
            p_h = cfg.ATMOSPHERE.P0_PASCAL * (1 - (cfg.ATMOSPHERE.L_TEMP_LAPSE_RATE * h) / cfg.ATMOSPHERE.T0_KELVIN) ** exponent
            rho = p_h / (R_spec * T_kelvin)

            densities.append(rho)
            
        return densities

    def calculate_power_profile(
        self,
        mass_rider_kg: float = None,
        mass_bike_kg: float  = None,
        cw_A_m2: float = None,
        c_r: float = None,
    ):
        """
        Calculates the required drive power for each GPS segment in Watts.
        """
        mass_rider_kg = mass_rider_kg if mass_rider_kg is not None else cfg.SETTINGS.mass_rider_kg
        mass_bike_kg = mass_bike_kg if mass_bike_kg is not None else cfg.SETTINGS.mass_bike_kg
        cw_A_m2 = cw_A_m2 if cw_A_m2 is not None else cfg.SETTINGS.cw_A_m2
        c_r = c_r if c_r is not None else cfg.SETTINGS.c_r

        speeds = self.calculate_speed_profile()
        accelerations = self.calculate_acceleration_profile()
        slopes = self.calculate_slope_profile()
        densities = self.calculate_air_density_profile()

        if not speeds or not accelerations or not slopes:
            return []

        m_total = mass_rider_kg + mass_bike_kg

        v = np.array(speeds)
        a = np.array(accelerations)
        phi = np.array(slopes)
        
        if densities and len(densities) > len(speeds):
            rho_air = np.array(densities[:-1])
        else:
            rho_air = cfg.PHYSICS.RHO_AIR_SEA_LEVEL

        F_inertia = m_total * a
        F_slope = m_total * cfg.PHYSICS.GRAVITY_EARTH * np.sin(phi)
        F_drag = 0.5 * rho_air * cw_A_m2 * v**2
        F_rolling = c_r * m_total * cfg.PHYSICS.GRAVITY_EARTH * np.cos(phi)

        F_total = F_inertia + F_slope + F_drag + F_rolling
        P = F_total * v  # W

        return P.tolist()

    def calculate_max_power(
        self,
        mass_rider_kg: float = None,
        mass_bike_kg: float = None,
        cw_A_m2: float = None,
        c_r: float = None,
    ):
        """
        Calculates the maximum required power in Watts.
        """
        mass_rider_kg = mass_rider_kg if mass_rider_kg is not None else cfg.SETTINGS.mass_rider_kg
        mass_bike_kg = mass_bike_kg if mass_bike_kg is not None else cfg.SETTINGS.mass_bike_kg
        cw_A_m2 = cw_A_m2 if cw_A_m2 is not None else cfg.SETTINGS.cw_A_m2
        c_r = c_r if c_r is not None else cfg.SETTINGS.c_r

        power_profile = self.calculate_power_profile(mass_rider_kg, mass_bike_kg, cw_A_m2, c_r)
        if not power_profile:
            return 0.0
        return float(np.max(power_profile))

    def calculate_torque_profile(
        self,
        wheel_diameter_inch: float = None, # Not in meters because bike wheels are usually specified in inches
        mass_rider_kg: float = None,
        mass_bike_kg: float = None,
        cw_A_m2: float = None,
        c_r: float = None,
    ):
        """
        Calculates the drive torque at the wheel for each GPS segment in Nm.
        Only one wheel is driven (hub motor).
        """
        wheel_diameter_inch = wheel_diameter_inch if wheel_diameter_inch is not None else cfg.SETTINGS.wheel_diameter_inch
        mass_rider_kg = mass_rider_kg if mass_rider_kg is not None else cfg.SETTINGS.mass_rider_kg
        mass_bike_kg = mass_bike_kg if mass_bike_kg is not None else cfg.SETTINGS.mass_bike_kg
        cw_A_m2 = cw_A_m2 if cw_A_m2 is not None else cfg.SETTINGS.cw_A_m2
        c_r = c_r if c_r is not None else cfg.SETTINGS.c_r

        speeds = self.calculate_speed_profile()
        accelerations = self.calculate_acceleration_profile()
        slopes = self.calculate_slope_profile()
        densities = self.calculate_air_density_profile()

        if not speeds or not accelerations or not slopes:
            return []

        m_total = mass_rider_kg + mass_bike_kg
        # Raddurchmesser in Zoll (inch) -> Radius in Meter umrechnen (1 inch = 0.0254 m)
        r_wheel = (wheel_diameter_inch * 0.0254) / 2.0

        v = np.array(speeds)
        a = np.array(accelerations)
        phi = np.array(slopes)
        
        if densities and len(densities) > len(speeds):
            rho_air = np.array(densities[:-1])
        else:
            rho_air = cfg.PHYSICS.RHO_AIR_SEA_LEVEL

        F_inertia = m_total * a
        F_slope = m_total * cfg.PHYSICS.GRAVITY_EARTH * np.sin(phi)
        F_drag = 0.5 * rho_air * cw_A_m2 * v**2
        F_rolling = c_r * m_total * cfg.PHYSICS.GRAVITY_EARTH * np.cos(phi)

        F_total = F_inertia + F_slope + F_drag + F_rolling
        T = F_total * r_wheel  # Nm

        return T.tolist()

    def calculate_motor_current_profile(
        self,
        motor_constant_NmA: float = None,
        wheel_diameter_inch: float = None,
        mass_rider_kg: float = None,
        mass_bike_kg: float = None,
        cw_A_m2: float = None,
        c_r: float = None,
    ):
        """
        Calculates the motor current for each GPS segment in Amperes.
        """
        motor_constant_NmA = motor_constant_NmA if motor_constant_NmA is not None else cfg.SETTINGS.motor_constant_NmA
        wheel_diameter_inch = wheel_diameter_inch if wheel_diameter_inch is not None else cfg.SETTINGS.wheel_diameter_inch
        mass_rider_kg = mass_rider_kg if mass_rider_kg is not None else cfg.SETTINGS.mass_rider_kg
        mass_bike_kg = mass_bike_kg if mass_bike_kg is not None else cfg.SETTINGS.mass_bike_kg
        cw_A_m2 = cw_A_m2 if cw_A_m2 is not None else cfg.SETTINGS.cw_A_m2
        c_r = c_r if c_r is not None else cfg.SETTINGS.c_r

        if motor_constant_NmA <= 0:
            raise ValueError("Motor constant must be positive.")

        torques = self.calculate_torque_profile(
            wheel_diameter_inch = wheel_diameter_inch,
            mass_rider_kg = mass_rider_kg,
            mass_bike_kg = mass_bike_kg,
            cw_A_m2 = cw_A_m2,
            c_r = c_r,
        )

        if not torques:
            return []

        currents = np.array(torques) / motor_constant_NmA
        return currents.tolist()

    def calculate_segment_durations(self):
        """
        Returns the time duration in seconds for each GPS segment.
        """
        time_diffs_s = self._calculate_segment_times_s()
        if time_diffs_s is None:
            return []
        return time_diffs_s.tolist()
    
    # rho air depends on altitude, temperature, and pressure
    # might be moved to calculator.py
    def calculate_dynamic_rho_air(self, altitude_m, temperature_celsius):
        """ 
        Calculate the air density at a given altitude and temperature using the barometric formula.
        """
        #pressure in pascal at given altitude
        pressure_pa = cfg.ATMOSPHERE.P0_PASCAL * (1 - cfg.ATMOSPHERE.L_TEMP_LAPSE_RATE * altitude_m / cfg.ATMOSPHERE.T0_KELVIN) ** (cfg.PHYSICS.GRAVITY_EARTH * cfg.ATMOSPHERE.M_MOLAR_MASS_AIR / (cfg.ATMOSPHERE.R_U_IDEAL_GAS * cfg.ATMOSPHERE.L_TEMP_LAPSE_RATE))
        temperature_kelvin = temperature_celsius + 273.15

        return pressure_pa / (cfg.ATMOSPHERE.R_U_IDEAL_GAS / cfg.ATMOSPHERE.M_MOLAR_MASS_AIR * temperature_kelvin)



    def calculate_energy_and_calories(
        self,
        sim: object = None,
        human_efficiency: float = cfg.BIO.HUMAN_EFFICIENCY_CYCLING,
        mass_rider_kg: float = None,
        mass_bike_kg: float = None,
    ) -> dict:
        """
        Calculates total route mechanical energy, electric motor contribution,
        rider muscle work, and estimated dietary calories burned (kcal).
        
        Returns a dictionary with all energy metrics.
        """
        power_profile = self.calculate_power_profile(mass_rider_kg, mass_bike_kg)
        durations = self.calculate_segment_durations()

        if not power_profile or not durations:
            return {
                "total_work_wh": 0.0, "motor_work_wh": 0.0, "rider_work_wh": 0.0,
                "calories_burned_kcal": 0.0, "motor_share_pct": 0.0, "rider_share_pct": 0.0
            }

        # Total mechanical work required for the route (Joules)
        total_work_joules = sum(max(0.0, p) * dt for p, dt in zip(power_profile, durations))

        # Electric motor work if a simulator run is provided
        motor_work_joules = 0.0
        if sim and hasattr(sim, "voltageValues") and hasattr(sim, "currentValues") and sim.voltageValues:
            batt_energy_joules = sum(
                u * i * dt for u, i, dt in zip(sim.voltageValues, sim.currentValues, durations)
            )
            motor_work_joules = batt_energy_joules * sim.motor.efficiency

        # Remaining work pedaled by human muscles
        human_work_joules = max(0.0, total_work_joules - motor_work_joules)

        # Convert mechanical Joules to dietary kcal
        calories_kcal = calories_kcal = human_work_joules / (cfg.BIO.JOULES_PER_KCAL * human_efficiency)

        return {
            "total_work_wh": total_work_joules / 3600.0,
            "motor_work_wh": motor_work_joules / 3600.0,
            "rider_work_wh": human_work_joules / 3600.0,
            "calories_burned_kcal": calories_kcal,
            "motor_share_pct": (motor_work_joules / total_work_joules * 100.0) if total_work_joules > 0 else 0.0,
            "rider_share_pct": (human_work_joules / total_work_joules * 100.0) if total_work_joules > 0 else 0.0,
        }    


    def calculate_temperature_profile(self) -> list[float]:
        """gernerate temperatureprofile °C per segment via GPS-Data"""
        temperatures = []
        points = self.gps_track.track_points
        for i in range(len(points) - 1):
            temp = points[i].temperature if points[i].temperature is not None else 20.0
            temperatures.append(temp)
        return temperatures

if __name__ == '__main__':
    pass
