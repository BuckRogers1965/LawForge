const postulateInput = document.getElementById('postulateInput');
const deriveButton = document.getElementById('deriveButton');
const outputElement = document.getElementById('output');

async function setupPyodide() {
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
    console.log("LawForge engine is ready.");
    return pyodide;
}

let pyodideReadyPromise = setupPyodide();

async function runDerivation() {
    let pyodide = await pyodideReadyPromise;
    const postulate = postulateInput.value;

    if (!postulate) {
        outputElement.textContent = "Please enter a postulate.";
        return;
    }

    outputElement.textContent = "Deriving law...";
    deriveButton.disabled = true;

    try {
        pyodide.globals.set("postulate_string", postulate);
        const pythonCode = `
from lawforge.deriver import derive_law_from_postulate
result = derive_law_from_postulate(postulate_string)
result
        `;
        let result = await pyodide.runPythonAsync(pythonCode);
        outputElement.textContent = result;
    } catch (error) {
        outputElement.textContent = `An error occurred:\n${error}`;
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
