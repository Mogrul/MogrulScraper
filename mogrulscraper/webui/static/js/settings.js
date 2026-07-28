const loadHistoryButton = document.getElementById(
    "load-history-button"
);

const urlsTextArea = document.getElementById(
    "urls"
);

loadHistoryButton.addEventListener(
    "click",
    async () => {
        const response = await fetch("/api/history");

        if (!response.ok) {
            return;
        }

        const data = await response.json();

        if (data.message) {
            showNotification(
                data.category,
                data.message
            );

            return;
        }

        urlsTextArea.value = data.urls.join("\n");
    }
);