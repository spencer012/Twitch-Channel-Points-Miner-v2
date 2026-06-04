import unittest
from unittest.mock import patch

from TwitchChannelPointsMiner.classes.Twitch import Twitch
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer


class OnlineDetectionTest(unittest.TestCase):
    def test_forced_check_ignores_recent_stream_down(self):
        twitch = Twitch("self-check", "ua")
        streamer = Streamer("ended")
        streamer.is_online = False
        streamer.online_at = 100
        streamer.offline_at = 150

        with patch("TwitchChannelPointsMiner.classes.Twitch.time.time", return_value=160):
            with patch.object(twitch, "get_spade_url") as get_spade_url:
                with patch.object(twitch, "update_stream") as update_stream:
                    twitch.check_streamer_online(streamer, force=True)

        get_spade_url.assert_not_called()
        update_stream.assert_not_called()
        self.assertFalse(streamer.is_online)

    def test_forced_check_still_runs_for_initial_offline_streamer(self):
        twitch = Twitch("self-check", "ua")
        streamer = Streamer("starting")
        streamer.is_online = False
        streamer.online_at = 0
        streamer.offline_at = 150

        with patch("TwitchChannelPointsMiner.classes.Twitch.time.time", return_value=160):
            with patch.object(twitch, "get_spade_url") as get_spade_url:
                with patch.object(twitch, "update_stream", return_value=True) as update_stream:
                    twitch.check_streamer_online(streamer, force=True)

        get_spade_url.assert_called_once_with(streamer)
        update_stream.assert_called_once_with(streamer, force=True)
        self.assertTrue(streamer.is_online)

