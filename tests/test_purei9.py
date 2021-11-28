"""Test the purei9 module"""
import unittest
from purei9_unofficial.common import BatteryStatus, RobotStates, PowerMode
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
        (RobotStates.Cleaning, BatteryStatus.Dead, STATE_CLEANING),
        (RobotStates.Sleeping, BatteryStatus.High, STATE_DOCKED),
        (RobotStates.Sleeping, BatteryStatus.Normal, STATE_IDLE)
    ]

    def test_state_to_hass(self):
        """Test the state_to_hass function"""
        for purei9_state, purei9_battery, expected in self.data_state_to_hass:
            with self.subTest(purei9_state=purei9_state,purei9_battery=purei9_battery):
                self.assertEqual(expected, purei9.state_to_hass(purei9_state, purei9_battery))

    data_battery_to_hass = [
        (BatteryStatus.Dead, 0),
        (BatteryStatus.CriticalLow, 20),
        (BatteryStatus.Low, 40),
        (BatteryStatus.Medium, 60),
        (BatteryStatus.Normal, 80),
        (BatteryStatus.High, 100)
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

        params = purei9.Params(unique_id, name, list([PowerMode.MEDIUM.name]))

        # No need to test every property. The test will become too fragile.
        self.assertEqual(unique_id, params.unique_id)
        self.assertEqual(name, params.name)
        self.assertEqual(100, params.battery)

        # Attempt to set a new name
        new_name = "hello,world"
        params.name = new_name
        self.assertEqual(new_name, params.name)

    data_is_power_mode_v2 = [
        (list([1, 2, 3]), True),
        (list([1, 2]), False),
    ]

    def test_is_power_mode_v2(self):
        """Test if the power mode is v2 or not"""
        for fan_speed_list, expected in self.data_is_power_mode_v2:
            with self.subTest():
                self.assertEqual(expected, purei9.is_power_mode_v2(fan_speed_list))

    data_fan_speed_list_to_hass = [
        (
            list([PowerMode.LOW, PowerMode.HIGH]),
            list([purei9.POWER_MODE_ECO, purei9.POWER_MODE_POWER])
        ),
        (
            list([PowerMode.LOW, PowerMode.MEDIUM, PowerMode.HIGH]),
            list([purei9.POWER_MODE_QUIET, purei9.POWER_MODE_SMART, purei9.POWER_MODE_POWER])
        ),
    ]

    def test_fan_speed_list_to_hass(self):
        """Test to convert the fan speed list to a format used by the integration"""
        for fan_speed_list, expected in self.data_fan_speed_list_to_hass:
            with self.subTest():
                self.assertEqual(expected, purei9.fan_speed_list_to_hass(fan_speed_list))

    data_fan_speed_to_purei9 = [
        (purei9.POWER_MODE_ECO, PowerMode.MEDIUM),
        (purei9.POWER_MODE_QUIET, PowerMode.LOW),
        (purei9.POWER_MODE_SMART, PowerMode.MEDIUM),
        (purei9.POWER_MODE_POWER, PowerMode.HIGH),
    ]

    def test_fan_speed_to_purei9(self):
        """Test to convert a fan speed value back to Purei9 integration format"""
        for fan_speed, expected in self.data_fan_speed_to_purei9:
            with self.subTest():
                self.assertEqual(expected, purei9.fan_speed_to_purei9(fan_speed))

    data_fan_speed_to_hass = [
        (list([1, 2]), PowerMode.MEDIUM, purei9.POWER_MODE_ECO),
        (list([1, 2, 3]), PowerMode.LOW, purei9.POWER_MODE_QUIET),
        (list([1, 2, 3]), PowerMode.MEDIUM, purei9.POWER_MODE_SMART),
        (list([1, 2]), PowerMode.HIGH, purei9.POWER_MODE_POWER),
    ]

    def test_fan_speed_to_hass(self):
        """Test to convert a fan speed value back to Purei9 integration format"""
        for fan_speed_list, fan_speed, expected in self.data_fan_speed_to_hass:
            with self.subTest():
                self.assertEqual(expected, purei9.fan_speed_to_hass(fan_speed_list, fan_speed))

if __name__ == '__main__':
    unittest.main()
