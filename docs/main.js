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
    'f_P': sqrt(c**5 / (h * G)), 'v_P': c, 'a_P': l_P / t_P**2, 
}
#'a_P': sqrt(c**7 / (h * G))
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
        
        # --- THE FIX: Revert to a simpler, more robust substitution logic ---
        all_symbols = expression.free_symbols.union({target_symbol})
        
        # Build the clean "display" equation
        display_planck_symbols = {key: sympy.Symbol(key) for key in PLANCK_UNITS.keys()}
        display_subs_dict = {sym: sym / display_planck_symbols[VARIABLE_TO_PLANCK_UNIT.get(str(sym))] for sym in all_symbols if VARIABLE_TO_PLANCK_UNIT.get(str(sym))}
        
        display_lhs = (target_symbol).subs(display_subs_dict)
        display_rhs = (expression).subs(display_subs_dict)
        display_eq = sympy.Eq(display_lhs, display_rhs)

        # Build the actual calculus equation for solving
        calculus_subs_dict = {sym: sym / PLANCK_UNITS[VARIABLE_TO_PLANCK_UNIT.get(str(sym))] for sym in all_symbols if VARIABLE_TO_PLANCK_UNIT.get(str(sym))}

        calculus_lhs = (target_symbol).subs(calculus_subs_dict)
        calculus_rhs = (expression).subs(calculus_subs_dict)
        calculus_eq = sympy.Eq(calculus_lhs, calculus_rhs)
        # --- End of Fix ---
        
        solution = sympy.solve(calculus_eq, target_symbol)
        if not solution: raise ValueError("Could not solve for the target variable.")
        
        simplified_solution = simplify(solution[0])
        final_law = simplified_solution

        output = (
            f"Deriving physical law from postulate: {postulate_string}\\n\\n"
            f"1. Conceptual Postulate:\\n   {target_symbol} ~ {expression}\\n\\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\\n"
            f"{sympy.pretty(display_eq, use_unicode=False)}\\n\\n"
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
