document.addEventListener('DOMContentLoaded', function () {
    const statusBox = document.getElementById('status-box');
    const warningSound = document.getElementById('warning-sound');
    const alertSound = document.getElementById('alert-sound');
    let lastWarningCount = 0;

    // Set initial volumes
    warningSound.volume = 0.4;
    alertSound.volume = 0.7;

    function updateStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                // Update text
                statusBox.textContent = `Status: ${data.status}`;

                // Color indicator
                if (data.status === "Drowsy") {
                    statusBox.classList.add("danger");
                    statusBox.classList.remove("safe");
                } else {
                    statusBox.classList.remove("danger");
                    statusBox.classList.add("safe");
                }

                // Sound alert logic
                if (data.alert) {
                    if (alertSound.paused) {
                        alertSound.currentTime = 0;
                        alertSound.play();
                        warningSound.pause();
                        warningSound.currentTime = 0;
                    }
                } else {
                    alertSound.pause();
                    alertSound.currentTime = 0;

                    if (data.warnings > lastWarningCount) {
                        warningSound.currentTime = 0;
                        warningSound.play();
                    }
                }

                lastWarningCount = data.warnings;
            })
            .catch(error => {
                console.error("Error fetching status:", error);
                statusBox.textContent = "⚠ Connection Error";
                statusBox.classList.add("danger");
            });
    }

    setInterval(updateStatus, 1000);
});
