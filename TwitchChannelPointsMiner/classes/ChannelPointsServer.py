import asyncio
import json
import logging
import threading
from datetime import datetime, timezone

from websockets.legacy.server import serve as ws_serve

logger = logging.getLogger(__name__)


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _normalize_login(login):
    return str(login or "").strip().lower()


def _build_test_page_html(ws_path):
    escaped_path = ws_path.replace("\\", "\\\\").replace("'", "\\'")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Channel Points Test UI</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 0;
      background: #0f1115;
      color: #e6e6e6;
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 16px;
    }}
    .row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }}
    .card {{
      background: #171a21;
      border: 1px solid #272b35;
      border-radius: 8px;
      padding: 12px;
    }}
    h1, h2 {{
      margin: 0 0 10px;
      font-size: 18px;
    }}
    h2 {{
      font-size: 16px;
    }}
    label {{
      display: block;
      margin-bottom: 6px;
      font-size: 13px;
      color: #bfc7d5;
    }}
    input, textarea, button {{
      width: 100%;
      box-sizing: border-box;
      border-radius: 6px;
      border: 1px solid #343a46;
      background: #0f1115;
      color: #e6e6e6;
      padding: 8px;
      margin-bottom: 8px;
    }}
    button {{
      cursor: pointer;
      background: #202533;
    }}
    .inline {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }}
    .inline-2 {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }}
    .status {{
      font-size: 13px;
      padding: 6px 8px;
      border-radius: 6px;
      display: inline-block;
      background: #292f3d;
      margin-bottom: 10px;
    }}
    .ok {{ color: #7ee787; }}
    .warn {{ color: #f2cc60; }}
    .bad {{ color: #ff7b72; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      margin-top: 8px;
    }}
    th, td {{
      border-bottom: 1px solid #272b35;
      text-align: left;
      padding: 6px;
      vertical-align: top;
    }}
    .log {{
      height: 260px;
      overflow-y: auto;
      background: #0f1115;
      border: 1px solid #2a2e3a;
      border-radius: 6px;
      padding: 8px;
      font-family: Consolas, monospace;
      font-size: 12px;
      white-space: pre-wrap;
    }}
    .muted {{ color: #9aa3b2; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Channel Points Test UI</h1>
    <p class="muted">Single-streamer test page on the same server port. Use this to exercise websocket actions and view events.</p>

    <div class="card">
      <div id="connStatus" class="status warn">Disconnected</div>
      <div class="inline-2">
        <input id="wsUrl" />
        <input id="streamerLogin" placeholder="streamer login (e.g. aquwa)" />
      </div>
      <div class="inline">
        <button id="connectBtn">Connect</button>
        <button id="disconnectBtn">Disconnect</button>
        <button id="clearLogBtn">Clear Log</button>
      </div>
      <div class="inline">
        <button id="subscribeBtn">Subscribe</button>
        <button id="unsubscribeBtn">Unsubscribe</button>
        <button id="getRewardsBtn">Get Rewards</button>
      </div>
    </div>

    <div class="row" style="margin-top: 12px;">
      <div class="card">
        <h2>Redeem Reward</h2>
        <input id="redeemRewardId" placeholder="rewardId" />
        <input id="redeemTitle" placeholder="title" />
        <div class="inline-2">
          <input id="redeemCost" type="number" min="1" placeholder="cost" />
          <input id="redeemTxId" placeholder="transactionId (optional)" />
        </div>
        <textarea id="redeemPrompt" rows="3" placeholder="prompt (optional)"></textarea>
        <button id="redeemBtn">Redeem</button>
      </div>

      <div class="card">
        <h2>Reward Snapshot</h2>
        <div id="snapshotMeta" class="muted">No snapshot loaded.</div>
        <table>
          <thead>
            <tr><th>Type</th><th>ID</th><th>Title</th><th>Cost</th><th>Status</th><th>Action</th></tr>
          </thead>
          <tbody id="rewardsBody"></tbody>
        </table>
      </div>
    </div>

    <div class="card" style="margin-top: 12px;">
      <h2>Events / Responses</h2>
      <div id="log" class="log"></div>
    </div>
  </div>

  <script>
    (function() {{
      const state = {{
        ws: null,
        requestCounter: 0,
        currentChannelLogin: "",
        currentChannelId: ""
      }};

      const wsUrlInput = document.getElementById("wsUrl");
      const streamerLoginInput = document.getElementById("streamerLogin");
      const connStatus = document.getElementById("connStatus");
      const logEl = document.getElementById("log");
      const rewardsBody = document.getElementById("rewardsBody");
      const snapshotMeta = document.getElementById("snapshotMeta");

      const redeemRewardId = document.getElementById("redeemRewardId");
      const redeemTitle = document.getElementById("redeemTitle");
      const redeemCost = document.getElementById("redeemCost");
      const redeemPrompt = document.getElementById("redeemPrompt");
      const redeemTxId = document.getElementById("redeemTxId");

      function mkRequestId(prefix) {{
        state.requestCounter += 1;
        return `${{prefix}}-${{Date.now()}}-${{state.requestCounter}}`;
      }}

      function log(kind, obj) {{
        const line = `[${{new Date().toISOString()}}] ${{kind}}\\n${{JSON.stringify(obj, null, 2)}}\\n\\n`;
        logEl.textContent = line + logEl.textContent;
      }}

      function setConnStatus(text, cssClass) {{
        connStatus.textContent = text;
        connStatus.className = "status " + cssClass;
      }}

      function getDefaultWsUrl() {{
        const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
        return `${{proto}}//${{window.location.host}}{escaped_path}`;
      }}

      function send(payload) {{
        if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {{
          log("client_error", {{message: "WebSocket is not connected"}});
          return;
        }}
        state.ws.send(JSON.stringify(payload));
        log("send", payload);
      }}

      function renderRewards(snapshot) {{
        const rewards = [];
        const custom = Array.isArray(snapshot.customRewards) ? snapshot.customRewards : [];
        const autoRewards = Array.isArray(snapshot.automaticRewards) ? snapshot.automaticRewards : [];

        for (const item of custom) {{
          const enabled = item.isEnabled === true ? "enabled" : "disabled";
          const paused = item.isPaused === true ? "paused" : "active";
          const stock = item.isInStock === true ? "in-stock" : "out-of-stock";
          rewards.push({{
            type: "custom",
            id: item.id || "",
            title: item.title || "",
            cost: item.cost ?? "",
            prompt: item.prompt || "",
            status: `${{enabled}} / ${{paused}} / ${{stock}}`
          }});
        }}

        for (const item of autoRewards) {{
          const enabled = item.isEnabled === false ? "disabled" : "enabled";
          rewards.push({{
            type: "automatic",
            id: item.id || "",
            title: item.title || item.type || "",
            cost: item.cost ?? "",
            prompt: "",
            status: enabled
          }});
        }}

        rewardsBody.innerHTML = "";
        if (rewards.length === 0) {{
          rewardsBody.innerHTML = "<tr><td colspan='6' class='muted'>No rewards found.</td></tr>";
          return;
        }}

        for (const reward of rewards) {{
          const tr = document.createElement("tr");
          const useBtn = document.createElement("button");
          useBtn.type = "button";
          useBtn.textContent = "Use";
          useBtn.style.margin = "0";
          useBtn.onclick = () => {{
            redeemRewardId.value = reward.id;
            redeemTitle.value = reward.title;
            if (reward.cost !== "") redeemCost.value = reward.cost;
            redeemPrompt.value = reward.prompt || "";
          }};

          tr.innerHTML = `<td>${{reward.type}}</td><td>${{reward.id}}</td><td>${{reward.title}}</td><td>${{reward.cost}}</td><td>${{reward.status}}</td>`;
          const actionCell = document.createElement("td");
          actionCell.appendChild(useBtn);
          tr.appendChild(actionCell);
          rewardsBody.appendChild(tr);
        }}
      }}

      function onMessage(evt) {{
        let msg = null;
        try {{
          msg = JSON.parse(evt.data);
        }} catch (err) {{
          log("recv_parse_error", {{raw: evt.data}});
          return;
        }}

        log("recv", msg);

        if (msg.type === "subscribed" && Array.isArray(msg.subscribed) && msg.subscribed[0]) {{
          state.currentChannelLogin = msg.subscribed[0].channelLogin || "";
          state.currentChannelId = msg.subscribed[0].channelId || "";
        }}

        if (msg.type === "rewards_snapshot" && msg.rewards) {{
          state.currentChannelLogin = msg.channelLogin || state.currentChannelLogin;
          state.currentChannelId = msg.channelId || state.currentChannelId;
          snapshotMeta.textContent = `Channel: ${{state.currentChannelLogin}} (${{state.currentChannelId}})`;
          renderRewards(msg.rewards);
        }}

        if (msg.type === "redeem_result" && msg.result && msg.result.ok === false) {{
          log("redeem_warning", msg);
        }}
      }}

      function connect() {{
        if (state.ws && state.ws.readyState === WebSocket.OPEN) {{
          return;
        }}
        const wsUrl = wsUrlInput.value.trim();
        state.ws = new WebSocket(wsUrl);
        setConnStatus("Connecting...", "warn");

        state.ws.onopen = () => setConnStatus("Connected", "ok");
        state.ws.onclose = () => setConnStatus("Disconnected", "bad");
        state.ws.onerror = () => setConnStatus("Error", "bad");
        state.ws.onmessage = onMessage;
      }}

      function disconnect() {{
        if (state.ws) {{
          state.ws.close();
        }}
      }}

      function requireLogin() {{
        const login = streamerLoginInput.value.trim().toLowerCase();
        if (!login) {{
          log("client_error", {{message: "Streamer login is required"}});
          return null;
        }}
        return login;
      }}

      document.getElementById("connectBtn").onclick = connect;
      document.getElementById("disconnectBtn").onclick = disconnect;
      document.getElementById("clearLogBtn").onclick = () => (logEl.textContent = "");

      document.getElementById("subscribeBtn").onclick = () => {{
        const login = requireLogin();
        if (!login) return;
        send({{
          action: "subscribe",
          requestId: mkRequestId("subscribe"),
          channels: [login]
        }});
      }};

      document.getElementById("unsubscribeBtn").onclick = () => {{
        const login = requireLogin();
        if (!login) return;
        send({{
          action: "unsubscribe",
          requestId: mkRequestId("unsubscribe"),
          channels: [login]
        }});
      }};

      document.getElementById("getRewardsBtn").onclick = () => {{
        const login = requireLogin();
        if (!login) return;
        send({{
          action: "get_rewards",
          requestId: mkRequestId("get-rewards"),
          channelLogin: login
        }});
      }};

      document.getElementById("redeemBtn").onclick = () => {{
        const login = requireLogin();
        if (!login) return;
        const rewardId = redeemRewardId.value.trim();
        const title = redeemTitle.value.trim();
        const cost = Number(redeemCost.value);
        if (!rewardId || !title || !Number.isFinite(cost) || cost <= 0) {{
          log("client_error", {{message: "Redeem requires rewardId, title, and positive cost"}});
          return;
        }}
        send({{
          action: "redeem",
          requestId: mkRequestId("redeem"),
          channelLogin: login,
          rewardId,
          title,
          cost,
          prompt: redeemPrompt.value || "",
          transactionId: redeemTxId.value.trim() || undefined
        }});
      }};

      wsUrlInput.value = getDefaultWsUrl();
      setConnStatus("Disconnected", "bad");
    }})();
  </script>
</body>
</html>"""


class ChannelPointsServer(threading.Thread):
    def __init__(
        self,
        twitch,
        ws_pool_getter,
        host="127.0.0.1",
        port=8765,
        path="/channel-points/ws",
    ):
        super(ChannelPointsServer, self).__init__()
        self.twitch = twitch
        self.ws_pool_getter = ws_pool_getter
        self.host = host
        self.port = port
        self.path = path
        self.test_path = "/channel-points/test"

        self._lock = threading.RLock()
        self._loop = None
        self._server = None
        self._running = True

        self._ws_pool = None
        self._clients = set()
        self._client_subscriptions = {}
        self._channel_states = {}
        self._channel_login_by_id = {}

    def bind_ws_pool(self, ws_pool):
        with self._lock:
            self._ws_pool = ws_pool
            if ws_pool is None:
                return

            ws_pool.set_channel_points_dispatcher(self.dispatch_twitch_event)
            channel_ids = [
                state["channel_id"]
                for state in self._channel_states.values()
                if state["count"] > 0
            ]

        for channel_id in channel_ids:
            try:
                ws_pool.subscribe_channel_points_channel(channel_id)
            except Exception:
                logger.error(
                    f"Unable to subscribe channel {channel_id} after ws_pool bind",
                    exc_info=True,
                )

    def _get_ws_pool(self):
        ws_pool = self._ws_pool
        if ws_pool is not None:
            return ws_pool

        getter = self.ws_pool_getter
        if getter is None:
            return None
        try:
            ws_pool = getter()
        except Exception:
            ws_pool = None

        if ws_pool is not None:
            self.bind_ws_pool(ws_pool)
        return ws_pool

    def dispatch_twitch_event(self, event_name, payload):
        if self._loop is None:
            return

        channel_id = str(payload.get("channel_id", ""))
        with self._lock:
            channel_login = self._channel_login_by_id.get(channel_id)

        event_payload = {
            "type": "event",
            "event": event_name,
            "channelId": channel_id,
            "channelLogin": channel_login,
            "timestamp": _utc_now(),
            "payload": payload,
        }

        future = asyncio.run_coroutine_threadsafe(
            self._broadcast_event(event_payload, channel_login, channel_id),
            self._loop,
        )
        try:
            future.result(timeout=2)
        except Exception:
            logger.debug("Event dispatch timeout or failure", exc_info=True)

    async def _broadcast_event(self, event_payload, channel_login, channel_id):
        dead_clients = []
        for ws in list(self._clients):
            subscriptions = self._client_subscriptions.get(ws, set())
            should_send = False

            if channel_login is not None and channel_login in subscriptions:
                should_send = True
            elif channel_id:
                for login in subscriptions:
                    state = self._channel_states.get(login)
                    if state and str(state["channel_id"]) == str(channel_id):
                        should_send = True
                        break

            if not should_send:
                continue

            try:
                await ws.send(json.dumps(event_payload))
            except Exception:
                dead_clients.append(ws)

        for ws in dead_clients:
            await self._cleanup_client(ws)

    async def _send(self, ws, payload):
        await ws.send(json.dumps(payload))

    async def _send_error(self, ws, request_id, code, message):
        await self._send(
            ws,
            {
                "type": "error",
                "requestId": request_id,
                "code": code,
                "message": message,
                "timestamp": _utc_now(),
            },
        )

    async def _resolve_channel_id(self, channel_login):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.twitch.get_channel_id, channel_login)

    async def _resolve_or_get_channel_id(self, channel_login):
        with self._lock:
            state = self._channel_states.get(channel_login)
            if state is not None:
                return str(state["channel_id"])

        channel_id = str(await self._resolve_channel_id(channel_login))
        with self._lock:
            if channel_login not in self._channel_states:
                self._channel_states[channel_login] = {"channel_id": channel_id, "count": 0}
            self._channel_login_by_id[channel_id] = channel_login
        return channel_id

    async def _subscribe_login(self, channel_login):
        channel_login = _normalize_login(channel_login)
        if not channel_login:
            return None, "invalid_channel_login"

        try:
            channel_id = await self._resolve_or_get_channel_id(channel_login)
        except Exception:
            return None, "channel_lookup_failed"

        should_subscribe_upstream = False
        with self._lock:
            state = self._channel_states[channel_login]
            state["count"] += 1
            if state["count"] == 1:
                should_subscribe_upstream = True

        if should_subscribe_upstream:
            ws_pool = self._get_ws_pool()
            if ws_pool is not None:
                try:
                    ws_pool.subscribe_channel_points_channel(channel_id)
                except Exception:
                    logger.error(
                        f"Unable to subscribe upstream for {channel_login}",
                        exc_info=True,
                    )

        return {"channelLogin": channel_login, "channelId": channel_id}, None

    async def _unsubscribe_login(self, channel_login):
        channel_login = _normalize_login(channel_login)
        if not channel_login:
            return None, "invalid_channel_login"

        channel_id = None
        should_unsubscribe_upstream = False
        with self._lock:
            state = self._channel_states.get(channel_login)
            if state is None or state["count"] <= 0:
                return None, "not_subscribed"
            state["count"] -= 1
            channel_id = str(state["channel_id"])
            if state["count"] == 0:
                should_unsubscribe_upstream = True

        if should_unsubscribe_upstream:
            ws_pool = self._get_ws_pool()
            if ws_pool is not None:
                try:
                    ws_pool.unsubscribe_channel_points_channel(channel_id)
                except Exception:
                    logger.error(
                        f"Unable to unsubscribe upstream for {channel_login}",
                        exc_info=True,
                    )

        return {"channelLogin": channel_login, "channelId": channel_id}, None

    async def _cleanup_client(self, ws):
        subscriptions = self._client_subscriptions.pop(ws, set())
        if ws in self._clients:
            self._clients.remove(ws)

        for channel_login in subscriptions:
            await self._unsubscribe_login(channel_login)

    async def _handle_subscribe(self, ws, payload):
        request_id = payload.get("requestId")
        channels = payload.get("channels", [])
        if not isinstance(channels, list):
            await self._send_error(ws, request_id, "invalid_payload", "channels must be a list")
            return

        ws_subscriptions = self._client_subscriptions.setdefault(ws, set())
        subscribed = []
        errors = []
        for raw_login in channels:
            login = _normalize_login(raw_login)
            if not login:
                errors.append({"channelLogin": raw_login, "code": "invalid_channel_login"})
                continue
            if login in ws_subscriptions:
                continue

            result, err = await self._subscribe_login(login)
            if err is not None:
                errors.append({"channelLogin": login, "code": err})
                continue

            ws_subscriptions.add(login)
            subscribed.append(result)

        await self._send(
            ws,
            {
                "type": "subscribed",
                "requestId": request_id,
                "subscribed": subscribed,
                "errors": errors,
                "timestamp": _utc_now(),
            },
        )

    async def _handle_unsubscribe(self, ws, payload):
        request_id = payload.get("requestId")
        channels = payload.get("channels", [])
        if not isinstance(channels, list):
            await self._send_error(ws, request_id, "invalid_payload", "channels must be a list")
            return

        ws_subscriptions = self._client_subscriptions.setdefault(ws, set())
        unsubscribed = []
        errors = []
        for raw_login in channels:
            login = _normalize_login(raw_login)
            if not login:
                errors.append({"channelLogin": raw_login, "code": "invalid_channel_login"})
                continue
            if login not in ws_subscriptions:
                errors.append({"channelLogin": login, "code": "not_subscribed"})
                continue

            result, err = await self._unsubscribe_login(login)
            if err is not None:
                errors.append({"channelLogin": login, "code": err})
                continue

            ws_subscriptions.remove(login)
            unsubscribed.append(result)

        await self._send(
            ws,
            {
                "type": "unsubscribed",
                "requestId": request_id,
                "unsubscribed": unsubscribed,
                "errors": errors,
                "timestamp": _utc_now(),
            },
        )

    async def _handle_replace_subscriptions(self, ws, payload):
        request_id = payload.get("requestId")
        channels = payload.get("channels", [])
        if not isinstance(channels, list):
            await self._send_error(ws, request_id, "invalid_payload", "channels must be a list")
            return

        target = set(_normalize_login(item) for item in channels if _normalize_login(item))
        current = set(self._client_subscriptions.setdefault(ws, set()))

        to_remove = sorted(current - target)
        to_add = sorted(target - current)

        for login in to_remove:
            _, _ = await self._unsubscribe_login(login)
            self._client_subscriptions[ws].discard(login)

        added = []
        errors = []
        for login in to_add:
            result, err = await self._subscribe_login(login)
            if err is not None:
                errors.append({"channelLogin": login, "code": err})
                continue
            self._client_subscriptions[ws].add(login)
            added.append(result)

        await self._send(
            ws,
            {
                "type": "subscriptions_replaced",
                "requestId": request_id,
                "channels": sorted(self._client_subscriptions[ws]),
                "added": added,
                "removed": to_remove,
                "errors": errors,
                "timestamp": _utc_now(),
            },
        )

    async def _handle_get_rewards(self, ws, payload):
        request_id = payload.get("requestId")
        channel_login = _normalize_login(payload.get("channelLogin"))
        if not channel_login:
            await self._send_error(ws, request_id, "invalid_payload", "channelLogin is required")
            return

        loop = asyncio.get_running_loop()
        try:
            rewards = await loop.run_in_executor(
                None, self.twitch.get_channel_rewards_context, channel_login
            )
        except Exception:
            await self._send_error(
                ws, request_id, "rewards_lookup_failed", "Unable to fetch rewards for channel"
            )
            return

        await self._send(
            ws,
            {
                "type": "rewards_snapshot",
                "requestId": request_id,
                "channelLogin": channel_login,
                "channelId": str(rewards.get("channelId", "")),
                "rewards": rewards,
                "timestamp": _utc_now(),
            },
        )

    async def _handle_redeem(self, ws, payload):
        request_id = payload.get("requestId")
        channel_login = _normalize_login(payload.get("channelLogin"))
        channel_id = str(payload.get("channelId", "")).strip()
        reward_id = payload.get("rewardId")
        title = payload.get("title")
        cost = payload.get("cost")
        prompt = payload.get("prompt")
        transaction_id = payload.get("transactionId")

        if not reward_id or title is None or cost is None:
            await self._send_error(
                ws,
                request_id,
                "invalid_payload",
                "rewardId, title and cost are required",
            )
            return

        if not channel_id:
            if not channel_login:
                await self._send_error(
                    ws,
                    request_id,
                    "invalid_payload",
                    "channelLogin or channelId is required",
                )
                return
            try:
                channel_id = await self._resolve_or_get_channel_id(channel_login)
            except Exception:
                await self._send_error(
                    ws,
                    request_id,
                    "channel_lookup_failed",
                    "Unable to resolve channelId from channelLogin",
                )
                return

        if not str(cost).strip().isdigit():
            await self._send_error(
                ws,
                request_id,
                "invalid_payload",
                "cost must be a positive integer",
            )
            return

        loop = asyncio.get_running_loop()
        redeem_payload = {
            "reward_id": reward_id,
            "title": title,
            "cost": int(cost),
            "prompt": prompt or "",
            "pricing_type": payload.get("pricingType", "POINTS"),
        }
        try:
            result = await loop.run_in_executor(
                None,
                self.twitch.redeem_custom_reward,
                channel_id,
                redeem_payload,
                transaction_id,
            )
        except Exception:
            await self._send_error(ws, request_id, "redeem_failed", "Unable to redeem reward")
            return

        message = {
            "type": "redeem_result",
            "requestId": request_id,
            "channelLogin": channel_login or self._channel_login_by_id.get(str(channel_id)),
            "channelId": str(channel_id),
            "result": result,
            "timestamp": _utc_now(),
        }
        await self._send(ws, message)

    async def _handle_message(self, ws, raw_message):
        try:
            payload = json.loads(raw_message)
        except Exception:
            await self._send_error(ws, None, "invalid_json", "Message body must be valid JSON")
            return

        if not isinstance(payload, dict):
            await self._send_error(ws, None, "invalid_payload", "Message body must be an object")
            return

        action = payload.get("action")
        if action == "subscribe":
            await self._handle_subscribe(ws, payload)
        elif action == "unsubscribe":
            await self._handle_unsubscribe(ws, payload)
        elif action == "replace_subscriptions":
            await self._handle_replace_subscriptions(ws, payload)
        elif action == "get_rewards":
            await self._handle_get_rewards(ws, payload)
        elif action == "redeem":
            await self._handle_redeem(ws, payload)
        else:
            await self._send_error(
                ws,
                payload.get("requestId"),
                "unsupported_action",
                f"Unsupported action '{action}'",
            )

    async def _ws_handler(self, ws, path):
        if path != self.path:
            await ws.close(code=1008, reason="Invalid websocket path")
            return

        self._clients.add(ws)
        self._client_subscriptions[ws] = set()
        await self._send(
            ws,
            {
                "type": "connected",
                "timestamp": _utc_now(),
                "path": self.path,
                "testPagePath": self.test_path,
                "actions": [
                    "subscribe",
                    "unsubscribe",
                    "replace_subscriptions",
                    "get_rewards",
                    "redeem",
                ],
            },
        )

        try:
            async for raw_message in ws:
                await self._handle_message(ws, raw_message)
        finally:
            await self._cleanup_client(ws)

    async def _process_request(self, path, request_headers):
        if path == "/health":
            with self._lock:
                payload = {
                    "status": "ok",
                    "timestamp": _utc_now(),
                    "websocketPath": self.path,
                    "connectedClients": len(self._clients),
                    "activeChannels": len(
                        [k for k, state in self._channel_states.items() if state["count"] > 0]
                    ),
                    "wsPoolReady": self._get_ws_pool() is not None,
                }
            body = json.dumps(payload).encode("utf-8")
            headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(body))),
            ]
            return (200, headers, body)

        if path == self.test_path:
            body = _build_test_page_html(self.path).encode("utf-8")
            headers = [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(body))),
            ]
            return (200, headers, body)

        if path != self.path:
            body = b"Not found"
            headers = [
                ("Content-Type", "text/plain"),
                ("Content-Length", str(len(body))),
            ]
            return (404, headers, body)

        return None

    def end(self):
        self._running = False
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def run(self):
        logger.info(
            f"Channel points server running on ws://{self.host}:{self.port}{self.path}",
            extra={"emoji": ":satellite:"},
        )
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._server = self._loop.run_until_complete(
            ws_serve(
                self._ws_handler,
                self.host,
                self.port,
                ping_interval=25,
                ping_timeout=20,
                process_request=self._process_request,
            )
        )

        try:
            self._loop.run_forever()
        finally:
            self._server.close()
            self._loop.run_until_complete(self._server.wait_closed())
            self._loop.close()
