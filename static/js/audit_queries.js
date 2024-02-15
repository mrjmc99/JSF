function displayVariables() {
    console.log("onChange started");

    const querySelect = document.getElementById("querySelect");
    let selectedQuery = querySelect.options[querySelect.selectedIndex];
    let variablesString = selectedQuery.getAttribute("data-variables");

    //console.log(variablesString);

    // Replace single quotes with double quotes for valid JSON format
    variablesString = variablesString.replace(/'/g, '"');

    const variables = JSON.parse(variablesString).variables;
    createVariableInputs(variables);

    console.log("onChange completed");
}


function executeSelectedQuery() {
    const querySelect = document.getElementById("querySelect");
    const selectedQueryId = querySelect.value;

    // Create a URL with the selected query id
    const url = `/audit_queries/execute/${selectedQueryId}/?`;

    // Serialize form inputs as query parameters
    const inputs = document.querySelectorAll("#variablesContainer input");
    const params = Array.from(inputs).map(input => {
        return encodeURIComponent(input.name) + "=" + encodeURIComponent(input.value);
    }).join("&");

    // Redirect to the constructed URL
    window.location.href = url + params;
}

// This function is called when the page is loaded
document.addEventListener("DOMContentLoaded", function() {
    const querySelect = document.getElementById("querySelect");
    querySelect.addEventListener("change", displayVariables);

    // Display variables for the initially selected query
    displayVariables();
});

function createVariableInputs(variables) {
    const variableInputs = document.getElementById("variablesContainer");

    // Clear existing variable inputs
    variableInputs.innerHTML = "";
    variables.forEach(function(variable) {
        const label = document.createElement("label");
        label.setAttribute("for", variable.name);
        label.innerText = variable.label;  // Use the label property for display

        const input = document.createElement("input");
        input.setAttribute("type", variable.type === 'date' ? 'text' : variable.type);  // If it's a date, use a text input for now
        input.setAttribute("name", variable.name);
        input.setAttribute("id", variable.name);
        input.placeholder = variable.label;

        variableInputs.appendChild(label);
        variableInputs.appendChild(input);
    });
}