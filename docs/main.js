// --- Pyodide Engine Logic ---

const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

const constants_py = `
from sympy import symbols, sqrt
c, G, h, k_B, e, epsilon_0 = symbols('c G h k_B e epsilon_0', positive=True, real=True)

# THE FIX: Define the base dictionary first.
PLANCK_UNITS = {
    'm_P': sqrt(h * c / G), 'l_P': sqrt(h * G / c**3), 't_P': sqrt(h * G / c**5),
    'T_P': sqrt(h * c**5 / (G * k_B**2)), 'E_P': sqrt(h * c**5 / G), 'F_P': c**4 / G,
    'P_P': c**5 / G, 'rho_P': c**7 / (h * G**2), 'p_P': sqrt(h * c**3 / G),
    'v_P': c,
}
# THEN, add the composite units that depend on the others. This prevents the NameError.
PLANCK_UNITS['f_P'] = 1 / PLANCK_UNITS['t_P']
PLANCK_UNITS['a_P'] = PLANCK_UNITS['l_P'] / PLANCK_UNITS['t_P']**2
PLANCK_UNITS['alpha'] = e**2 / (2 * epsilon_0 * h * c)

VARIABLE_TO_PLANCK_UNIT = {
    'M': 'm_P', 'M1': 'm_P', 'M2': 'm_P', 'm': 'm_P',
    'r': 'l_P', 'l': 'l_P', 'x': 'l_P', 'lambda': 'l_P', 'r_s': 'l_P',
    't': 't_P', 'T': 'T_P', 'E': 'E_P', 'F': 'F_P', 'P': 'P_P',
    'rho': 'rho_P', 'p': 'p_P', 'a': 'a_P', 'v': 'v_P', 'f': 'f_P',
    'alpha': 'alpha',
}
`;

const deriver_py = `
import sympy
from sympy import simplify, pi
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

def parse_postulate(postulate_string):
    if '~' not in postulate_string: raise ValueError("Postulate must contain '~'")
    target_str, expr_str = [s.strip() for s in postulate_string.split('~')]
    target_symbol = sympy.Symbol(target_str, positive=True, real=True)
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_symbols = { s: sympy.Symbol(s, positive=True, real=True) for s in ['M1', 'M2', 'r_s', 'M', 'm', 'r', 'l', 'x', 'lambda', 't', 'E', 'F', 'P', 'rho', 'p', 'a', 'v', 'f', 'T', 'alpha'] }
    local_symbols['pi'] = pi
    expression = parse_expr(expr_str, local_dict=local_symbols, transformations=transformations)
    return target_symbol, expression

def derive_law_from_postulate(postulate_string):
    try:
        # --- THIS IS A DIRECT IMPLEMENTATION OF YOUR ORIGINAL, WORKING LOGIC ---
        target_symbol, expression = parse_postulate(postulate_string)
        all_vars = expression.free_symbols.union({target_symbol})

        #this block fixes alpha becuase it is dimensionless being promoted to dimensions
        alpha_symbol = sympy.Symbol('alpha')
        if alpha_symbol in expression.free_symbols:
            expression = expression.subs(alpha_symbol, PLANCK_UNITS['alpha'])
        
        # 1. Create a dictionary of simple Planck symbols (e.g., 'F_P', 'm_P')
        planck_symbols = {key: sympy.Symbol(key) for key in PLANCK_UNITS.keys()}
        
        # 2. Formulate the dimensionless postulate using these simple symbols.
        subs_dict_simple = {sym: sym / planck_symbols[VARIABLE_TO_PLANCK_UNIT.get(str(sym))] for sym in all_vars if VARIABLE_TO_PLANCK_UNIT.get(str(sym))}
        lhs_simple = target_symbol.subs(subs_dict_simple)
        rhs_simple = expression.subs(subs_dict_simple)
        dimensionless_eq_simple = sympy.Eq(lhs_simple, rhs_simple)

        # 3. Solve this simple equation FIRST.
        solution_with_planck_symbols = sympy.solve(dimensionless_eq_simple, target_symbol)
        if not solution_with_planck_symbols: raise ValueError("Could not solve for the target variable.")
        
        # 4. NOW, substitute the full, complex definitions into the solved result.
        #    This 'substitutions_full' dictionary contains both the simple names and their complex values.
        substitutions_full = {**planck_symbols, **PLANCK_UNITS}
        final_solution_unsimplified = solution_with_planck_symbols[0].subs(substitutions_full)
        
        # 5. Finally, simplify the result. This is robust and correct.
        final_law = simplify(final_solution_unsimplified)
        # --- End of Correct Logic ---

        output = (
            f"Deriving physical law from postulate: {postulate_string}\\n\\n"
            f"1. Conceptual Postulate:\\n   {target_symbol} ~ {expression}\\n\\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\\n"
            f"{sympy.pretty(dimensionless_eq_simple, use_unicode=False)}\\n\\n"
            f"3. Solving and Simplifying...\\n\\n"
            f"------------------------------------\\n"
            f"   RESULTING PHYSICAL LAW\\n"
            f"------------------------------------\\n"
            f"Final form: {target_symbol} = {final_law}\\n\\n"
            f"Note: Any dimensionless geometric factors must be included in the initial postulate."
        )
        return output.strip()
    except Exception as e:
        import traceback
        return f"ERROR: {e}\\n\\nTraceback:\\n{traceback.format_exc()}"
`;

