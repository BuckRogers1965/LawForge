import os
from textwrap import dedent

# --- Project Configuration ---
PROJECT_NAME = "LawForge"
YOUR_GITHUB_USERNAME = "BuckRogers1965"

# --- File Content Definitions ---

GITIGNORE_CONTENT = """
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
pip-selfcheck.json

# IDE / Editor specific
.idea/
.vscode/
*.swp
"""

README_CONTENT = f"""
# {PROJECT_NAME}: The Physics Law Discovery Engine

This is an interactive web application that demonstrates the principle that physical laws are coordinate-dependent projections of simpler, dimensionless postulates.

## The Theory
This tool is a practical implementation of the ideas described in "The Knowledge Pattern" and "The Uniformity Principle." It posits that "fundamental constants" like `c`, `G`, and `h` are not properties of reality, but artifacts of our arbitrary, human-centric measurement systems (SI units).

The real laws of nature are simple proportionalities (e.g., `Energy ~ Mass`). This engine performs the basis transformation from that simple reality to the complex, constant-laden equations we see in textbooks.

## How to Use the Live Demo
A live, interactive version is hosted on GitHub Pages. [Click here to use it now.](https://{YOUR_GITHUB_USERNAME}.github.io/LawForge/)

## Local Development
To run tests locally:
1. Make sure you have `pytest` installed (`pip install pytest`).
2. Run the tests from the root directory: `pytest`
"""

INDEX_HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PROJECT_NAME}: The Physics Law Discovery Engine</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{PROJECT_NAME}</h1>
            <p class="subtitle">The Physics Law Discovery Engine</p>
        </header>
        <main>
            <p class="description">
                This tool demonstrates that physical laws are projections of simple,
                dimensionless postulates. It operates on the theory that "fundamental constants"
                are coordinate artifacts of our measurement system. Enter a postulate in the form
                <code>A ~ B * C**2 / D</code> to see its physical realization.
            </p>
            <div class="input-group">
                <input type="text" id="postulateInput" placeholder="e.g., T ~ 1/M" size="40">
                <button id="deriveButton" onclick="runDerivation()">Derive Law</button>
            </div>
            <hr>
            <h3>Derivation Steps:</h3>
            <pre><code id="output">Your derived law will appear here...</code></pre>
        </main>
        <footer>
            <p>
                Based on the principles of The Knowledge Pattern. Created by J. Rogers.
            </p>
            <p>
                <a href="https://github.com/{YOUR_GITHUB_USERNAME}/LawForge" target="_blank">View on GitHub</a>
            </p>
        </footer>
    </div>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js"></script>
    <script src="main.js"></script>
</body>
</html>
"""

STYLE_CSS_CONTENT = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
.container { max-width: 800px; margin: 0 auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
header { text-align: center; border-bottom: 1px solid #e0e0e0; padding-bottom: 20px; margin-bottom: 20px; }
h1 { color: #1a237e; margin: 0; }
.subtitle { color: #555; font-style: italic; }
.input-group { display: flex; gap: 10px; margin: 20px 0; }
#postulateInput { flex-grow: 1; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; }
#deriveButton { padding: 10px 20px; background-color: #3949ab; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; transition: background-color 0.3s; }
#deriveButton:hover { background-color: #1a237e; }
pre { background-color: #e8eaf6; padding: 15px; border-radius: 4px; white-space: pre-wrap; word-wrap: break-word; font-family: "Courier New", Courier, monospace; font-size: 14px; }
code { font-family: inherit; }
footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 14px; color: #777; }
a { color: #3949ab; text-decoration: none; }
a:hover { text-decoration: underline; }
"""

