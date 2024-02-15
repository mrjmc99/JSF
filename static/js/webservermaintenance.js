$(document).ready(function() {
    let startTime;
    let intervalId;

    function updateElapsedTime() {
        const currentTime = new Date();
        const elapsedTime = Math.floor((currentTime - startTime) / 1000);
        $(".progress-text").text("Time Elapsed: " + elapsedTime + " seconds");
    }

    $(".executeButton").click(function() {
        const csrftoken = getCookie('csrftoken');
        const buttonId = $(this).data("server");
        const commandName = $(this).data("command");
        const targetUrl = `execute-remote-command/${buttonId}/${commandName}/`;

        const processingMessageId = "processingMessage-" + buttonId;
        const outputId = "output-" + buttonId;

        // Clear previous output
        $("#" + outputId).html("");

        // Show processing message
        $("#" + processingMessageId).css("visibility", "visible").show();

        // Start timer
        startTime = new Date();
        intervalId = setInterval(updateElapsedTime, 1000);

        $.ajax({
            type: "POST",
            url: targetUrl,
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(data) {
                clearInterval(intervalId);
                $("#" + processingMessageId).hide();
                let formattedOutput = `
                    <strong>Output:</strong>
                    <pre>${data.output}</pre>
                `;
                $("#" + outputId).html(formattedOutput);
            },
            error: function(error) {
                clearInterval(intervalId);
                $("#" + processingMessageId).hide();
                $("#" + outputId).html("Error: " + error.responseText);
            }
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
// Handle the command-specific global button click
$(".executeAllForCommand").click(function() {
    const targetCommand = $(this).data("command");

    // Trigger the specific command for all servers
    $(".executeButton[data-command='" + targetCommand + "']").each(function() {
        $(this).trigger('click');
    });
});