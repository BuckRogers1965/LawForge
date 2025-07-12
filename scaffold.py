import os
from textwrap import dedent, indent

# --- Project Configuration ---
PROJECT_NAME = "LawForge"
YOUR_GITHUB_USERNAME = "BuckRogers1965"

# --- File Content Definitions ---
# This section defines the content for every file the script will create.

# --- ROOT-LEVEL FILES ---

GITIGNORE_CONTENT = """
# Python build artifacts
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
dist/
*.egg-info/

# Virtual environments
env/
venv/
.venv/

# IDE and editor files
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
"""

# --- INLINED PYTHON MODULES (for JavaScript) ---

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
# Note: constants are loaded from the same global scope in Pyodide, so no local import needed.

def parse_postulate(postulate_string):
    if '~' not in postulate_string:
        raise ValueError("Postulate must contain '~' to separate sides.")
    target_str, expr_str = [s.strip() for s in postulate_string.split('~')]
    target_symbol = sympy.Symbol(target_str)
    
    transformations = (standard_transformations + (implicit_multiplication_application,))
    local_symbols = {str(s): s for s in [sympy.Symbol('M1'), sympy.Symbol('M2'), sympy.Symbol('r_s')]}
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
            
            if planck_key == 'v_P':
                subs_dict[sym] = sym / sympy.Symbol('c')
            elif planck_key == 'f_P':
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
            f"Note: 'k' represents a dimensionless geometric constant (e.g., 1/2, 8*pi) not derived by this calculus."
        )
        return output.strip()

    except Exception as e:
        import traceback
        return f"ERROR: {{e}}\\n\\nTraceback:\\n{{traceback.format_exc()}}\\nPlease check your postulate format (e.g., 'E ~ m')."
"""

# --- WEB APPLICATION FILES (in /docs) ---

MAIN_JS_CONTENT = f"""
const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

// Inlining Python code to avoid all fetch/filesystem errors
const constants_py = `{indent(CONSTANTS_PY_CONTENT, ' ' * 0)}`;
const deriver_py = `{indent(DERIVER_PY_CONTENT, ' ' * 0)}`;

async function setupPyodide() {{
    outputElement.textContent = "Initializing Python environment...";
    try {{
        let pyodide = await loadPyodide();
        outputElement.textContent = "Loading scientific libraries (SymPy)...";
        await pyodide.loadPackage("sympy");

        outputElement.textContent = "Loading LawForge engine...";
        pyodide.runPython(constants_py);
        pyodide.runPython(deriver_py);

        outputElement.textContent = "Environment ready. Please enter a postulate.";
        console.log("{PROJECT_NAME} engine is ready.");
        return pyodide;
    }} catch (error) {{
        outputElement.textContent = `CRITICAL ERROR during initialization: ${{error}}`;
        console.error("Initialization failed:", error);
    }}
}}

let pyodideReadyPromise = setupPyodide();

async function runDerivation() {{
    deriveButton.disabled = true;
    outputElement.textContent = "Waiting for environment...";
    let pyodide = await pyodideReadyPromise;
    if (!pyodide) {{
        outputElement.textContent = "Initialization failed. Please refresh the page.";
        return;
    }}

    const postulate = postulateInput.value;
    if (!postulate) {{
        outputElement.textContent = "Please enter a postulate.";
        deriveButton.disabled = false;
        return;
    }}

    outputElement.textContent = "Deriving law...";

    try {{
        pyodide.globals.set("postulate_string", postulate);
        const pythonCode = `result = derive_law_from_postulate(postulate_string)`;
        await pyodide.runPythonAsync(pythonCode);
        const result = pyodide.globals.get("result");
        outputElement.textContent = result;
    }} catch (error) {{
        outputElement.textContent = `An error occurred during derivation:\\n${{error}}`;
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

    # The entire application will now live self-contained in the '/docs' folder.
    create_file('docs/index.html', INDEX_HTML_CONTENT)
    create_file('docs/style.css', STYLE_CSS_CONTENT)
    create_file('docs/main.js', MAIN_JS_CONTENT)
    
    # Add a .gitignore and a README at the root.
    create_file('.gitignore', GITIGNORE_CONTENT)
    create_file('README.md', README_CONTENT)

    print("\n--- Scaffolding Complete! ---")
    print("\nThis script has created a 100% self-contained web application in the '/docs' folder.")
    print("All Python code is now inlined in 'docs/main.js' to prevent file loading errors.")
    print("\nNext Steps:")
    print("1. Initialize git: `git init`")
    print("2. Add and commit all files: `git add .` and `git commit -m 'Initial scaffold'`")
    print("3. Push to your new, empty GitHub repository.")
    print("4. In repository settings -> Pages, deploy from the 'main' branch and '/docs' folder.")
    print("5. Your interactive LawForge app will be live and will work correctly.")

if __name__ == "__main__":
    main()
