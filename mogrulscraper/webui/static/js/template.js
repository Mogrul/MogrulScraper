function setupNotifications() {
    const notifications = document.querySelectorAll(
        ".notification"
    );

    notifications.forEach((notification) => {
        const closeButton = notification.querySelector(
            ".notification-close"
        );

        const removeNotification = () => {
            notification.classList.add("removing");

            setTimeout(() => {
                notification.remove();
            }, 250);
        };

        closeButton.addEventListener(
            "click",
            removeNotification
        );

        setTimeout(
            removeNotification,
            5000
        );
    });
}


function showNotification(category, message) {
    const container = document.getElementById(
        "notifications"
    );

    const notification = document.createElement("div");

    notification.className =
        `notification notification-${category}`;

    notification.innerHTML = `
        <span class="notification-message">
            ${message}
        </span>

        <button
            class="notification-close"
            type="button"
            aria-label="Close notification"
        >
            &times;
        </button>
    `;

    container.appendChild(notification);

    // Apply the same close/timeout behaviour
    const closeButton = notification.querySelector(
        ".notification-close"
    );

    const removeNotification = () => {
        notification.classList.add("removing");

        setTimeout(() => {
            notification.remove();
        }, 250);
    };

    closeButton.addEventListener(
        "click",
        removeNotification
    );

    setTimeout(
        removeNotification,
        5000
    );
}


document.addEventListener(
    "DOMContentLoaded",
    setupNotifications
);
