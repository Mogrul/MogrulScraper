const events = new EventSource(
    "/events"
);

events.onmessage = (event) => {
    const data = JSON.parse(
        event.data
    );

    switch (data.type) {
        case "download_add":
            addDownload(
                data.id,
                data.name,
                data.progress
            );

            break;

        case "download_progress":
            updateDownload(
                data.id,
                data.progress
            );

            break;

        case "download_complete":
            removeDownload(
                data.id
            );

            break;

        case "terminal":
            addTerminalMessage(
                data.message
            );

            break;

        default:
            console.warn(
                "Unknown event type:",
                data.type
            );
    }
};

events.onerror = (event) => {
    resetDownloads();

    if (events.readyState === EventSource.CONNECTING) {
        console.log("Reconnecting...");
    }

    else if (events.readyState === EventSource.CLOSED) {
        console.error("SSE connection closed.");
    }
}

const downloads = document.getElementById(
    "downloads"
);

const emptyDownloads = document.getElementById(
    "empty-downloads"
);

const downloadCount = document.getElementById(
    "download-count"
);

const terminal = document.getElementById(
    "terminal"
);

const playButton = document.getElementById(
    "play-button"
);

const pauseButton = document.getElementById(
    "pause-button"
);

const clearTerminalButton = document.getElementById(
    "clear-terminal"
);


function resetDownloads() {
    document
        .querySelectorAll(".download-item")
        .forEach(download => {
            download.remove();
        });
}

function updateDownloadCount() {
    const count = downloads.querySelectorAll(
        ".download-item"
    ).length;

    downloadCount.textContent = count;

    emptyDownloads.style.display =
        count === 0
            ? "flex"
            : "none";
}


function addDownload(
    id,
    name,
    progress = 0
) {
    const download = document.createElement(
        "div"
    );

    download.className = "download-item";

    download.dataset.id = id;

    download.innerHTML = `
        <div class="download-header">
            <span class="download-name">
                ${name}
            </span>

            <span class="download-progress-text">
                ${progress}%
            </span>
        </div>

        <div class="progress-bar">
            <div
                class="progress-bar-fill"
                style="width: ${progress}%"
            ></div>
        </div>
    `;

    downloads.appendChild(download);

    updateDownloadCount();
}


function updateDownload(
    id,
    progress
) {
    const download = downloads.querySelector(
        `[data-id="${id}"]`
    );

    if (!download) {
        return;
    }

    const progressText =
        download.querySelector(
            ".download-progress-text"
        );

    const progressBar =
        download.querySelector(
            ".progress-bar-fill"
        );

    progressText.textContent =
        `${progress}%`;

    progressBar.style.width =
        `${progress}%`;
}


function removeDownload(id) {
    const download = downloads.querySelector(
        `[data-id="${id}"]`
    );

    if (!download) {
        return;
    }

    download.remove();

    updateDownloadCount();
}


function addTerminalMessage(
    message
) {
    const line = document.createElement(
        "div"
    );

    line.className = "terminal-line";

    line.textContent = message;

    terminal.appendChild(line);

    terminal.scrollTop =
        terminal.scrollHeight;
}


clearTerminalButton.addEventListener(
    "click",
    () => {
        terminal.innerHTML = "";
    }
);


playButton.addEventListener(
    "click",
    async () => {
        playButton.disabled = true;

        pauseButton.disabled = false;

        await fetch(
            "/start",
            {
                method: "POST",
            }
        );
    }
);


pauseButton.addEventListener(
    "click",
    async () => {
        playButton.disabled = false;

        pauseButton.disabled = true;

        await fetch(
            "/stop",
            {
                method: "POST",
            }
        );
    }
);


updateDownloadCount();