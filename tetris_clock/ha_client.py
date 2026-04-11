"""
Home Assistant integration: polls HA REST API for temperature and display state.

Runs a background daemon thread that periodically fetches:
- Temperature from a sensor entity
- Display on/off state from an input_boolean entity

Triggers temperature display every 5 minutes.
"""

import json
import sys
import time
import threading
import urllib.request
import urllib.error


class HAState:
    """Shared state between the HA polling thread and the main loop."""

    def __init__(self, ha_url, ha_token, temp_entity_id, display_entity_id=None,
                 temp_interval=300, temp_display_secs=12):
        """
        Args:
            ha_url: Home Assistant base URL (e.g., http://homeassistant.local:8123)
            ha_token: Long-lived access token
            temp_entity_id: Sensor entity ID for temperature
            display_entity_id: input_boolean entity ID for on/off control (optional)
            temp_interval: Seconds between temperature display triggers (default: 300)
            temp_display_secs: How long to show temperature (default: 12)
        """
        self.ha_url = ha_url.rstrip("/")
        self.ha_token = ha_token
        self.temp_entity_id = temp_entity_id
        self.display_entity_id = display_entity_id
        self.temp_interval = temp_interval
        self.temp_display_secs = temp_display_secs

        # Shared state (read by main loop)
        self.temperature = None
        self.display_on = True
        self.show_temp_until = 0.0

    def start(self):
        """Launch the background polling thread."""
        t = threading.Thread(target=self._poll_loop, daemon=True)
        t.start()

    def _fetch_state(self, entity_id):
        """Fetch entity state from HA REST API. Returns state string or None."""
        url = f"{self.ha_url}/api/states/{entity_id}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.ha_token}",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["state"]

    def _poll_loop(self):
        """Background polling loop."""
        backoff = 10
        last_temp_trigger = 0.0

        while True:
            try:
                # Fetch temperature
                state = self._fetch_state(self.temp_entity_id)
                self.temperature = float(state)

                # Fetch display on/off state
                if self.display_entity_id:
                    state = self._fetch_state(self.display_entity_id)
                    self.display_on = state == "on"

                # Trigger temperature display every temp_interval seconds
                now = time.monotonic()
                if (self.temperature is not None
                        and now - last_temp_trigger >= self.temp_interval):
                    self.show_temp_until = now + self.temp_display_secs
                    last_temp_trigger = now

                backoff = 10  # reset on success

            except Exception as e:
                print(f"HA poll error: {e}", file=sys.stderr)
                backoff = min(backoff * 2, 60)

            time.sleep(backoff)
