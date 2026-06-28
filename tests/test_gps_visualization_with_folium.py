import os
import pandas as pd
import folium

def test_visualize_gps_data():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'final_project_input_data.csv')
    df = pd.read_csv(data_path, sep=';')
    print(f"{len(df)} Datenpunkte geladen.")

    start_lat, start_lon = df['lat'].iloc[0], df['lon'].iloc[0]
    end_lat, end_lon = df['lat'].iloc[-1], df['lon'].iloc[-1]
    m = folium.Map(location=[start_lat, start_lon], zoom_start=14)

    folium.PolyLine(
        locations=df[['lat', 'lon']].values.tolist(),
        color='blue',
        weight=5,
        opacity=0.8
    ).add_to(m)

    folium.Marker([start_lat, start_lon], popup='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker([end_lat, end_lon], popup='Ende', icon=folium.Icon(color='red')).add_to(m)

    output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'gps_visualization.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)

if __name__ == '__main__':
    test_visualize_gps_data()