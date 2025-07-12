// --- Pyodide Engine Logic ---

const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

const constants_py = `
from sympy import symbols, sqrt
c, G, h, k_B = symbols('c G h k_B', positive=True, real=True)
PLANCK_UNITS = {
    'm_P': sqrt(h * c / G), 'l_P': sqrt(h * G / c**3), 't_P': sqrt(h * G / c**5),
    'T_P': sqrt(h * c**5 / (G * k_B**2)), 'E_P': sqrt(h * c**5 / G), 'F_P': c**4 / G,
    'P_P': c**5 / G, 'rho_P': c**7 / (h * G**2), 'p_P': sqrt(h * c**3 / G),
    'a_P': sqrt(c**7 / (h * G)), 'f_P': sqrt(c**5 / (h * G)), 'v_P': c,
}
VARIABLE_TO_PLANCK_UNIT = {
    'M': 'm_P', 'M1': 'm_P', 'M2': 'm_P', 'm': 'm_P',
    'r': 'l_P', 'l': 'l_P', 'x': 'l_P', 'lambda': 'l_P', 'r_s': 'l_P',
    't': 't_P', 'T': 'T_P', 'E': 'E_P', 'F': 'F_P', 'P': 'P_P',
    'rho': 'rho_P', 'p': 'p_P', 'a': 'a_P', 'v': 'v_P', 'f': 'f_P',
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
    local_symbols = { s: sympy.Symbol(s, positive=True, real=True) for s in ['M1', 'M2', 'r_s', 'M', 'm', 'r', 'l', 'x', 'lambda', 't', 'E', 'F', 'P', 'rho', 'p', 'a', 'v', 'f', 'T'] }
    local_symbols['pi'] = pi
    expression = parse_expr(expr_str, local_dict=local_symbols, transformations=transformations)
    return target_symbol, expression

def derive_law_from_postulate(postulate_string):
    try:
        target_symbol, expression = parse_postulate(postulate_string)

        # --- THE FIX: Build a separate, clean "display" equation ---
        # 1. Create simple symbols for display (e.g., m_P, l_P)
        display_planck_symbols = {key: sympy.Symbol(key) for key in PLANCK_UNITS.keys()}
        target_planck_key_str = VARIABLE_TO_PLANCK_UNIT.get(str(target_symbol))
        if not target_planck_key_str: raise ValueError(f"Unknown target variable: {target_symbol}")

        # 2. Build the "display" version of the equation for printing
        display_lhs = target_symbol / display_planck_symbols[target_planck_key_str]
        display_subs_dict = {sym: sym / display_planck_symbols[VARIABLE_TO_PLANCK_UNIT.get(str(sym))] for sym in expression.free_symbols if VARIABLE_TO_PLANCK_UNIT.get(str(sym))}
        display_rhs = expression.subs(display_subs_dict)
        display_eq = sympy.Eq(display_lhs, display_rhs)
        # --- End of Display Fix ---
        
        # Now, build the actual equation for calculation with full sqrt definitions
        calculus_lhs = target_symbol / PLANCK_UNITS[target_planck_key_str]
        calculus_subs_dict = {sym: sym / PLANCK_UNITS[VARIABLE_TO_PLANCK_UNIT.get(str(sym))] for sym in expression.free_symbols if VARIABLE_TO_PLANCK_UNIT.get(str(sym))}
        calculus_rhs = expression.subs(calculus_subs_dict)
        calculus_eq = sympy.Eq(calculus_lhs, calculus_rhs)
        
        solution = sympy.solve(calculus_eq, target_symbol)
        if not solution: raise ValueError("Could not solve for the target variable.")
        
        simplified_solution = simplify(solution[0])
        final_law = simplified_solution

        output = (
            f"Deriving physical law from postulate: {postulate_string}\\n\\n"
            f"1. Conceptual Postulate:\\n   {target_symbol} ~ {expression}\\n\\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\\n"
            f"{sympy.pretty(display_eq, use_unicode=False)}\\n\\n" # Use the clean display version
            f"3. Solving and Simplifying...\\n\\n"
            f"------------------------------------\\n"
            f"   RESULTING PHYSICAL LAW\\n"
            f"------------------------------------\\n"
            f"Final form: {target_symbol} = {final_law}\\n\\n"
            f"Note: Any dimensionless geometric factors (e.g., 1/2, 8*pi) must be included in the initial postulate."
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
    
    // --- Modal Popup Logic ---
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

    // --- Dropdown Logic ---
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
