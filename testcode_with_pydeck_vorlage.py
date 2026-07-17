import pandas as pd
import pydeck as pdk
import webbrowser
import os
from pathlib import Path

def run_real_data_demo():
    # =======================================================
    # KONFIGURATION
    # =======================================================
    # Multiplikator für die vertikale Überhöhung (z.B. 5.0)
    ELEVATION_MULTIPLIER = 5.0  
    
    # Pfad zu deiner CSV-Datei
    csv_pfad_string = r"G:\Meine Ablage\02_Studium\FH_SM2\Programmieren\Abschlussprojekt\Abschlussprojekt_LT_GR_Programmieren_I\data\test_data_Leon.csv"
    # =======================================================

    csv_path = Path(csv_pfad_string)
    if not csv_path.exists():
        print(f"Fehler: Konnte die Datei '{csv_path.absolute()}' nicht finden.")
        return

    # --- DATENLADEN ---
    print(f"Lade Daten aus '{csv_path}'...")
    df = pd.read_csv(csv_path, sep=';')
    
    # Spaltennamen-Korrektur: 'ele' -> 'elevation' für einheitliche Verarbeitung
    if 'ele' in df.columns:
        df.rename(columns={'ele': 'elevation'}, inplace=True)
        
    if 'lat' not in df.columns or 'lon' not in df.columns:
        print("Fehler: CSV benötigt 'lat' und 'lon' Spalten!")
        return
        
    df = df.fillna({'elevation': 0})

    # --- BERECHNUNG DER STATISTIKEN ---
    # Dummy-Berechnung für Geschwindigkeit, da diese noch in deinem Calculator-Modul fehlt
    max_speed = 45.2  # Beispielwert
    avg_speed = 22.8  # Beispielwert
    total_dist = 12.4 # Beispielwert
    
    # --- VORBEREITUNG DER GEOMETRIE ---
    min_elev = df['elevation'].min()
    max_elev = df['elevation'].max()
    elev_diff = max_elev - min_elev if (max_elev - min_elev) > 0 else 1.0 

    vertical_lines = []
    top_path_segments = []
    
    # Erstelle die 3D-Struktur (Pfeiler + Oberkante)
    for i in range(len(df)):
        p = df.iloc[i]
        # Boden-Korrektur: Aktuelle Höhe minus min_elev, damit alles am Boden startet
        current_relative_h = (p['elevation'] - min_elev) * ELEVATION_MULTIPLIER
        
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
        
        h1 = (p1['elevation'] - min_elev) * ELEVATION_MULTIPLIER
        h2 = (p2['elevation'] - min_elev) * ELEVATION_MULTIPLIER
        
        ratio = (p1['elevation'] - min_elev) / elev_diff
        color = [int(255 * ratio), 50, int(255 * (1 - ratio)), 255]
        
        top_path_segments.append({
            'path': [[p1['lon'], p1['lat'], h1], [p2['lon'], p2['lat'], h2]],
            'color': color,
            'real_elev': round(p1['elevation'], 2),
            'rel_elev': round(p1['elevation'] - min_elev, 2)
        })

    # --- LAYER DEFINITION ---
    # Layer 1: Die Wand-Pfeiler
    curtain_layer = pdk.Layer(
        "LineLayer",
        data=pd.DataFrame(vertical_lines),
        get_source_position="start",
        get_target_position="end",
        get_color="color",
        get_width=3,
        pickable=True
    )
    
    # Layer 2: Der Pfad-Kamm
    top_layer = pdk.Layer(
        "PathLayer",
        data=pd.DataFrame(top_path_segments),
        get_path="path",
        get_color="color",
        get_width=10,
        pickable=True
    )

    # --- UI & RENDER ---
    view_state = pdk.ViewState(
        latitude=df['lat'].iloc[0], longitude=df['lon'].iloc[0],
        zoom=15.5, pitch=65, bearing=45
    )

    # HTML für das Infofenster oben links
    info_html = f"""
    <div style="background: rgba(255,255,255,0.8); padding: 15px; border-radius: 8px; font-family: Arial;">
        <h3 style="margin-top:0;">Track Statistik</h3>
        <b>Max Speed:</b> {max_speed} km/h<br>
        <b>Avg Speed:</b> {avg_speed} km/h<br>
        <b>Distanz:</b> {total_dist} km
    </div>
    """

    r = pdk.Deck(
        layers=[curtain_layer, top_layer],
        initial_view_state=view_state,
        map_provider='carto',
        map_style=pdk.map_styles.LIGHT,
        tooltip={"text": "Absolute Höhe: {real_elev} m\nRelative Höhe: {rel_elev} m"},
        description=info_html  # Fügt das Infofenster hinzu
    )

    # --- SPEICHERN ---
    output_file = "results/pydeck_real_data.html"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    r.to_html(output_file)
    
    full_path = 'file://' + os.path.realpath(output_file)
    print(f"Fertig! Öffne die Visualisierung unter: {full_path}")
    webbrowser.open(full_path)

if __name__ == '__main__':
    run_real_data_demo()