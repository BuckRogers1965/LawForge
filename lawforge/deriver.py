import sympy
from sympy.parsing.sympy_parser import parse_expr
from constants import PLANCK_UNITS, VARIABLE_TO_PLANCK_UNIT

def parse_postulate(postulate_string):
    if '~' not in postulate_string:
        raise ValueError("Postulate must contain '~' to separate sides.")

    target_str, expr_str = [s.strip() for s in postulate_string.split('~')]
    target_symbol = sympy.Symbol(target_str)

    local_symbols = {str(s): s for s in [sympy.Symbol('M1'), sympy.Symbol('M2'), sympy.Symbol('r_s')]}
    expression = parse_expr(expr_str, local_dict=local_symbols)
    return target_symbol, expression

def derive_law_from_postulate(postulate_string):
    try:
        target_symbol, expression = parse_postulate(postulate_string)

        lhs_normalized = target_symbol / PLANCK_UNITS[VARIABLE_TO_PLANCK_UNIT.get(str(target_symbol))]

        subs_dict = {}
        for sym in expression.free_symbols:
            s_str = str(sym)
            if s_str in VARIABLE_TO_PLANCK_UNIT:
                planck_unit_key = VARIABLE_TO_PLANCK_UNIT[s_str]
                if planck_unit_key == 'v_P':
                    subs_dict[sym] = sym / sympy.Symbol('c')
                else:
                    subs_dict[sym] = sym / PLANCK_UNITS[planck_unit_key]
            else:
                subs_dict[sym] = sym

        rhs_normalized = expression.subs(subs_dict)
        dimensionless_eq = sympy.Eq(lhs_normalized, rhs_normalized)
        solution = sympy.solve(dimensionless_eq, target_symbol)

        if not solution:
            raise ValueError("Could not solve for the target variable.")

        final_law = solution[0]

        # Add placeholder 'k' for dimensionless constants not derived by this method
        if 'v' in str(final_law) or 'T' in str(final_law) or 'G' in str(final_law):
             final_law = sympy.Symbol('k') * final_law

        output = (
            f"Deriving physical law from postulate: {postulate_string}\n\n"
            f"1. Conceptual Postulate:\n   {target_symbol} ~ {expression}\n\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\n"
            f"   {sympy.pretty(dimensionless_eq, use_unicode=False)}\n"
            f"3. Solving for {target_symbol} to project into chosen coordinate system...\n\n"
            f"------------------------------------\n"
            f"   RESULTING PHYSICAL LAW\n"
            f"------------------------------------\n"
            f"   {sympy.pretty(sympy.Eq(target_symbol, final_law), use_unicode=False)}\n\n"
            f"Note: 'k' represents a dimensionless geometric constant (e.g., 1/2, 8*pi) not determined by this dimensional calculus."
        )
        return output.strip()

    except Exception as e:
        import traceback
        return f"ERROR: {{e}}\n\nTraceback:\n{{traceback.format_exc()}}\n\nPlease check your postulate format (e.g., 'E ~ m')."