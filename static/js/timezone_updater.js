    var seconds = 0;
    function startTimer() {
        document.getElementById("pleaseWaitMessage").style.display = "block";
        document.getElementById("countupTimer").style.display = "block";

        setInterval(function() {
            seconds++;
            document.getElementById("countupTimer").innerHTML = seconds + " seconds";
        }, 1000);
    }