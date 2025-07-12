const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

const constants_py = `
from sympy import symbols, sqrt

# By defining constants as positive and real, simplify() can correctly handle sqrt laws.
c, G, h, k_B = symbols('c G h k_B', positive=True, real=True)

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
    'f_P': sqrt(c**5 / (h * G)), # Planck Frequency is 1 / Planck Time
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
`;
const deriver_py = `
import sympy
from sympy import simplify
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# Note: The 'constants' module is run in the same scope by Pyodide, so its variables are available.

def parse_postulate(postulate_string):
    if '~' not in postulate_string:
        raise ValueError("Postulate must contain '~' to separate sides.")
    target_str, expr_str = [s.strip() for s in postulate_string.split('~')]

    # Define symbols as positive and real for physical quantities
    target_symbol = sympy.Symbol(target_str, positive=True, real=True)

    transformations = (standard_transformations + (implicit_multiplication_application,))

    # Also define common variables as positive and real
    local_symbols = {
        s: sympy.Symbol(s, positive=True, real=True) for s in 
        ['M1', 'M2', 'r_s', 'M', 'm', 'r', 'l', 'x', 'lambda', 't', 'E', 'F', 'P', 'rho', 'p', 'a', 'v', 'f']
    }

    expression = parse_expr(expr_str, local_dict=local_symbols, transformations=transformations)
    return target_symbol, expression

def derive_law_from_postulate(postulate_string):
    try:
        target_symbol, expression = parse_postulate(postulate_string)

        target_planck_key = VARIABLE_TO_PLANCK_UNIT.get(str(target_symbol))
        if not target_planck_key: raise ValueError(f"Unknown target variable: {target_symbol}")
        lhs_normalized = target_symbol / PLANCK_UNITS[target_planck_key]

        subs_dict = {}
        for sym in expression.free_symbols:
            s_str = str(sym)
            planck_key = VARIABLE_TO_PLANCK_UNIT.get(s_str)
            if not planck_key: continue

            if planck_key == 'v_P': subs_dict[sym] = sym / c
            elif planck_key == 'f_P': subs_dict[sym] = sym * PLANCK_UNITS['t_P']
            else: subs_dict[sym] = sym / PLANCK_UNITS[planck_key]

        rhs_normalized = expression.subs(subs_dict)
        dimensionless_eq = sympy.Eq(lhs_normalized, rhs_normalized)

        solution = sympy.solve(dimensionless_eq, target_symbol)
        if not solution: raise ValueError("Could not solve for the target variable.")

        # The key step: simplify the raw algebraic solution.
        simplified_solution = simplify(solution[0])

        final_law = sympy.Symbol('k') * simplified_solution

        output = (
            f"Deriving physical law from postulate: {postulate_string}\\n\\n"
            f"1. Conceptual Postulate:\\n   {target_symbol} ~ {expression}\\n\\n"
            f"2. Formulating Dimensionless Equation:\\n"
            f"{sympy.pretty(dimensionless_eq, use_unicode=False)}\\n\\n"
            f"3. Solving and Simplifying...\\n\\n"
            f"------------------------------------\\n"
            f"   RESULTING PHYSICAL LAW\\n"
            f"------------------------------------\\n"
            f"Final form: {target_symbol} = {final_law}\\n\\n"
            f"Note: 'k' represents a dimensionless geometric constant (e.g., 1/2, 8*pi) not derived by this calculus."
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
        pyodide.runPython(constants_py);
        pyodide.runPython(deriver_py);

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
        deriveButton.disabled = false;
        return;
    }

    const postulate = postulateInput.value;
    if (!postulate) {
        outputElement.textContent = "Please enter a postulate.";
        deriveButton.disabled = false;
        return;
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
    if (event.key === "Enter") {
        event.preventDefault();
        deriveButton.click();
    }
});

// --- Modal Popup Logic ---
const modal = document.getElementById("axesModal");
const link = document.getElementById("showAxesLink");
const closeButton = document.querySelector(".close-button");

// When the user clicks the link, open the modal
link.onclick = function(event) {
    event.preventDefault(); // Stop the link from trying to navigate
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
closeButton.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal content, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
