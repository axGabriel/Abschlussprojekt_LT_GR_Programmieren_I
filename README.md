# Abschlussprojekt_LT_GR_Programmieren_I

Aufgabenstellung:
https://mrp123.github.io/MCI-MECH-B-2-PRO1-PRO1-ILV/lectures/15_abschlussprojekt/1_abschlussprojekt.html#/title-slide


---

## Umgesetzte Erweiterungen 

* **Dynamischer Temperatureinfluss**: Automatische Anpassung von Innenwiderstand und Entladeeffizienz basierend auf den echten GPS-Temperaturdaten.
* **Moving-Average-Glättung**: Rauschminderung der Temperaturaufzeichnungen mittels gleitendem Mittelwert.
* **Pace-Auswertung**: Berechnung der min/km-Pace pro Kilometer via linearer Interpolation sowie Bestimmung der Durchschnittspace.
* **Interaktive 3D-Karte**: Export des Streckenverlaufs in eine HTML-Ansicht mittels Pydeck.
* **Erweiterte Physik**: Integration von temperatur- und höhenabhängiger Luftdichte \(\rho\) sowie des Rollwiderstands \(c_r\).
* **Energie- & Kalorienrechner**: Aufteilung zwischen biologischer Eigenleistung (kcal) und elektrischer Motorarbeit (Wh).
* **Interaktives GUI-Dashboard**: Abschlussfenster (CustomTkinter) mit Klick-Verknüpfung zum Öffnen aller Diagramme.
* **Automatische Unit-Tests**: 12 automatisierte Testfälle zur Absicherung der Berechnungslogik.

---

## Quellen zu verwendeten Inhalten

