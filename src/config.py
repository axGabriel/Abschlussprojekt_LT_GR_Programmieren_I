from dataclasses import dataclass
# changed the constants to dataclasses because they seemed cleaner
@dataclass(frozen=True)
class PhysicsConstants:
    GRAVITY_EARTH: float = 9.81
    GRAVITY_MOON: float = 1.62
    GRAVITY_MARS: float = 3.71
    GRAVITY_JUPITER: float = 24.79
    EARTH_RADIUS_KM: float = 6371.0
    EARTH_RADIUS_M: float = 6_371_000.0
    RHO_AIR_SEA_LEVEL: float = 1.225

@dataclass(frozen=True)
class AtmosphereConstants:
    P0_PASCAL: float = 101325.0
    T0_KELVIN: float = 288.15
    L_TEMP_LAPSE_RATE: float = 0.0065
    R_U_IDEAL_GAS: float = 8.31446
    M_MOLAR_MASS_AIR: float = 0.0289652

@dataclass(frozen=True)
class BioenergeticsConstants:
    HUMAN_EFFICIENCY_CYCLING: float = 0.24  # 24 % biological efficiency
    JOULES_PER_KCAL: float = 4184.0         # 1 kcal == 4184 Joule


# will be used if there arent any other settings provided
@dataclass
class SimulationSettings:
    mass_rider_kg: float = 70.0
    mass_bike_kg: float = 10.0
    cw_A_m2: float = 0.5625
    c_r: float = 0.015
    wheel_diameter_inch: float = 27.0
    motor_constant_NmA: float = 1.5

# for easy access to the constants
PHYSICS = PhysicsConstants()
ATMOSPHERE = AtmosphereConstants()
SETTINGS = SimulationSettings()
BIO = BioenergeticsConstants()