async function setupPyodide() {
    outputElement.textContent = "Initializing Python environment...";
    try {
        let pyodide = await loadPyodide();
        outputElement.textContent = "Loading scientific libraries (SymPy)...";
        await pyodide.loadPackage("sympy");
        outputElement.textContent = "Loading LawForge engine...";
        pyodide.runPython(constants_py.replaceAll('\\\\', '\\\\\\\\'));
        pyodide.runPython(deriver_py.replaceAll('\\\\', '\\\\\\\\'));
        outputElement.textContent = "Environment ready. Please enter a postulate.";
        console.log("LawForge engine is ready.");
        return pyodide;
    } catch (error) {
        outputElement.textContent = `CRITICAL ERROR during initialization: ${error}`;
        console.error("Initialization failed:", error);
    }
}

let pyodideReadyPromise = setupPyodide();

async function runDerivation() {
    deriveButton.disabled = true;
    outputElement.textContent = "Waiting for environment...";
    let pyodide = await pyodideReadyPromise;
    if (!pyodide) {
        outputElement.textContent = "Initialization failed. Please refresh the page.";
        deriveButton.disabled = false; return;
    }
    const postulate = postulateInput.value;
    if (!postulate) {
        outputElement.textContent = "Please enter a postulate.";
        deriveButton.disabled = false; return;
    }
    outputElement.textContent = "Deriving law...";
    try {
        pyodide.globals.set("postulate_string", postulate);
        const pythonCode = `result = derive_law_from_postulate(postulate_string)`;
        await pyodide.runPythonAsync(pythonCode);
        const result = pyodide.globals.get("result");
        outputElement.textContent = result;
    } catch (error) {
        outputElement.textContent = `An error occurred during derivation:\n${error}`;
        console.error(error);
    } finally {
        deriveButton.disabled = false;
    }
}

postulateInput.addEventListener("keyup", (event) => {
    if (event.key === "Enter") { event.preventDefault(); deriveButton.click(); }
});

// --- UI Interaction Logic ---
document.addEventListener('DOMContentLoaded', function() {
    
    const modal = document.getElementById("axesModal");
    const link = document.getElementById("showAxesLink");
    const closeButton = document.querySelector(".close-button");

    if (modal && link && closeButton) {
        link.onclick = function(event) {
            event.preventDefault();
            modal.style.display = "block";
        }
        closeButton.onclick = function() {
            modal.style.display = "none";
        }
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    }

    const selector = document.getElementById("postulateSelector");
    if (selector) {
        selector.addEventListener('change', function() {
            const selectedValue = this.value;
            if (selectedValue) {
                postulateInput.value = selectedValue;
                runDerivation();
            }
        });
    }
});
