import { deleteNotification, subscribeToNotifications } from './notificationService.js';

function generateNotificationListItem(notification, dropdownMenu) {
  const listItem = document.createElement("li");
  listItem.className = "dropdown-item";
  listItem.id = `notification-${notification.id}`;

  listItem.innerHTML = `
    <strong>${notification.message}</strong><br />
    <small>${new Date(notification.sentAt).toLocaleString()}</small>
    <button
      class="btn btn-sm btn-danger ms-2 delete-notification"
      data-id="${notification.id}"
      aria-label="Close">
      X
    </button>
  `;

  dropdownMenu.appendChild(listItem);
  const deleteButton = listItem.querySelector(".delete-notification");
  deleteButton.addEventListener("click", async () => {
    await handleDeleteNotification(notification, listItem);
  });
}

async function handleDeleteNotification(notification, listItem) {
  try {
    // Send delete request to the server
    const deleteResponse = await deleteNotification(notification.id);

    if (deleteResponse && deleteResponse.manageNotification.success === true) {
      const listItem = document.getElementById(`notification-${notification.id}`);
      if (listItem) {
        listItem.remove();
      }
    } else {
      // Log the actual response
      console.error("Error deleting notification:", deleteResponse?.message ?? "Unknown server response");
    }
  } catch (error) {
    console.error("Error handling notification deletion:", error);
  }
}

const handleNewNotification = (notification) => {
  const dropdownMenu = document.querySelector(".dropdown-menu");

  // Remove "No notifications" message if it exists
  const noNotificationsItem = Array.from(dropdownMenu.children).find(
    (item) => item.textContent.trim() === "No notifications"
  );
  if (noNotificationsItem) {
    noNotificationsItem.remove();
  }

  generateNotificationListItem(notification, dropdownMenu);

  // Show the notification indicator
  const notificationIndicator = document.getElementById("notificationIndicator");

  // Store the state in local storage
  const latestNotificationTime = new Date(notification.sentAt).getTime();
  const storedNotificationTime = localStorage.getItem('latestNotificationTime');
  if (!storedNotificationTime || latestNotificationTime > storedNotificationTime) {
    localStorage.setItem('latestNotificationTime', latestNotificationTime);
    localStorage.setItem('hasUnreadNotifications', 'true');
    notificationIndicator.classList.remove('d-none');
  }
};

const initializeNotificationSubscription = async () => {
  try {
    subscribeToNotifications(
      (response) => {
        const notification = response.data.notificationsForUser;
        handleNewNotification(notification);
      },
      (err) => {
        console.error('Subscription error:', err);
      }
    );
  } catch (error) {
    console.error('Error subscribing to notifications:', error);
  }
};

// Manual dropdown toggle functionality
const dropdownToggle = document.getElementById("notificationDropdown");
const dropdownMenu = document.getElementById("dropdownMenu");

dropdownToggle.addEventListener("click", () => {

  // Hide the notification indicator when the dropdown is opened
  if (dropdownMenu.style.display === "block") {
    const notificationIndicator = document.getElementById("notificationIndicator");
    notificationIndicator.classList.add('d-none');

    // Update the state in local storage
    localStorage.setItem('hasUnreadNotifications', 'false');
  }
});

// Initialize the notification subscription
initializeNotificationSubscription();

// Check local storage for unread notifications on page load
document.addEventListener('DOMContentLoaded', () => {
  const hasUnreadNotifications = localStorage.getItem('hasUnreadNotifications') === 'true';
  if (hasUnreadNotifications) {
    const notificationIndicator = document.getElementById("notificationIndicator");
    notificationIndicator.classList.remove('d-none');
  }
});
