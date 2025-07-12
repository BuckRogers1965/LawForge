import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from lawforge.constants import PLANCK_UNITS, VARIABLE_TO_PLANCK_UNIT

def parse_postulate(postulate_string):
    if '~' not in postulate_string:
        raise ValueError("Postulate must contain '~' to separate sides.")
    target_str, expr_str = [s.strip() for s in postulate_string.split('~')]
    target_symbol = sympy.Symbol(target_str)

    # Enable parsing of expressions like "M1*M2"
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_symbols = {str(s): s for s in [sympy.Symbol('M1'), sympy.Symbol('M2'), sympy.Symbol('r_s')]}
    expression = parse_expr(expr_str, local_dict=local_symbols, transformations=transformations)
    return target_symbol, expression

def derive_law_from_postulate(postulate_string):
    try:
        target_symbol, expression = parse_postulate(postulate_string)

        # Normalize the target symbol
        target_planck_key = VARIABLE_TO_PLANCK_UNIT.get(str(target_symbol))
        if not target_planck_key: raise ValueError(f"Unknown target variable: {target_symbol}")
        lhs_normalized = target_symbol / PLANCK_UNITS[target_planck_key]

        # Normalize the expression symbols
        subs_dict = {}
        for sym in expression.free_symbols:
            s_str = str(sym)
            planck_key = VARIABLE_TO_PLANCK_UNIT.get(s_str)
            if not planck_key: continue

            if planck_key == 'v_P': # Velocity special case
                subs_dict[sym] = sym / sympy.Symbol('c')
            elif planck_key == 'f_P': # Frequency special case
                 subs_dict[sym] = sym * PLANCK_UNITS['t_P']
            else:
                subs_dict[sym] = sym / PLANCK_UNITS[planck_key]

        rhs_normalized = expression.subs(subs_dict)
        dimensionless_eq = sympy.Eq(lhs_normalized, rhs_normalized)
        solution = sympy.solve(dimensionless_eq, target_symbol)

        if not solution: raise ValueError("Could not solve for the target variable.")

        final_law = sympy.Symbol('k') * solution[0]

        output = (
            f"Deriving physical law from postulate: {postulate_string}\n\n"
            f"1. Conceptual Postulate:\n   {target_symbol} ~ {expression}\n\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\n"
            f"   {sympy.pretty(dimensionless_eq, use_unicode=False)}\n\n"
            f"3. Solving for {target_symbol} to project into chosen coordinate system...\n\n"
            f"------------------------------------\n"
            f"   RESULTING PHYSICAL LAW\n"
            f"------------------------------------\n"
            f"   {sympy.pretty(sympy.Eq(target_symbol, final_law), use_unicode=False)}\n\n"
            f"Note: 'k' represents a dimensionless constant (e.g., 1/2, 8*pi) from geometry or integration, which is not derived by this calculus."
        )
        return output.strip()

    except Exception as e:
        import traceback
        return f"ERROR: {{e}}\n\nTraceback:\n{{traceback.format_exc()}}\nPlease check your postulate format (e.g., 'E ~ m')."
