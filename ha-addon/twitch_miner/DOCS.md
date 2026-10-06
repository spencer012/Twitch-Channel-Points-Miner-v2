# Twitch Channel Points Miner

Runs the miner with your own `run.py`, stored in the add-on configuration.
Analytics opens from the sidebar (Ingress).

## Setting run.py

1. Open **Configuration**, then the three-dot menu, **Edit in YAML**.
2. Paste the whole file as a block (keep the two-space indent):

   ```yaml
   run_py: |
     import logging
     ...
     twitch_miner.mine(["streamer_one", "streamer_two"])
   ```

3. Save and restart the add-on.

Always edit `run_py` in YAML mode. The form view shows a single-line box and
can strip the line breaks.

Requirements for the pasted file:

- `twitch_miner.analytics(host="0.0.0.0", port=5000, ...)` so the sidebar
  panel can reach it.
- No `twitch_miner.channel_points(...)` call unless you also expose its port.

## Start-up check

On every start the add-on checks `run_py`:

- Empty, a single line, or a syntax error: the problem is printed in the
  **Log** tab with the line number.
- If a previous `run_py` passed, the add-on keeps mining with that version
  and says so in the log. Otherwise it stops.

Errors that only appear when the script runs (for example a misspelled
setting) show up in the log as a normal crash.

## Data

`cookies/`, `logs/` and `analytics/` live in the add-on's `/data` and are
included in Home Assistant backups.

To bring data from another install, put those folders in
`/share/twitch_miner_import/` (for example with the SSH add-on) before the
first start. They are copied only into empty folders. Delete the import
folder afterwards: it holds your login cookie and `/share` is readable by
other add-ons.

## Login

If there is no valid cookie, the log shows a code to enter at
https://www.twitch.tv/activate. The miner continues once it is accepted.
