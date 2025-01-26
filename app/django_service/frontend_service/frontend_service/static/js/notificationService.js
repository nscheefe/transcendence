import { executeQuery, executeMutation, executeSubscription,  } from './utils.js';

// Query for getting notifications
export const getNotifications = async (userId) => {
  const query = `
      query GetNotifications {
        user {
          notifications {
              id
            userId
            message
            read
            sentAt
          }
        }
  }
  `;

  const variables = { userId };
  return executeQuery(query, variables);
};


export const subscribeToNotifications = (onNotificationUpdate, onError) => {
  const subscriptionQuery = {
    query: `
      subscription NotificationsForUser {
        notificationsForUser {
          id
          userId
          message
          read
          sentAt
        }
      }
    `,
    variables: {},
    extensions: {},
    operationName: "NotificationsForUser",
  };
  executeSubscription(subscriptionQuery, onNotificationUpdate, onError);
};

// Mutation for creating a notification
export const createNotification = async (notificationData) => {
  const mutation = `
    mutation CreateNotification($notificationData: NotificationCreateInput!) {
      manageNotification(notificationData: { create: $notificationData }) {
        success
        message
      }
    }
  `;

  const variables = {
    notificationData,
  };
  return executeMutation(mutation, variables);
};

// Mutation for updating a notification
export const updateNotification = async (notificationData) => {
  const mutation = `
    mutation UpdateNotification($notificationData: NotificationUpdateInput!) {
      manageNotification(notificationData: { update: $notificationData }) {
        success
        message
      }
    }
  `;

  const variables = {
    notificationData,
  };
  return executeMutation(mutation, variables);
};

// Mutation for deleting a notification (if needed)
export const deleteNotification = async (notificationId) => {
  const mutation = `
    mutation DeleteNotification($notificationId: Int!) {
      manageNotification(notificationData: { delete: { id: $notificationId } }) {
        success
        message
      }
    }
  `;

  const variables = {
    notificationId,
  };
  return executeMutation(mutation, variables);
};
