"""Test the purei9 module"""
import unittest
from purei9_unofficial.common import BatteryStatus, RobotStates
from homeassistant.components.vacuum import (
    STATE_CLEANING,
    STATE_DOCKED,
    STATE_IDLE
)
from custom_components.purei9 import purei9

class TestPureI9(unittest.TestCase):
    """Tests for the purei9 module"""
    data_state_to_hass = [
        # No need to test every single case. The test will become too fragile.
        (RobotStates[1], BatteryStatus[1], STATE_CLEANING),
        (RobotStates[10], BatteryStatus[6], STATE_DOCKED),
        (RobotStates[10], BatteryStatus[5], STATE_IDLE)
    ]

    def test_state_to_hass(self):
        """Test the state_to_hass function"""
        for purei9_state, purei9_battery, expected in self.data_state_to_hass:
            with self.subTest(purei9_state=purei9_state,purei9_battery=purei9_battery):
                self.assertEqual(expected, purei9.state_to_hass(purei9_state, purei9_battery))

    data_battery_to_hass = [
        (BatteryStatus[1], 0),
        (BatteryStatus[2], 20),
        (BatteryStatus[3], 40),
        (BatteryStatus[4], 60),
        (BatteryStatus[5], 80),
        (BatteryStatus[6], 100)
    ]

    def test_battery_to_hass(self):
        """Test the battery_to_hass function"""
        for purei9_battery, expected in self.data_battery_to_hass:
            with self.subTest():
                self.assertEqual(expected, purei9.battery_to_hass(purei9_battery))

    def test_params(self):
        """Test the Params class"""
        unique_id = "bar"
        name = "foo"

        params = purei9.Params(unique_id, name)

        # No need to test every property. The test will become too fragile.
        self.assertEqual(unique_id, params.unique_id)
        self.assertEqual(name, params.name)
        self.assertEqual(100, params.battery)

if __name__ == '__main__':
    unittest.main()
