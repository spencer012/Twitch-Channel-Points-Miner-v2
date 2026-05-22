# Channel Points WebSocket API

This document is the implementation contract for the local Channel Points module.
It is written so another agent can implement client integration without reading internal miner code.

## Version

- Protocol version: `1.0`
- Compatibility policy:
  - additive fields are allowed without breaking changes,
  - removing or renaming fields requires a protocol version bump.

## Transport

- Bind host/port/path are configured via:
  - `twitch_miner.channel_points(host, port, path)`.
- Default endpoint:
  - WebSocket: `ws://127.0.0.1:8765/channel-points/ws`
  - Health: `http://127.0.0.1:8765/health`
  - Test page: `http://127.0.0.1:8765/channel-points/test`
- Delivery:
  - best-effort while connected,
  - no replay after reconnect.
- Heartbeats:
  - transport-level ping/pong is handled by the server.

## Connection Lifecycle

1. Client opens websocket.
2. Server emits a `connected` message.
3. Client sends control actions (`subscribe`, `unsubscribe`, `replace_subscriptions`, `get_rewards`, `redeem`).
4. Server sends action result messages and event messages.
5. On disconnect, all subscriptions owned by that socket are removed automatically.

## Built-In Test Page

The server hosts a built-in single-streamer test UI on the same port:

- URL: `http://127.0.0.1:8765/channel-points/test`
- It connects to the websocket endpoint automatically.
- It supports:
  - connect/disconnect,
  - subscribe/unsubscribe for one streamer login,
  - `get_rewards` snapshot fetch,
  - `redeem` calls,
  - live event/response log display.

## Message Envelope

### Client -> Server

All client actions are JSON objects:

```json
{
  "action": "subscribe",
  "requestId": "req-123",
  "...": "action-specific fields"
}
```

- `action`: required string.
- `requestId`: optional string; echoed in responses and errors.

### Server -> Client

- Success/result messages use typed objects (for example `subscribed`, `rewards_snapshot`, `redeem_result`).
- Errors use:

```json
{
  "type": "error",
  "requestId": "req-123",
  "code": "invalid_payload",
  "message": "channels must be a list",
  "timestamp": "2026-03-19T12:00:00.000000+00:00"
}
```

## Actions and Schemas

## `subscribe`

Add channel subscriptions for the current websocket client.

Request:

```json
{
  "action": "subscribe",
  "requestId": "req-1",
  "channels": ["aquwa", "kokonuts"]
}
```

Response:

```json
{
  "type": "subscribed",
  "requestId": "req-1",
  "subscribed": [
    {"channelLogin": "aquwa", "channelId": "996756981"}
  ],
  "errors": [
    {"channelLogin": "bad_name", "code": "channel_lookup_failed"}
  ],
  "timestamp": "2026-03-19T12:00:00.000000+00:00"
}
```

Validation:

- `channels` is required and must be a list of strings.
- duplicate entries for the same socket are ignored.

## `unsubscribe`

Remove channel subscriptions for the current websocket client.

Request:

```json
{
  "action": "unsubscribe",
  "requestId": "req-2",
  "channels": ["aquwa"]
}
```

Response:

```json
{
  "type": "unsubscribed",
  "requestId": "req-2",
  "unsubscribed": [
    {"channelLogin": "aquwa", "channelId": "996756981"}
  ],
  "errors": [],
  "timestamp": "2026-03-19T12:00:00.000000+00:00"
}
```

## `replace_subscriptions`

Atomically replace the subscription set for this websocket.

Request:

```json
{
  "action": "replace_subscriptions",
  "requestId": "req-3",
  "channels": ["aquwa", "myfaceisausome"]
}
```

Response:

```json
{
  "type": "subscriptions_replaced",
  "requestId": "req-3",
  "channels": ["aquwa", "myfaceisausome"],
  "added": [{"channelLogin": "aquwa", "channelId": "996756981"}],
  "removed": ["oldchannel"],
  "errors": [],
  "timestamp": "2026-03-19T12:00:00.000000+00:00"
}
```

## `get_rewards`

Fetch the latest channel points rewards snapshot from Twitch.

Request:

```json
{
  "action": "get_rewards",
  "requestId": "req-4",
  "channelLogin": "aquwa"
}
```

Response:

