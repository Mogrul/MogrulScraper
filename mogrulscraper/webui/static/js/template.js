document.addEventListener("DOMContentLoaded", () => {
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
});