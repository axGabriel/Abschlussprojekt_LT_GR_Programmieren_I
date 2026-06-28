import pandas as pd
from pathlib import Path

class GeographicData():
    """
    Base class for all our geographic data.
    Provides a simple foundation and shows how inheritance works here.
    """
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name


class TrackingPoint():
    """
    A simple container to store a single coordinate point.
    """
    def __init__(self, latitude, longitude):
        # make sure the coordinates are stored as floats
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    def __str__(self):
        # for easy printing of the tracking point
        return f"Point(Lat: {self.latitude}, Lon: {self.longitude})"


class GpsTrack(GeographicData):
    """
    The main class for handling GPS routes.
    It takes care of loading the CSV and turning rows into clean objects.
    """
    def __init__(self, dataset_name, csv_file_path):
        # initialize the base class with the dataset name
        super().__init__(dataset_name)
        
        # pathlib for path handling
        self.csv_file_path = Path(csv_file_path)
        self.track_points = []
        
        # trigger the loading of the gps data from the CSV file
        self._load_gps_data_from_file()

    def _load_gps_data_from_file(self):
        # check if the file exists before trying to read it
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"File not found at: {self.csv_file_path}")

        print(f"Loading data for track: {self.dataset_name}...")
        
        # using pandas to read the CSV, may change this later
        gps_data_table = pd.read_csv(self.csv_file_path, sep=';')
        
        # check if the required columns are present
        if 'lat' not in gps_data_table.columns or 'lon' not in gps_data_table.columns:
            raise ValueError("The CSV needs 'lat' and 'lon' columns to work.")

        # looping through the table and create a TrackingPoint for every row
        # row_index is  not used could be replaced with _ to indicate it's unused but we didnt learn this yet so i left it as is
        for row_index, current_data_row in gps_data_table.iterrows():
            new_tracking_point = TrackingPoint(latitude = current_data_row['lat'], longitude = current_data_row['lon'])
            self.track_points.append(new_tracking_point)


    def get_point_count(self):
        # helper returning the number of points in this track
        return len(self.track_points)


if __name__ == '__main__':
    file_path = Path(__file__).parent.parent.parent / 'data' / 'final_project_input_data.csv'
    
    try:
        my_first_gps_track = GpsTrack(
            dataset_name = "Final Project Main Route",
            csv_file_path = file_path
        )
        
        # Print info about the loaded track.
        print(f"Track: {my_first_gps_track.dataset_name}")
        print(f"Total points: {my_first_gps_track.get_point_count()}")
        
        if my_first_gps_track.get_point_count() > 0:
            print(f"Start: {my_first_gps_track.track_points[0]}")
            print(f"End: {my_first_gps_track.track_points[-1]}")

    except Exception as error_message:
        print(f"Error: {error_message}")