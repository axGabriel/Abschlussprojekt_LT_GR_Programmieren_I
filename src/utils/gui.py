import customtkinter as ctk
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def show_summary_window(calculator, sim_lipo, sim_nmc, energy_report):
    """
    Opens a CustomTkinter GUI window summarizing the simulation results and linking plots.
    """
    # Helper function to open files in Windows default viewer
    def open_plot(relative_path):
        full_path = Path(relative_path).resolve()
        if full_path.exists():
            os.startfile(full_path)
        else:
            logger.warning(f"Could not open file, path does not exist: {full_path}")

    try:
        # Set up CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize root window
        root = ctk.CTk()
        root.title("E-Bike Simulation Summary")
        root.geometry("700x550")
        root.resizable(False, False)
        
        # Header title
        header = ctk.CTkLabel(
            root, 
            text="E-Bike Simulation Summary Results", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=15)
        
        # Grid frame for two columns
        grid_frame = ctk.CTkFrame(root, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # --- LEFT COLUMN: Route Statistics ---
        left_frame = ctk.CTkFrame(grid_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        grid_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            left_frame, 
            text="Route Statistics", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Time formatting
        total_time_s = calculator.calculate_total_time()
        hours = int(total_time_s // 3600)
        minutes = int((total_time_s % 3600) // 60)
        seconds = int(total_time_s % 60)
        
        # Pace formatting
        avg_pace = calculator.calculate_average_pace()
        pace_min = int(avg_pace)
        pace_sec = int(round((avg_pace - pace_min) * 60))
        if pace_sec == 60:
            pace_min += 1
            pace_sec = 0
            
        stats_text = (
            f"• Distance: {calculator.calculate_total_distance():.2f} km\n\n"
            f"• Duration: {hours:02d}:{minutes:02d}:{seconds:02d}\n\n"
            f"• Avg Speed: {calculator.calculate_average_speed():.1f} km/h\n\n"
            f"• Max Speed: {calculator.calculate_max_speed():.1f} km/h\n\n"
            f"• Avg Pace: {pace_min}:{pace_sec:02d} min/km"
        )
        
        ctk.CTkLabel(
            left_frame, 
            text=stats_text, 
            justify="left", 
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=10)
        
        # --- RIGHT COLUMN: Energy & Battery ---
        right_frame = ctk.CTkFrame(grid_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        grid_frame.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            right_frame, 
            text="Energy & Battery", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        energy_text = (
            f"• Total Work: {energy_report['total_work_wh']:.1f} Wh\n\n"
            f"• Rider Share: {energy_report['rider_share_pct']:.1f}%\n"
            f"  ({energy_report['rider_work_wh']:.1f} Wh)\n\n"
            f"• Motor Share: {energy_report['motor_share_pct']:.1f}%\n"
            f"  ({energy_report['motor_work_wh']:.1f} Wh)\n\n"
            f"• Calories Burned: {energy_report['calories_burned_kcal']:.0f} kcal\n\n"
            f"• Final LiPo SoC: {sim_lipo.socValues[-1]*100:.1f}%\n\n"
            f"• Final NMC SoC: {sim_nmc.socValues[-1]*100:.1f}%"
        )
        
        ctk.CTkLabel(
            right_frame, 
            text=energy_text, 
            justify="left", 
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=10)
        
        # --- BOTTOM SECTION: Open Plots & Maps ---
        plot_frame = ctk.CTkFrame(root)
        plot_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            plot_frame, 
            text="Open Generated Charts & Maps:", 
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(10, 5))
        
        # Row 1 of buttons
        ctk.CTkButton(plot_frame, text="Track Map (2D)", width=140, command=lambda: open_plot("results/track_plot.png")).grid(row=1, column=0, padx=10, pady=5)
        ctk.CTkButton(plot_frame, text="Elevation Profile", width=140, command=lambda: open_plot("results/elevation_profile.png")).grid(row=1, column=1, padx=10, pady=5)
        ctk.CTkButton(plot_frame, text="Speed Profile", width=140, command=lambda: open_plot("results/speed_profile.png")).grid(row=1, column=2, padx=10, pady=5)
        ctk.CTkButton(plot_frame, text="Interactive 3D Map ", fg_color="#2b7a78", hover_color="#3a8f8d", width=140, command=lambda: open_plot("results/interactive_map.html")).grid(row=1, column=3, padx=10, pady=5)
        
        # Row 2 of buttons
        ctk.CTkButton(plot_frame, text="Temperature Profile", width=140, command=lambda: open_plot("results/temperature_profile.png")).grid(row=2, column=0, padx=10, pady=5)
        ctk.CTkButton(plot_frame, text="Pace Profile", width=140, command=lambda: open_plot("results/pace_profile.png")).grid(row=2, column=1, padx=10, pady=5)
        ctk.CTkButton(plot_frame, text="SoC Comparison", width=140, command=lambda: open_plot("results/soc_comparison.png")).grid(row=2, column=2, padx=10, pady=5)
        ctk.CTkButton(plot_frame, text="Close Summary", fg_color="#d9534f", hover_color="#c9302c", width=140, command=root.destroy).grid(row=2, column=3, padx=10, pady=5)

        root.mainloop()
    except Exception as e:
        logger.error(f"Failed to open GUI summary window: {e}")