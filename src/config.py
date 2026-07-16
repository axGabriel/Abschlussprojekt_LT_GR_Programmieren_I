# constants for the rest of the code

GRAVITATION_EARTH = 9.81  
GRAVITATION_MOON = 1.62
GRAVITATION_MARS = 3.71
GRAVITATION_JUPITER = 24.79

EARTH_RADIUS_KM = 6371.0
EARTH_RADIUS_M = 6_371_000.0

P0_PASCAL = 101325.0  # sea level standard pressure
T0_KELVIN = 288.15  # sea level standard temperature
L_TEMP_LAPSE_RATE = 0.0065 # temperature lapse rate: how much the temperature decreases with altitude in the troposphere
R_U_IDEAL_GAS = 8.31446  # universal ideal gas constant
M_MOLAR_MASS_AIR = 0.0289652  # molar mass of air

#placeholder for air density at sea level, will implement a function to calculate it based on altitude 
RHO_AIR = 1.225