import { getNotifications, deleteNotification} from './notificationService.js';

async function fetchNotifications() {
  const dropdownMenu = document.querySelector(".dropdown-menu");
   dropdownMenu.innerHTML = "";
  // Clear the dropdown menu and show a loading indicator
  dropdownMenu.innerHTML = `<li class="dropdown-item">Loading...</li>`;

  try {
    // Fetch notifications from the notification service
    const response = await getNotifications();

    // Access notifications from the API response
    const notifications = response?.user?.notifications || []; // Safely handle missing fields



    // Populate the dropdown menu
    if (notifications.length === 0) {
      dropdownMenu.innerHTML = `<li class="dropdown-item">No notifications</li>`;
    } else {
      dropdownMenu.innerHTML = ""; // Clear previous messages
      notifications.forEach((notification) => {
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
          await handleDeleteNotification(notification, listItem, notifications);
        });
      });
    }
  } catch (error) {
    console.error("Error fetching notifications:", error);

    // Display error message in the dropdown
    dropdownMenu.innerHTML = `<li class="dropdown-item text-danger">Failed to load notifications</li>`;
  }
}
async function handleDeleteNotification(notification, listItem, notifications) {
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

// Attach the function to the dropdown button's click event

// Manual dropdown toggle functionality
const dropdownToggle = document.getElementById("notificationDropdown");
const dropdownMenu = document.getElementById("dropdownMenu");

dropdownToggle.addEventListener("click", () => {
      fetchNotifications();

  // Toggle the display of the dropdown menu
  const isVisible = dropdownMenu.style.display === "block";
  dropdownMenu.style.display = isVisible ? "none" : "block";
});