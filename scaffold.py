import os
from textwrap import dedent

# --- Project Configuration ---
PROJECT_NAME = "LawForge"
YOUR_GITHUB_USERNAME = "BuckRogers1965" # Replace with your actual GitHub username

# --- File Content Definitions ---

# .gitignore
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

# docs/index.html
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
                Based on the principles of The Knowledge Pattern.
                Created by J. Rogers.
            </p>
            <p>
                <a href="https://github.com/{YOUR_GITHUB_USERNAME}/LawForge" target="_blank">View on GitHub</a>
            </p>
        </footer>
    </div>

    <!-- Load Pyodide and our JavaScript -->
    <script src="https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js"></script>
    <script src="main.js"></script>
</body>
</html>
"""

# docs/style.css
STYLE_CSS_CONTENT = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    background-color: #f4f7f6;
    color: #333;
    margin: 0;
    padding: 20px;
}
.container {
    max-width: 800px;
    margin: 0 auto;
    background-color: #fff;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
header {
    text-align: center;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 20px;
    margin-bottom: 20px;
}
h1 {
    color: #1a237e;
    margin: 0;
}
.subtitle {
    color: #555;
    font-style: italic;
}
.input-group {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}
#postulateInput {
    flex-grow: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 16px;
}
#deriveButton {
    padding: 10px 20px;
    background-color: #3949ab;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.3s;
}
#deriveButton:hover {
    background-color: #1a237e;
}
pre {
    background-color: #e8eaf6;
    padding: 15px;
    border-radius: 4px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: "Courier New", Courier, monospace;
}
code {
    font-family: inherit;
}
footer {
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
    font-size: 14px;
    color: #777;
}
a {
    color: #3949ab;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}
"""

# docs/main.js
MAIN_JS_CONTENT = f"""
const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

// Initialize Pyodide and load necessary packages
async function setupPyodide() {{
    outputElement.textContent = "Initializing Python environment (this may take a moment)...";
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("sympy");

    // Fetch and load our own Python modules
    const constantsPromise = fetch('../lawforge/constants.py').then(res => res.text());
    const deriverPromise = fetch('../lawforge/deriver.py').then(res => res.text());
    
    const [constants_code, deriver_code] = await Promise.all([constantsPromise, deriverPromise]);

    pyodide.runPython(constants_code);
    pyodide.runPython(deriver_code);

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
from deriver import derive_law_from_postulate
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

postulateInput.addEventListener("keyup", function(event) {{
    if (event.key === "Enter") {{
        event.preventDefault();
        deriveButton.click();
    }}
}});
"""

# lawforge/__init__.py
INIT_PY_CONTENT = "# LawForge: A Physics Law Discovery Engine"

# lawforge/constants.py
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
    'a_P': sqrt(c**7 / (h*G)),
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
    'v': 'v_P', # Special case: velocity is l_P / t_P = c
    'f': 'f_P', # Special case: frequency is 1 / t_P
}
"""

# lawforge/deriver.py
DERIVER_PY_CONTENT = """
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
            f"Deriving physical law from postulate: {postulate_string}\\n\\n"
            f"1. Conceptual Postulate:\\n   {target_symbol} ~ {expression}\\n\\n"
            f"2. Formulating Dimensionless Equation (Normalizing by Planck Units):\\n"
            f"   {sympy.pretty(dimensionless_eq, use_unicode=False)}\\n"
            f"3. Solving for {target_symbol} to project into chosen coordinate system...\\n\\n"
            f"------------------------------------\\n"
            f"   RESULTING PHYSICAL LAW\\n"
            f"------------------------------------\\n"
            f"   {sympy.pretty(sympy.Eq(target_symbol, final_law), use_unicode=False)}\\n\\n"
            f"Note: 'k' represents a dimensionless geometric constant (e.g., 1/2, 8*pi) not determined by this dimensional calculus."
        )
        return output.strip()

    except Exception as e:
        import traceback
        return f"ERROR: {{e}}\\n\\nTraceback:\\n{{traceback.format_exc()}}\\n\\nPlease check your postulate format (e.g., 'E ~ m')."
"""

# --- Main Scaffolding Logic ---
def create_file(path, content):
    """Creates a file with the given content, creating directories if needed."""
    # Get the directory part of the path
    directory = os.path.dirname(path)
    # Only try to create directories if the path actually has a directory part
    if directory:
        os.makedirs(directory, exist_ok=True)
    # Now, create the file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(dedent(content).strip())
    print(f"✓ Created {path}")

def main():
    """Main function to scaffold the entire project."""
    print(f"--- Scaffolding {PROJECT_NAME} Project ---")

    create_file('.gitignore', GITIGNORE_CONTENT)
    create_file('README.md', f"# {PROJECT_NAME}\n\nA Physics Law Discovery Engine.")
    create_file('docs/index.html', INDEX_HTML_CONTENT)
    create_file('docs/style.css', STYLE_CSS_CONTENT)
    create_file('docs/main.js', MAIN_JS_CONTENT)
    create_file('lawforge/__init__.py', INIT_PY_CONTENT)
    create_file('lawforge/constants.py', CONSTANTS_PY_CONTENT)
    create_file('lawforge/deriver.py', DERIVER_PY_CONTENT)
    
    print("\n--- Scaffolding Complete! ---")
    print("\nNext Steps:")
    print("1. Initialize a git repository: `git init`")
    print("2. Add and commit the files: `git add .` and `git commit -m 'Initial scaffold'`")
    print("3. Push to your GitHub repository.")
    print("4. In your repository settings, configure GitHub Pages to deploy from the '/docs' folder.")
    print("5. Your interactive LawForge app will be live shortly!")

if __name__ == "__main__":
    main()