```json
{
  "type": "rewards_snapshot",
  "requestId": "req-4",
  "channelLogin": "aquwa",
  "channelId": "996756981",
  "rewards": {
    "channelLogin": "aquwa",
    "channelId": "996756981",
    "balance": 41682,
    "availableClaim": null,
    "automaticRewards": [],
    "customRewards": []
  },
  "timestamp": "2026-03-19T12:00:00.000000+00:00"
}
```

## `redeem`

Redeem a custom reward through Twitch GraphQL `RedeemCustomReward`.

Request:

```json
{
  "action": "redeem",
  "requestId": "req-5",
  "channelLogin": "aquwa",
  "rewardId": "d8a02cee-13b6-4d5e-85f7-97e017fea31b",
  "title": "Hydrate",
  "cost": 500,
  "prompt": "Drink water",
  "transactionId": "optional-client-id"
}
```

Response:

```json
{
  "type": "redeem_result",
  "requestId": "req-5",
  "channelLogin": "aquwa",
  "channelId": "996756981",
  "result": {
    "ok": true,
    "transactionId": "optional-client-id",
    "error": null,
    "raw": {
      "error": null,
      "__typename": "RedeemCommunityPointsCustomRewardPayload"
    }
  },
  "timestamp": "2026-03-19T12:00:00.000000+00:00"
}
```

Validation:

- Required: `rewardId`, `title`, `cost`, and either `channelLogin` or `channelId`.
- `cost` must be numeric.

## Event Messages

Server emits best-effort event notifications:

- `reward_redeemed`
- `reward_updated`
- `points_spent`

Example:

```json
{
  "type": "event",
  "event": "reward_redeemed",
  "channelId": "996756981",
  "channelLogin": "aquwa",
  "timestamp": "2026-03-19T12:00:00.000000+00:00",
  "payload": {
    "topic": "community-points-channel-v1",
    "type": "reward-redeemed",
    "timestamp": "2026-03-19T11:59:59.000000+00:00",
    "data": {}
  }
}
```

## Error Codes

Current machine-readable error codes:

- `invalid_json`
- `invalid_payload`
- `unsupported_action`
- `invalid_channel_login`
- `channel_lookup_failed`
- `not_subscribed`
- `rewards_lookup_failed`
- `redeem_failed`

## Multi-Consumer and Ref Counting Rules

- Multiple local websocket consumers can subscribe to the same channel.
- The miner keeps one global ref count per channel.
- Upstream Twitch topic subscription is created when ref count transitions from `0 -> 1`.
- Upstream Twitch topic unsubscription is sent when ref count transitions from `1 -> 0`.
- Socket disconnect removes only that socket's subscriptions and decrements ref counts accordingly.

## State Machine

```text
Disconnected
  -> Connected (server sends "connected")
Connected
  -> Subscribed (after subscribe/replace_subscriptions)
Subscribed
  -> Connected (unsubscribe all)
Subscribed or Connected
  -> Disconnected (socket closed, server cleanup runs)
```

## Manual Single-Streamer Workflow

1. Start miner and channel points module:
   - call `twitch_miner.channel_points(host, port, path)` before `mine()`.
2. Open test page:
   - `http://127.0.0.1:8765/channel-points/test`.
3. Connect websocket from UI.
4. Enter streamer login and click `Subscribe`.
5. Click `Get Rewards` and confirm `rewards_snapshot` plus populated rewards table.
6. Pick a reward row (or enter reward fields manually), then click `Redeem`.
7. Confirm `redeem_result` and observe event log (`reward_redeemed`, `reward_updated`, `points_spent`, or `error`).
8. Click `Unsubscribe` or disconnect; server drops this socket's subscriptions automatically.

## UI-Driven Action Sequence

The expected request/response sequence from the test page:

1. `connected` (server -> client after open)
2. `subscribe` -> `subscribed`
3. `get_rewards` -> `rewards_snapshot`
4. `redeem` -> `redeem_result`
5. asynchronous `event` messages as Twitch PubSub updates arrive

## Security Notes

- This protocol is intended for local-trust environments.
- Do not expose this websocket endpoint directly to the public internet.
- OAuth credentials remain inside the miner process and are never accepted from client payloads.
- Clients should avoid sending sensitive user content in `prompt` unless needed.

## Implementation Checklist for Follow-Up Agent

- Implement websocket client reconnection with backoff.
- Always include `requestId` to correlate results/errors.
- Maintain local desired subscription set and issue `replace_subscriptions` after reconnect.
- Handle all error codes without crashing.
- Validate reward payloads before issuing `redeem`.
- Treat events as best-effort and idempotent where possible.