* **Entfernungsberechnung (Haversine-Formel)**: [Wikipedia - Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula) (zur Berechnung des Abstands zwischen zwei Geokoordinaten auf einer Kugel).
* **Luftdichtebestimmung (Barometrische Höhenformel)**: [Wikipedia - Barometric Formula](https://en.wikipedia.org/wiki/Barometric_formula) (zur Höhen- und Temperaturabhängigkeit der Luftdichte).
* **Fahrphysikalisches Modell**: Grundlagen der Fahrzeugtechnik (Fahrwiderstandsgleichungen für Steigungs-, Luft- und Rollwiderstand).
* **Bibliotheken**: CustomTkinter (GUI-Layout), Pydeck (3D-Visualisierung), Pandas & NumPy (Datenverarbeitung), Matplotlib (Diagramme).


## Installation & Ausführung

   ```bash
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1

   # Pakete installieren:
   pip install -r requirements.txt 

   # Simulation starten:
   python main.py
   ```

Ablaufdiagramm:


```mermaid
flowchart TD
    %% UML Start and End Nodes
    StartNode(( )) ---> SelectFile(Select GPS CSV File via Picker)
    
    SelectFile --> ParseCSV(Parse CSV into GPS Track Points)
    ParseCSV --> CalcProfiles(Calculate Profiles: Power, Slopes, Speeds, Rhos, Temps, Pace)
    CalcProfiles --> InitSim(Initialize Vehicle, Motor, & Batteries)
    
    %% Loop Start
    InitSim --> ForEachSegment(Select Next GPS Segment)
    
    %% Decision Node (UML Diamond)
    ForEachSegment --> DecisionAkku{ }
    
    %% Decision Labels as Guards [Condition]
    DecisionAkku -->|"[SoC > 0%]"| CalcCurrent(Calculate Motor Current Draw)
    CalcCurrent --> Discharge(Apply Current & Discharging Rate)
    Discharge --> CalcVoltage(Calculate Effective Voltage)
    CalcVoltage --> VehicleStep(Simulate Vehicle Physical Step)
    
    DecisionAkku -->|"[SoC <= 0%]"| ZeroPower(Set Motor Power to 0)
    ZeroPower --> VehicleStep
    
    %% Loop Condition check
    VehicleStep --> NextSegment{ }
    NextSegment -->|"[Has more segments]"| ForEachSegment
    
    %% Post-simulation
    NextSegment -->|"[End of route]"| CalcEnergy(Calculate Energy & Calorie Metrics)
    CalcEnergy --> GeneratePlots(Generate PNG Plots & Interactive 3D Map)
    GeneratePlots --> ShowGUI(Show CustomTkinter Dashboard Window)
    
    %% GUI Interaction Loop
    ShowGUI --> UserChoice{ }
    UserChoice -->|"[Click chart button]"| OpenPlot(Open Chart File in OS Viewer)
    OpenPlot --> ShowGUI
    UserChoice -->|"[Click Close]"| EndNode
    
    EndNode((( )))
    
    %% Styles to match UML standard
    style StartNode fill:#000,stroke:#000,width:20px,height:20px
    style EndNode fill:#000,stroke:#000,stroke-width:4px,width:20px,height:20px
    style DecisionAkku fill:#fff,stroke:#000,width:30px,height:30px
    style NextSegment fill:#fff,stroke:#000,width:30px,height:30px
    style UserChoice fill:#fff,stroke:#000,width:30px,height:30px
```

---

## 📊 Softwarestruktur (UML Klassendiagramm)

```mermaid
classDiagram
    class GeographicData {
        +dataset_name: str
    }
    class GpsTrack {
        +csv_file_path: Path
        +track_points: list
        -load_gps_data_from_file()
        +get_point_count() int
    }
    class TrackingPoint {
        +latitude: float
        +longitude: float
        +elevation: float
        +timestamp: datetime
        +temperature: float
    }
    class TrackCalculator {
        +gps_track: GpsTrack
        +calculate_total_distance() float
        +calculate_elevation_gain() float
        +calculate_elevation_loss() float
        +calculate_total_time() float
        +calculate_average_speed() float
        +calculate_max_speed() float
        +calculate_speed_profile() list
        +calculate_acceleration_profile() list
        +calculate_slope_profile() list
        +calculate_air_density_profile() list
        +calculate_power_profile() list
        +calculate_torque_profile() list
        +calculate_motor_current_profile() list
        +calculate_temperature_profile() list
        +calculate_pace_profile() list
        +calculate_average_pace() float
        +calculate_energy_and_calories() dict
    }
    class BatteryPack {
        +capacity_nom_As: float
        +internal_resistance_mOhm: float
        +initial_soc: float
        +soc: float
        +Vmin: float
        +Vmax: float
        +apply_current(current, duration, temp)
        +voltage(current, temp) float
        +is_empty() bool
        +is_full() bool
    }
    class LiPoBatteryPack
    class NmcBatteryPack
    class Motor {
        +efficiency: float
        +get_current_draw(power, voltage) float
    }
    class VehicleModel {
        +mass: float
        +v: float
        +s: float
        +step(power, duration, slope, v_gps, cw_A, rho, c_r)
    }
    class EBikeSimulator {
        +battery: BatteryPack
        +motor: Motor
        +vehicle: VehicleModel
        +currentValues: list
        +voltageValues: list
        +speedValues: list
        +distanceValues: list
        +socValues: list
        +simulate(power, duration, slopes, speeds, rhos, temperatures)
    }
    class TrackPlotter {
        +gps_track: GpsTrack
        +plot_track_path(output_path)
        +plot_elevation_profile(output_path)
        +plot_speed_profile(calculator, output_path)
        +plot_soc_comparison(sim_lipo, sim_nmc, durations, output_path)
        +plot_temperature_profile(calculator, output_path, w)
        +plot_pace_profile(calculator, output_path)
        +plot_interactive_3d_map(calculator, output_path)
    }

    GeographicData <|-- GpsTrack
    GpsTrack *-- TrackingPoint
    TrackCalculator --> GpsTrack
    BatteryPack <|-- LiPoBatteryPack
    BatteryPack <|-- NmcBatteryPack
    EBikeSimulator --> BatteryPack
    EBikeSimulator --> Motor
    EBikeSimulator --> VehicleModel
    TrackPlotter --> GpsTrack
```

