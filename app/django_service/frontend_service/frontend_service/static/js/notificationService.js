import { executeQuery, executeMutation, gql } from './utils.js';

// Query for getting notifications
export const getNotifications = async (userId) => {
  const query = gql`
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

// Mutation for creating a notification
export const createNotification = async (notificationData) => {
  const mutation = gql`
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
  const mutation = gql`
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
  const mutation = gql`
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