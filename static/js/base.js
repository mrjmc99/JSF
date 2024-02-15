function exportTableToCSV(tableId) {
    let table = document.getElementById(tableId);
    let rows = table.querySelectorAll("tr");
    let csv = [];

    // Retrieve the page title
    let title = document.querySelector("h2").innerText;

    // Generate the current timestamp
    let date = new Date();
    let timestamp = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + '_' + date.getHours() + '-' + date.getMinutes();

    // Combine both to create a filename
    let filename = title.replace(/\s+/g, '_').toLowerCase() + "_" + timestamp + ".csv";

    for (let i = 0; i < rows.length; i++) {
        let row = [], cols = rows[i].querySelectorAll("td, th");

        for (let j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }

        csv.push(row.join(","));
    }

    downloadCSV(csv.join("\n"), filename);
}

function downloadCSV(csv, filename) {
    let csvFile, downloadLink;

    csvFile = new Blob([csv], {type: "text/csv"});
    downloadLink = document.createElement("a");
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
    downloadLink.click();
}
