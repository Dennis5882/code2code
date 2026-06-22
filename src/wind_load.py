# TW-2014 풍하중 2장 건축물설계 풍력계산
# Clause 2.1~2.13

import math

# Constants
AIR_DENSITY = 0.06  # kgf/m^2 per (m/s)^2, from q(z) formula

# Terrain categories: alpha, z_g (m)
TERRAIN = {
    'A': {'alpha': 0.10, 'z_g': 300},
    'B': {'alpha': 0.15, 'z_g': 350},
    'C': {'alpha': 0.25, 'z_g': 400}
}

def wind_speed_profile(V10, z, terrain='C'):
    """
    Equation (2.5): Vz = V10 (z/10)^alpha
    """
    alpha = TERRAIN[terrain]['alpha']
    return V10 * (z / 10.0) ** alpha

def exposure_factor_K(z, terrain='C'):
    """
    Equation (2.7): K(z) = 2.774 (z/z_g)^(2alpha) for z > 5m
    For z <= 5m, use z=5m
    """
    alpha = TERRAIN[terrain]['alpha']
    z_g = TERRAIN[terrain]['z_g']
    if z <= 5.0:
        z_eff = 5.0
    else:
        z_eff = z
    return 2.774 * (z_eff / z_g) ** (2 * alpha)

def topographic_factor_Kzt(K1, K2, K3):
    """
    Equation (2.8): Kzt = (1 + K1*K2*K3)^2
    """
    return (1 + K1 * K2 * K3) ** 2

def wind_velocity_pressure(V10, I, z, Kzt=1.0, terrain='C'):
    """
    Equation (2.6): q(z) = 0.06 * K(z) * Kzt * (I * V10)^2
    """
    Kz = exposure_factor_K(z, terrain)
    return AIR_DENSITY * Kz * Kzt * (I * V10) ** 2

def gust_factor_general(Iz, gQ, Q, gV):
    """
    Equation (2.9): G = 1.927 * (1 + 1.7*Iz*sqrt(gQ^2*Q + gV^2)) / (1 + 1.7*gV*Iz)
    """
    numerator = 1 + 1.7 * Iz * math.sqrt(gQ**2 * Q + gV**2)
    denominator = 1 + 1.7 * gV * Iz
    return 1.927 * numerator / denominator

def gust_factor_flexible(Iz, gQ, Q, gR, R, gV):
    """
    Equation (2.13): Gf = 1.927 * (1 + 1.7*Iz*sqrt(gQ^2*Q + gR^2*R)) / (1 + 1.7*gV*Iz)
    """
    numerator = 1 + 1.7 * Iz * math.sqrt(gQ**2 * Q + gR**2 * R)
    denominator = 1 + 1.7 * gV * Iz
    return 1.927 * numerator / denominator

def turbulence_intensity(z, terrain='C'):
    """
    Equation (2.10): Iz = c * (z/10)^(-1/6)
    c depends on terrain: A:0.25, B:0.20, C:0.15
    """
    c_map = {'A': 0.25, 'B': 0.20, 'C': 0.15}
    c = c_map[terrain]
    return c * (z / 10.0) ** (-1.0/6.0)

def background_response(B, h, Lz):
    """
    Equation (2.11): Q = 1 / sqrt(1 + 0.63 * ((B+h)/Lz)^0.63)
    """
    return 1.0 / math.sqrt(1 + 0.63 * ((B + h) / Lz) ** 0.63)

def integral_length_scale(z, terrain='C'):
    """
    Equation (2.12): Lz = lambda * (z/10)^epsilon
    lambda, epsilon depend on terrain
    """
    params = {
        'A': {'lam': 100, 'eps': 0.20},
        'B': {'lam': 120, 'eps': 0.25},
        'C': {'lam': 140, 'eps': 0.30}
    }
    lam = params[terrain]['lam']
    eps = params[terrain]['eps']
    return lam * (z / 10.0) ** eps

def resonant_peak_factor(nf, T=3600):
    """
    Equation (2.14): gR = sqrt(2*ln(nf*T)) + 0.577 / sqrt(2*ln(nf*T))
    """
    arg = 2 * math.log(nf * T)
    return math.sqrt(arg) + 0.577 / math.sqrt(arg)

def resonant_response(nf, Lz, Vz, beta, B, h, L):
    """
    Equation (2.15): R = (1/beta) * Rn * Rh * RB * (0.53 + 0.47*RL)
    Rn from (2.16), Rh, RB, RL from (2.18)
    """
    N1 = nf * Lz / Vz  # (2.17)
    Rn = 7.47 * N1 / (1 + 10.3 * N1) ** (5.0/3.0)  # (2.16)
    # Rh, RB, RL using aerodynamic admittance function
    def admittance(eta):
        if eta == 0:
            return 1.0
        return (1.0 / eta) * (1 - (1.0 / (2 * eta**2)) * (1 - math.exp(-2 * eta)))
    eta_h = 4.6 * nf * h / Vz
    eta_B = 4.6 * nf * B / Vz
    eta_L = 15.4 * nf * L / Vz
    Rh = admittance(eta_h)
    RB = admittance(eta_B)
    RL = admittance(eta_L)
    return (1.0 / beta) * Rn * Rh * RB * (0.53 + 0.47 * RL)

def mean_wind_speed(V10, z, terrain='C'):
    """
    Equation (2.19): Vz = b * V10 * (z/10)^alpha
    b depends on terrain: A:1.0, B:0.85, C:0.70
    """
    b_map = {'A': 1.0, 'B': 0.85, 'C': 0.70}
    b = b_map[terrain]
    alpha = TERRAIN[terrain]['alpha']
    return b * V10 * (z / 10.0) ** alpha

def design_wind_pressure(q, G, Cp, qi, GCpi):
    """
    Equation (2.1): p = q*G*Cp - qi*(GCpi)
    """
    return q * G * Cp - qi * GCpi

def design_wind_force(q, G, Cf, Ac):
    """
    Equation (2.4): F = q(z_Ac) * G * Cf * Ac
    """
    return q * G * Cf * Ac

def low_rise_along_wind(I, V10, lam, Kzt_h, Az):
    """
    Equation (2.25): S_Dz = 1.49 * I^2 * V10 * lam * Kzt(h) * Az
    Note: V10 is V10(C) in the formula
    """
    return 1.49 * I**2 * V10 * lam * Kzt_h * Az

def low_rise_across_wind(S_Dz, L, B):
    """
    Equation (2.29): S_Lz = (0.6 + 0.05 * L/B) * S_Dz
    """
    return (0.6 + 0.05 * L / B) * S_Dz

def low_rise_torque(B, S_Dz_star):
    """
    Equation (2.30): S_Tz = 0.21 * B * S_Dz_star
    """
    return 0.21 * B * S_Dz_star
