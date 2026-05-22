# Twitch Channel Points Miner (Armi1014 Fork)

A **reliability-first fork** of `Twitch-Channel-Points-Miner-v2`.

Built for people who want:
- **better watch streak reliability**
- **cleaner favorite / priority behavior**
- **faster startup in real use**
- **less transient Twitch/API/network log noise**

If upstream mostly works for you but occasionally behaves weirdly, this fork is meant to be the **more practical, more stable version**.
It also aims to be the **faster fork in day-to-day use**, especially during startup and early channel refreshes.

> Not affiliated with Twitch. Use at your own risk.

## Quick Start

If you are coming from upstream, one of the first things you should notice is that this fork is tuned to spend less time stuck in slow startup behavior before it becomes usable.

Read more about the channel points [here](https://help.twitch.tv/s/article/channel-points-guide).

# README Contents
1. 🤝 [Community](#community)
2. 🚀 [Main differences from the original repository](#main-differences-from-the-original-repository)
3. 🧾 [Logs feature](#logs-feature)
    - [Full logs](#full-logs)
    - [Less logs](#less-logs)
    - [Final report](#final-report)
4. 🧐 [How to use](#how-to-use)
    - [Cloning](#by-cloning-the-repository)
    - [Docker](#docker)
    	- [Docker Hub](#docker-hub)
		- [Portainer](#portainer)
    - [Replit](#replit)
    - [Limits](#limits)
5. 🔧 [Settings](#settings)
    - [LoggerSettings](#loggersettings)
    - [StreamerSettings](#streamersettings)
    - [BetSettings](#betsettings)
        - [Bet strategy](#bet-strategy)
    - [FilterCondition](#filtercondition)
        - [Example](#example)
6. 📈 [Analytics](#analytics)
7. 🔌 [Channel Points WebSocket API](#channel-points-websocket-api)
8. 🍪 [Migrating from an old repository (the original one)](#migrating-from-an-old-repository-the-original-one)
9. 🪟 [Windows](#windows)
10. 📱 [Termux](#termux)
11. ⚠️ [Disclaimer](#disclaimer)


## Community
If you want to help with this project, please leave a star 🌟 and share it with your friends! 😎

If you want to offer me a coffee, I would be grateful! ❤️

|                                                                                                                                                                                                                                                                                                           |                                               |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
|<a href="https://bitcoin.org" target="_blank"><img src="https://dynamic-assets.coinbase.com/e785e0181f1a23a30d9476038d9be91e9f6c63959b538eabbc51a1abc8898940383291eede695c3b8dfaa1829a9b57f5a2d0a16b0523580346c6b8fab67af14b/asset_icons/b57ac673f06a4b0338a596817eb0a50ce16e2059f327dc117744449a47915cb2.png" alt="Donate BTC" height="16" width="16"></a>|`bc1qq49mvgda2zw4f9kta0a85xztwuxewqwac5eckd` _(<a href="https://bitcoin.org" target="_blank">BTC</a>)_|
|<a href="https://dogechain.info" target="_blank"><img src="https://dynamic-assets.coinbase.com/3803f30367bb3972e192cd3fdd2230cd37e6d468eab12575a859229b20f12ff9c994d2c86ccd7bf9bc258e9bd5e46c5254283182f70caf4bd02cc4f8e3890d82/asset_icons/1597d628dd19b7885433a2ac2d7de6ad196c519aeab4bfe679706aacbf1df78a.png" alt="Donate DOGE" height="16" width="16"></a>|`DAKzncwKkpfPCm1xVU7u2pConpXwX7HS3D` _(<a href="https://dogechain.info" target="_blank">DOGE</a>)_|
|<a href="https://www.donationalerts.com/r/rdavydov" target="_blank"><img src="https://www.donationalerts.com/static/donations/dist/favicon.ico" alt="Donate via DonationAlerts" height="16" width="16"></a>|https://www.donationalerts.com/r/rdavydov|
|<a href="https://boosty.to/rdavydov/donate" target="_blank"><img src="https://static.boosty.to/static/favicon.png?v=11" alt="Donate via Boosty" height="16" width="16"></a>|https://boosty.to/rdavydov/donate|

If you have any issues or you want to contribute, you are welcome! But please read the [CONTRIBUTING.md](https://github.com/rdavydov/Twitch-Channel-Points-Miner-v2/blob/master/CONTRIBUTING.md) file.

## Main differences from the original repository:

- Improved logging: emojis, colors, files and much more ✔️
- Final report with all the data ✔️
- Rewritten codebase now uses classes instead of modules with global variables ✔️
- Automatic downloading of the list of followers and using it as an input ✔️
- Better 'Watch Streak' strategy in the priority system [#11](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/11) ✔️
- Auto claiming [game drops](https://help.twitch.tv/s/article/mission-based-drops) from the Twitch inventory [#21](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/21) ✔️
- Placing a bet / making a prediction with your channel points [#41](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/41) ([@lay295](https://github.com/lay295)) ✔️
- Switchable analytics chart that shows the progress of your points with various annotations [#96](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/96) ✔️
- Joining the IRC Chat to increase the watch time and get StreamElements points [#47](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/47) ✔️
- [Moments](https://help.twitch.tv/s/article/moments) claiming [#182](https://github.com/rdavydov/Twitch-Channel-Points-Miner-v2/issues/182) ✔️
- Notifying on `@nickname` mention in the Twitch chat [#227](https://github.com/rdavydov/Twitch-Channel-Points-Miner-v2/issues/227) ✔️

## Logs feature
### Full logs
```
%d/%m/%y %H:%M:%S - INFO - [run]: 💣  Start session: '9eb934b0-1684-4a62-b3e2-ba097bd67d35'
%d/%m/%y %H:%M:%S - INFO - [run]: 🤓  Loading data for x streamers. Please wait ...
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username1, channel_id=0000000, channel_points=67247) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username2, channel_id=0000000, channel_points=4240) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username3, channel_id=0000000, channel_points=61365) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_offline]: 😴  Streamer(username=streamer-username4, channel_id=0000000, channel_points=3760) is Offline!
%d/%m/%y %H:%M:%S - INFO - [set_online]: 🥳  Streamer(username=streamer-username, channel_id=0000000, channel_points=61365) is Online!
%d/%m/%y %H:%M:%S - INFO - [start_bet]: 🔧  Start betting for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo) owned by Streamer(username=streamer-username, channel_id=0000000, channel_points=61365)
%d/%m/%y %H:%M:%S - INFO - [__open_coins_menu]: 🔧  Open coins menu for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [__click_on_bet]: 🔧  Click on the bet for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [__enable_custom_bet_value]: 🔧  Enable input of custom value for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [on_message]: ⏰  Place the bet after: 89.99s for: EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx-15c61914ef69, title=Please star this repo)
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=61377) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [make_predictions]: 🍀  Going to complete bet for EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx-15c61914ef69, title=Please star this repo) owned by Streamer(username=streamer-username, channel_id=0000000, channel_points=61377)
%d/%m/%y %H:%M:%S - INFO - [make_predictions]: 🍀  Place 5k channel points on: SI (BLUE), Points: 848k, Users: 190 (70.63%), Odds: 1.24 (80.65%)
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +6675 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64206) - Reason: PREDICTION.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 📊  EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title=Please star this repo) - Result: WIN, Points won: 6675
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64218) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64230) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [claim_bonus]: 🎁  Claiming the bonus for Streamer(username=streamer-username, channel_id=0000000, channel_points=64230)!
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +60 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64290) - Reason: CLAIM.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64326) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +400 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64326) - Reason: WATCH_STREAK.
%d/%m/%y %H:%M:%S - INFO - [claim_bonus]: 🎁  Claiming the bonus for Streamer(username=streamer-username, channel_id=0000000, channel_points=64326)!
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +60 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64386) - Reason: CLAIM.
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +12 → Streamer(username=streamer-username, channel_id=0000000, channel_points=64398) - Reason: WATCH.
%d/%m/%y %H:%M:%S - INFO - [update_raid]: 🎭  Joining raid from Streamer(username=streamer-username, channel_id=0000000, channel_points=64398) to another-username!
%d/%m/%y %H:%M:%S - INFO - [on_message]: 🚀  +250 → Streamer(username=streamer-username, channel_id=0000000, channel_points=6845) - Reason: RAID.
```
### Less logs
```
%d/%m %H:%M:%S - 💣  Start session: '9eb934b0-1684-4a62-b3e2-ba097bd67d35'
%d/%m %H:%M:%S - 🤓  Loading data for 13 streamers. Please wait ...
%d/%m %H:%M:%S - 😴  streamer-username1 (xxx points) is Offline!
%d/%m %H:%M:%S - 😴  streamer-username2 (xxx points) is Offline!
%d/%m %H:%M:%S - 😴  streamer-username3 (xxx points) is Offline!
%d/%m %H:%M:%S - 😴  streamer-username4 (xxx points) is Offline!
%d/%m %H:%M:%S - 🥳  streamer-username (xxx points) is Online!
%d/%m %H:%M:%S - 🔧  Start betting for EventPrediction: Please star this repo owned by streamer-username (xxx points)
%d/%m %H:%M:%S - 🔧  Open coins menu for EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🔧  Click on the bet for EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🔧  Enable input of custom value for EventPrediction: Please star this repo
%d/%m %H:%M:%S - ⏰  Place the bet after: 89.99s EventPrediction: Please star this repo
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🍀  Going to complete bet for EventPrediction: Please star this repo owned by streamer-username (xxx points)
%d/%m %H:%M:%S - 🍀  Place 5k channel points on: SI (BLUE), Points: 848k, Users: 190 (70.63%), Odds: 1.24 (80.65%)
%d/%m %H:%M:%S - 🚀  +6675 → streamer-username (xxx points) - Reason: PREDICTION.
%d/%m %H:%M:%S - 📊  EventPrediction: Please star this repo - Result: WIN, Points won: 6675
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🚀  +60 → streamer-username (xxx points) - Reason: CLAIM.
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🚀  +400 → streamer-username (xxx points) - Reason: WATCH_STREAK.
%d/%m %H:%M:%S - 🚀  +60 → streamer-username (xxx points) - Reason: CLAIM.
%d/%m %H:%M:%S - 🚀  +12 → streamer-username (xxx points) - Reason: WATCH.
%d/%m %H:%M:%S - 🎭  Joining raid from streamer-username (xxx points) to another-username!
%d/%m %H:%M:%S - 🚀  +250 → streamer-username (xxx points) - Reason: RAID.
```
### Final report:
```
%d/%m/%y %H:%M:%S - 🛑  End session 'f738d438-cdbc-4cd5-90c4-1517576f1299'
%d/%m/%y %H:%M:%S - 📄  Logs file: /.../path/Twitch-Channel-Points-Miner-v2/logs/username.timestamp.log
%d/%m/%y %H:%M:%S - ⌛  Duration 10:29:19.547371

%d/%m/%y %H:%M:%S - 📊  BetSettings(Strategy=Strategy.SMART, Percentage=7, PercentageGap=20, MaxPoints=7500
%d/%m/%y %H:%M:%S - 📊  EventPrediction(event_id=xxxx-xxxx-xxxx-xxxx, title="Event Title1")
		Streamer(username=streamer-username, channel_id=0000000, channel_points=67247)
		Bet(TotalUsers=1k, TotalPoints=11M), Decision={'choice': 'B', 'amount': 5289, 'id': 'xxxx-yyyy-zzzz'})
		Outcome0(YES (BLUE) Points: 7M, Users: 641 (58.49%), Odds: 1.6, (5}%)
		Outcome1(NO (PINK),Points: 4M, Users: 455 (41.51%), Odds: 2.65 (37.74%))
		Result: {'type': 'LOSE', 'won': 0}
%d/%m/%y %H:%M:%S - 📊  EventPrediction(event_id=yyyy-yyyy-yyyy-yyyy, title="Event Title2")
		Streamer(username=streamer-username, channel_id=0000000, channel_points=3453464)
		Bet(TotalUsers=921, TotalPoints=11M), Decision={'choice': 'A', 'amount': 4926, 'id': 'xxxx-yyyy-zzzz'})
		Outcome0(YES (BLUE) Points: 9M, Users: 562 (61.02%), Odds: 1.31 (76.34%))
		Outcome1(YES (PINK) Points: 3M, Users: 359 (38.98%), Odds: 4.21 (23.75%))
		Result: {'type': 'WIN', 'won': 6531}
%d/%m/%y %H:%M:%S - 📊  EventPrediction(event_id=ad152117-251b-4666-b683-18e5390e56c3, title="Event Title3")
		Streamer(username=streamer-username, channel_id=0000000, channel_points=45645645)
		Bet(TotalUsers=260, TotalPoints=3M), Decision={'choice': 'A', 'amount': 5054, 'id': 'xxxx-yyyy-zzzz'})
		Outcome0(YES (BLUE) Points: 689k, Users: 114 (43.85%), Odds: 4.24 (23.58%))
		Outcome1(NO (PINK) Points: 2M, Users: 146 (56.15%), Odds: 1.31 (76.34%))
		Result: {'type': 'LOSE', 'won': 0}

%d/%m/%y %H:%M:%S - 🤖  Streamer(username=streamer-username, channel_id=0000000, channel_points=67247), Total points gained (after farming - before farming): -7838
%d/%m/%y %H:%M:%S - 💰  CLAIM(11 times, 550 gained), PREDICTION(1 times, 6531 gained), WATCH(35 times, 350 gained)
%d/%m/%y %H:%M:%S - 🤖  Streamer(username=streamer-username2, channel_id=0000000, channel_points=61365), Total points gained (after farming - before farming): 977
%d/%m/%y %H:%M:%S - 💰  CLAIM(4 times, 240 gained), REFUND(1 times, 605 gained), WATCH(11 times, 132 gained)
%d/%m/%y %H:%M:%S - 🤖  Streamer(username=streamer-username5, channel_id=0000000, channel_points=25960), Total points gained (after farming - before farming): 1680
%d/%m/%y %H:%M:%S - 💰  CLAIM(17 times, 850 gained), WATCH(53 times, 530 gained)
%d/%m/%y %H:%M:%S - 🤖  Streamer(username=streamer-username6, channel_id=0000000, channel_points=9430), Total points gained (after farming - before farming): 1120
%d/%m/%y %H:%M:%S - 💰  CLAIM(14 times, 700 gained), WATCH(42 times, 420 gained), WATCH_STREAK(1 times, 450 gained)
```

## How to use:
First of all please create a run.py file. You can just copy [example.py](https://github.com/rdavydov/Twitch-Channel-Points-Miner-v2/blob/master/example.py) and modify it according to your needs.
```python
# -*- coding: utf-8 -*-

import logging
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Webhook import Webhook
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Gotify import Gotify
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings

twitch_miner = TwitchChannelPointsMiner(
    username="your-twitch-username",
    password="write-your-secure-psw",           # If no password will be provided, the script will ask interactively
    claim_drops_startup=False,                  # If you want to auto claim all drops from Twitch inventory on the startup
    priority=[                                  # Custom priority in this case for example:
        Priority.STREAK,                        # - We want first of all to catch all watch streak from all streamers
        Priority.DROPS,                         # - When we don't have anymore watch streak to catch, wait until all drops are collected over the streamers
        Priority.ORDER                          # - When we have all of the drops claimed and no watch-streak available, use the order priority (POINTS_ASCENDING, POINTS_DESCENDING)
    ],
    enable_analytics=False,			# Disables Analytics if False. Disabling it significantly reduces memory consumption
    disable_ssl_cert_verification=False,	# Set to True at your own risk and only to fix SSL: CERTIFICATE_VERIFY_FAILED error
    disable_at_in_nickname=False,               # Set to True if you want to check for your nickname mentions in the chat even without @ sign
    logger_settings=LoggerSettings(
        save=True,                              # If you want to save logs in a file (suggested)
        console_level=logging.INFO,             # Level of logs - use logging.DEBUG for more info
        console_username=False,                 # Adds a username to every console log line if True. Also adds it to Telegram, Discord, etc. Useful when you have several accounts
        auto_clear=True,                        # Create a file rotation handler with interval = 1D and backupCount = 7 if True (default)
        time_zone="",                           # Set a specific time zone for console and file loggers. Use tz database names. Example: "America/Denver"
        file_level=logging.DEBUG,               # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=True,                             # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less=False,                             # If you think that the logs are too verbose, set this to True
        colored=True,                           # If you want to print colored text
        color_palette=ColorPalette(             # You can also create a custom palette color (for the common message).
            STREAMER_online="GREEN",            # Don't worry about lower/upper case. The script will parse all the values.
            streamer_offline="red",             # Read more in README.md
            BET_wiN=Fore.MAGENTA                # Color allowed are: [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET].
        ),
        telegram=Telegram(                                                          # You can omit or set to None if you don't want to receive updates on Telegram
            chat_id=123456789,                                                      # Chat ID to send messages @getmyid_bot
            token="123456789:shfuihreuifheuifhiu34578347",                          # Telegram API token @BotFather
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE,
                    Events.BET_LOSE, Events.CHAT_MENTION],                          # Only these events will be sent to the chat
            disable_notification=True,                                              # Revoke the notification (sound/vibration)
        ),
        discord=Discord(
            webhook_api="https://discord.com/api/webhooks/0123456789/0a1B2c3D4e5F6g7H8i9J",  # Discord Webhook URL
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE,
                    Events.BET_LOSE, Events.CHAT_MENTION],					                         # Only these events will be sent to the chat
        ),
        webhook=Webhook(
            endpoint="https://example.com/webhook",                                                                    # Webhook URL
            method="GET",                                                                   # GET or POST
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE,
                    Events.BET_LOSE, Events.CHAT_MENTION],                                  # Only these events will be sent to the endpoint
        ),
        matrix=Matrix(
            username="twitch_miner",                                                   # Matrix username (without homeserver)
            password="...",                                                            # Matrix password
            homeserver="matrix.org",                                                   # Matrix homeserver
            room_id="...",                                                             # Room ID
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE], # Only these events will be sent
        ),
        pushover=Pushover(
            userkey="YOUR-ACCOUNT-TOKEN",                                             # Login to https://pushover.net/, the user token is on the main page
            token="YOUR-APPLICATION-TOKEN",                                           # Create a application on the website, and use the token shown in your application
            priority=0,                                                               # Read more about priority here: https://pushover.net/api#priority
            sound="pushover",                                                         # A list of sounds can be found here: https://pushover.net/api#sounds
            events=[Events.CHAT_MENTION, Events.DROP_CLAIM],                          # Only these events will be sent
        ),
        gotify=Gotify(
            endpoint="https://example.com/message?token=TOKEN",
            priority=8,
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE,
                    Events.BET_LOSE, Events.CHAT_MENTION], 
        )
    ),
    streamer_settings=StreamerSettings(
        make_predictions=True,                  # If you want to Bet / Make prediction
        follow_raid=True,                       # Follow raid to obtain more points
        claim_drops=True,                       # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        claim_moments=True,                     # If set to True, https://help.twitch.tv/s/article/moments will be claimed when available
        watch_streak=True,                      # If a streamer go online change the priority of streamers array and catch the watch screak. Issue #11
        community_goals=False,                  # If True, contributes the max channel points per stream to the streamers' community challenge goals
        chat=ChatPresence.ONLINE,               # Join irc chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=BetSettings(
            strategy=Strategy.SMART,            # Choose you strategy!
            percentage=5,                       # Place the x% of your channel points
            percentage_gap=20,                  # Gap difference between outcomesA and outcomesB (for SMART strategy)
            max_points=50000,                   # If the x percentage of your channel points is gt bet_max_points set this value
            stealth_mode=True,                  # If the calculated amount of channel points is GT the highest bet, place the highest value minus 1-2 points Issue #33
            delay_mode=DelayMode.FROM_END,      # When placing a bet, we will wait until `delay` seconds before the end of the timer
            delay=6,
            minimum_points=20000,               # Place the bet only if we have at least 20k points. Issue #113
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,     # Where apply the filter. Allowed [PERCENTAGE_USERS, ODDS_PERCENTAGE, ODDS, TOP_POINTS, TOTAL_USERS, TOTAL_POINTS]
                where=Condition.LTE,            # 'by' must be [GT, LT, GTE, LTE] than value
                value=800
            )
        )
    )
)

# You can customize the settings for each streamer. If not settings were provided, the script would use the streamer_settings from TwitchChannelPointsMiner.
# If no streamer_settings are provided in TwitchChannelPointsMiner the script will use default settings.
# The streamers array can be a String -> username or Streamer instance.

# The settings priority are: settings in mine function, settings in TwitchChannelPointsMiner instance, default settings.
# For example, if in the mine function you don't provide any value for 'make_prediction' but you have set it on TwitchChannelPointsMiner instance, the script will take the value from here.
# If you haven't set any value even in the instance the default one will be used

#twitch_miner.analytics(host="127.0.0.1", port=5000, refresh=5, days_ago=7)   # Start the Analytics web-server (replit: host="0.0.0.0")
#twitch_miner.channel_points(host="127.0.0.1", port=8765, path="/channel-points/ws")  # Start the Channel Points websocket server

twitch_miner.mine(
    [
        Streamer("streamer-username01", settings=StreamerSettings(make_predictions=True  , follow_raid=False , claim_drops=True  , watch_streak=True , community_goals=False , bet=BetSettings(strategy=Strategy.SMART      , percentage=5 , stealth_mode=True,  percentage_gap=20 , max_points=234   , filter_condition=FilterCondition(by=OutcomeKeys.TOTAL_USERS,      where=Condition.LTE, value=800 ) ) )),
        Streamer("streamer-username02", settings=StreamerSettings(make_predictions=False , follow_raid=True  , claim_drops=False ,                                             bet=BetSettings(strategy=Strategy.PERCENTAGE , percentage=5 , stealth_mode=False, percentage_gap=20 , max_points=1234  , filter_condition=FilterCondition(by=OutcomeKeys.TOTAL_POINTS,     where=Condition.GTE, value=250 ) ) )),
        Streamer("streamer-username03", settings=StreamerSettings(make_predictions=True  , follow_raid=False ,                     watch_streak=True , community_goals=True  , bet=BetSettings(strategy=Strategy.SMART      , percentage=5 , stealth_mode=False, percentage_gap=30 , max_points=50000 , filter_condition=FilterCondition(by=OutcomeKeys.ODDS,             where=Condition.LT,  value=300 ) ) )),
        Streamer("streamer-username04", settings=StreamerSettings(make_predictions=False , follow_raid=True  ,                     watch_streak=True ,                                                                                                                                                                                                                                                       )),
        Streamer("streamer-username05", settings=StreamerSettings(make_predictions=True  , follow_raid=True  , claim_drops=True ,  watch_streak=True , community_goals=True  , bet=BetSettings(strategy=Strategy.HIGH_ODDS  , percentage=7 , stealth_mode=True,  percentage_gap=20 , max_points=90    , filter_condition=FilterCondition(by=OutcomeKeys.PERCENTAGE_USERS, where=Condition.GTE, value=300 ) ) )),
        Streamer("streamer-username06"),
        Streamer("streamer-username07"),
        Streamer("streamer-username08"),
        "streamer-username09",
        "streamer-username10",
        "streamer-username11"
    ],                                  # Array of streamers (order = priority)
    followers=False,                    # Automatic download the list of your followers
    followers_order=FollowersOrder.ASC  # Sort the followers list by follow date. ASC or DESC
)
```
You can also use all the default values except for your username obv. Short version:
```python
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.classes.Settings import FollowersOrder
twitch_miner = TwitchChannelPointsMiner("your-twitch-username")
twitch_miner.mine(["streamer1", "streamer2"])                                                       # Array of streamers OR
twitch_miner.mine(followers=True, followers_order=FollowersOrder.ASC)                               # Automatic use the followers list OR
twitch_miner.mine(["streamer1", "streamer2"], followers=True, followers_order=FollowersOrder.DESC)  # Mixed
```
If you follow so many streamers on Twitch, but you don't want to mine points for all of them, you can blacklist the users with the `blacklist` keyword. [#94](https://github.com/Tkd-Alex/Twitch-Channel-Points-Miner-v2/issues/94)
```python
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
twitch_miner = TwitchChannelPointsMiner("your-twitch-username")
twitch_miner.mine(followers=True, blacklist=["user1", "user2"])  # Blacklist example
```

### By cloning the repository
1. Clone this repository `git clone https://github.com/rdavydov/Twitch-Channel-Points-Miner-v2`
2. Install all the requirements `pip install -r requirements.txt` . If you have problems with requirements, make sure to have at least Python3.6. You could also try to create a _virtualenv_ and then install all the requirements
```sh
git clone https://github.com/Armi1014/Twitch-Channel-Points-Miner-v2
cd Twitch-Channel-Points-Miner-v2
cp example.py run.py
uv sync
uv run run.py
```

Hermes is the default websocket backend in this fork. If you need the legacy PubSub path, set `USE_HERMES = False` in your runner file.

**Pip Alternative**

```sh
python -m venv .venv
source .venv/bin/activate
cp example.py run.py
pip install -r requirements.txt
python run.py
```

## Why this fork

Compared to upstream, this fork focuses on **reliability first**:

* better handling of transient Twitch/API/network issues
* more reliable watch streak behavior, including already-online channels at startup
* per-account streak cache files to avoid multi-account conflicts
* clearer `Priority.FAVORITE` behavior
* faster startup and less waiting during the initial refresh cycle
* reduced recurring timeout / backend error log spam
* Hermes websocket support with explicit PubSub fallback

**Example startup improvement**

* upstream sample: `179s`
* this fork sample: `14s`
* about **12.8x faster** in that test

Results vary depending on account size, network quality, and Twitch backend health.
The exact number will vary, but faster startup is a core goal of this fork, not just a side effect.

## Use this fork if...

* you care more about **reliability** than staying as close as possible to upstream
* you use **watch streaks** heavily
* you want clearer favorite / priority behavior
* you want the miner to become usable faster after launch
* you want fewer annoying transient error logs

## Subscription Notifications

This fork can send `Events.SUBSCRIPTION` notifications to Discord or other webhook-style integrations.

What it does:

* listens for Twitch IRC `USERNOTICE` events
* formats a cleaner subscription message with the streamer/channel and current points
* only alerts for subscription events that are about **your own account**

What counts as "about your own account":

* you subscribe
* you renew a subscription
* you receive a sub gift
* you upgrade a gift or Prime subscription

What it ignores:

* other viewers subscribing
* other viewers renewing
* other viewers receiving gifted subs

Important:

* this depends on IRC chat being enabled for that streamer
* `chat=ChatPresence.NEVER` disables this feature for that channel
* `chat=ChatPresence.ONLINE` is enough

See [example.py](example.py) for a basic Discord webhook configuration example.

## Docs

* [Latest Releases](https://github.com/Armi1014/Twitch-Channel-Points-Miner-v2/releases)
* [Example Config](example.py)
* [Fork Features](FORK_FEATURES.md)
* [FAQ](FAQ.md)
* [Contributing](CONTRIBUTING.md)

## Disclaimer

This project is not affiliated with Twitch.

Use it at your own risk and make sure you understand the platform rules before using automation tools.
