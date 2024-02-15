function createVariableInputs(variables) {
    const variableInputs = document.getElementById("variableInputs");

    // Access the array inside the variables object
    const variableArray = variables.variables || [];

    // Clear existing variable inputs
    variableInputs.innerHTML = "";
    variableArray.forEach(function(variable) {
        const label = document.createElement("label");
        label.setAttribute("for", variable.name);
        label.innerText = variable.name;

        const input = document.createElement("input");
        input.setAttribute("type", variable.type);
        input.setAttribute("name", variable.name);
        input.setAttribute("id", variable.name);

        variableInputs.appendChild(label);
        variableInputs.appendChild(input);
    });
}

function filterServersByQueryType(queryType) {
    const serverSelect = document.getElementById("server");
    const allOptions = serverSelect.querySelectorAll("option");
    let isCurrentSelectedServerValid = false;

    for (let option of allOptions) {
        if (option.getAttribute("data-type") !== queryType) {
            option.style.display = "none";  // Hide non-matching servers
        } else {
            option.style.display = "";  // Show matching servers
            if (option.value === serverSelect.value) {
                isCurrentSelectedServerValid = true;
            }
        }
    }

    // If the currently selected server is not valid for the query type, reset the server selection
    if (!isCurrentSelectedServerValid) {
        for (let option of allOptions) {
            if (option.getAttribute("data-type") === queryType) {
                serverSelect.value = option.value;  // Set the value to the first matching server
                break;
            }
        }
    }
}


document.addEventListener("DOMContentLoaded", function() {
    const querySelect = document.getElementById("query");
    const queryForm = document.getElementById("queryForm");

    // Function to handle query change
    function handleQueryChange() {
        const selectedQueryId = querySelect.value;
        const selectedQueryType = querySelect.options[querySelect.selectedIndex].getAttribute("data-querytype");
        const variables = JSON.parse(querySelect.options[querySelect.selectedIndex].getAttribute("data-variables"));

        queryForm.action = `/oraclequery/${selectedQueryId}/`;

        createVariableInputs(variables);
        filterServersByQueryType(selectedQueryType);
    }

    querySelect.addEventListener("change", handleQueryChange);

document.getElementById('queryForm').addEventListener('submit', function() {
    // Show the processing message
    document.getElementById('processing').style.display = 'block';

    // Start the timer
    let counter = 0;
    const timerElement = document.getElementById('timer');
    const timer = setInterval(function() {
        counter++;
        timerElement.textContent = counter;
    }, 1000);

    // Note: The timer will keep running until the page is reloaded with the query results.
});



    // Call the function once on page load
    handleQueryChange();
});
