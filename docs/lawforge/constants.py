from sympy import symbols, sqrt

c, G, h, k_B = symbols('c G h k_B')

PLANCK_UNITS = {
    'm_P': sqrt(h * c / G),
    'l_P': sqrt(h * G / c**3),
    't_P': sqrt(h * G / c**5),
    'T_P': sqrt(h * c**5 / (G * k_B**2)),
    'E_P': sqrt(h * c**5 / G),
    'F_P': c**4 / G,
    'P_P': c**5 / G,
    'rho_P': c**7 / (h * G**2),
    'p_P': sqrt(h * c**3 / G),
    'a_P': sqrt(c**7 / (h * G)),
}

VARIABLE_TO_PLANCK_UNIT = {
    'M': 'm_P', 'M1': 'm_P', 'M2': 'm_P', 'm': 'm_P',
    'r': 'l_P', 'l': 'l_P', 'x': 'l_P', 'lambda': 'l_P', 'r_s': 'l_P',
    't': 't_P',
    'T': 'T_P',
    'E': 'E_P',
    'F': 'F_P',
    'P': 'P_P',
    'rho': 'rho_P',
    'p': 'p_P',
    'a': 'a_P',
    'v': 'v_P',
    'f': 'f_P',
}
