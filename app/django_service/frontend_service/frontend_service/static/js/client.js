import { SubscriptionClient } from 'https://cdn.jsdelivr.net/npm/@httptoolkit/subscriptions-transport-ws@0.11.2/+esm';

// Set up the WebSocket client
const wsClient = new SubscriptionClient('wss://localhost/graphql/', {
    reconnect: true,
});

// Define the subscription query
const SUBSCRIPTION_QUERY = {
    variables: {},
    extensions: {},
    operationName: "Subscription",
    query: `subscription Subscription {
    chatRoomsForUser {
        id
    game_id
    name
    created_at
    users {
        id
      user_id
      chat_room_id
      joined_at
    }
    messages {
    id
    content
    sender_id
    chat_room_id
    timestamp
}
  }
}
`
}
    ;

// Execute the subscription
const subscription = wsClient.request(SUBSCRIPTION_QUERY).subscribe({
    next(data) {
        console.log('Subscription data:', data);
    },
    error(err) {
        console.error('Subscription error:', err);
    },
    complete() {
        console.log('Subscription complete');
    },
});

// To unsubscribe from the subscription
// subscription.unsubscribe();