MAIN_JS_CONTENT = f"""
const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

async function setupPyodide() {{
    outputElement.textContent = "Initializing Python environment (this may take a moment)...";
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("sympy");

    // Correctly fetch python files from the 'lawforge' subdirectory
    const constantsPromise = fetch('lawforge/constants.py').then(res => res.text());
    const deriverPromise = fetch('lawforge/deriver.py').then(res => res.text());
    const [constants_code, deriver_code] = await Promise.all([constantsPromise, deriverPromise]);

    // Load the python modules into Pyodide's virtual filesystem
    pyodide.FS.writeFile("lawforge/constants.py", constants_code);
    pyodide.FS.writeFile("lawforge/deriver.py", deriver_code);
    pyodide.FS.writeFile("lawforge/__init__.py", ""); // Make it a package

    outputElement.textContent = "Environment ready. Please enter a postulate.";
    console.log("{PROJECT_NAME} engine is ready.");
    return pyodide;
}}

let pyodideReadyPromise = setupPyodide();

async function runDerivation() {{
    let pyodide = await pyodideReadyPromise;
    const postulate = postulateInput.value;

    if (!postulate) {{
        outputElement.textContent = "Please enter a postulate.";
        return;
    }}

    outputElement.textContent = "Deriving law...";
    deriveButton.disabled = true;

    try {{
        pyodide.globals.set("postulate_string", postulate);
        const pythonCode = `
from lawforge.deriver import derive_law_from_postulate
result = derive_law_from_postulate(postulate_string)
result
        `;
        let result = await pyodide.runPythonAsync(pythonCode);
        outputElement.textContent = result;
    }} catch (error) {{
        outputElement.textContent = `An error occurred:\\n${{error}}`;
        console.error(error);
    }} finally {{
        deriveButton.disabled = false;
    }}
}}

postulateInput.addEventListener("keyup", (event) => {{
    if (event.key === "Enter") {{
        event.preventDefault();
        deriveButton.click();
    }}
}});
"""

INIT_PY_CONTENT = "# LawForge: A Physics Law Discovery Engine"

CONSTANTS_PY_CONTENT = """
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
"""

DERIVER_PY_CONTENT = """
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
            f"Deriving physical law from postulate: {postulate_string}\\n\\n"
            f"1. Conceptual Postulate:\\n   {target_symbol} ~ {expression}\\n\\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\\n"
            f"   {sympy.pretty(dimensionless_eq, use_unicode=False)}\\n\\n"
            f"3. Solving for {target_symbol} to project into chosen coordinate system...\\n\\n"
            f"------------------------------------\\n"
            f"   RESULTING PHYSICAL LAW\\n"
            f"------------------------------------\\n"
            f"   {sympy.pretty(sympy.Eq(target_symbol, final_law), use_unicode=False)}\\n\\n"
            f"Note: 'k' represents a dimensionless constant (e.g., 1/2, 8*pi) from geometry or integration, which is not derived by this calculus."
        )
        return output.strip()

    except Exception as e:
        import traceback
        return f"ERROR: {{e}}\\n\\nTraceback:\\n{{traceback.format_exc()}}\\nPlease check your postulate format (e.g., 'E ~ m')."
"""

TEST_PY_CONTENT = """
import sys
import pytest

# Add the 'docs' directory to the python path to find the 'lawforge' module
sys.path.insert(0, 'docs')

from lawforge.deriver import derive_law_from_postulate

def test_einstein_derivation():
    result = derive_law_from_postulate("E ~ m")
    assert "E = k*c**2*m" in result.replace(" ", "")

def test_newton_gravity_derivation():
    result = derive_law_from_postulate("F ~ M1*M2/r**2")
    assert "F=k*G*M1*M2/r**2" in result.replace(" ", "")
    
# Add more tests here...
"""

# --- Main Scaffolding Logic ---

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(dedent(content).strip() + '\n')
    print(f"✓ Created {path}")

def main():
    print(f"--- Scaffolding {PROJECT_NAME} Project ---")

    # Root level files
    create_file('.gitignore', GITIGNORE_CONTENT)
    create_file('README.md', README_CONTENT)

    # Web application files (ALL INSIDE 'docs')
    create_file('docs/index.html', INDEX_HTML_CONTENT)
    create_file('docs/style.css', STYLE_CSS_CONTENT)
    create_file('docs/main.js', MAIN_JS_CONTENT)

    # Core Python package (ALSO INSIDE 'docs' for deployment)
    create_file('docs/lawforge/__init__.py', INIT_PY_CONTENT)
    create_file('docs/lawforge/constants.py', CONSTANTS_PY_CONTENT)
    create_file('docs/lawforge/deriver.py', DERIVER_PY_CONTENT)
    
    # Test files (at root level for local development)
    create_file('tests/test_deriver.py', TEST_PY_CONTENT)

    print("\n--- Scaffolding Complete! ---")
    print("\nThis script has created a self-contained web application in the '/docs' folder.")
    print("\nNext Steps:")
    print("1. Initialize a git repository: `git init`")
    print("2. Add and commit the files: `git add .` and `git commit -m 'Initial scaffold'`")
    print("3. Push to your new GitHub repository.")
    print("4. In your repository settings, go to 'Pages' and configure deployment from the 'main' branch and '/docs' folder.")
    print("5. Your interactive LawForge app will be live shortly!")

if __name__ == "__main__":
    main()
