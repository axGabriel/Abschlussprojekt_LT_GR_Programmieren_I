from pathlib import Path
from src.scripts.gps_classes import GpsTrack
from src.scripts.calculator import TrackCalculator
from src.utils.plotting import TrackPlotter

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

    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    main()
