#!/usr/bin/env python3

""" Test control for SDS011 sensor """

import time
import unittest
import pytest
import serial

from pysds011.sds011 import SDS011
from pysds011.definitions import WorkingMode, ReportMode, Modifier, Command


@pytest.mark.skip(reason="Only works with real SDS011 sensor.")
class TestSDS011Simulation(unittest.TestCase):
    """ Tests SDS011 class with real SDS011 sensor """
    @classmethod
    def setUpClass(cls):
        cls.serial = serial.Serial('COM4', 9600)
        cls.sensor = SDS011(cls.serial)

    @classmethod
    def tearDownClass(cls):
        cls.serial.close()

    def setUp(self):
        time.sleep(1)

    def tearDown(self):
        pass

    def __check_command_id_command_valid(self):
        """ Check command id is b'\xff\xff' and command is valid """
        self.assertEqual(self.sensor.last_command[-4:-2], bytes([255, 255]))
        self.assertTrue(self.sensor.command_message_valid())

    def __check_reply_id_reply_valid(self):
        """ Check command id is id from simulated device and reply is valid """
        self.assertEqual(self.sensor.last_reply[-4:-2], bytes(self.sensor.device_id))
        self.assertTrue(self.sensor.reply_message_valid())

    def __check_working_mode_command(self):
        """ Check working mode command """
        self.assertEqual(self.sensor.last_command[2], Command.WORKING_MODE.value)
        self.__check_command_id_command_valid()

    def __check_working_mode_reply(self):
        """ Check working mode reply """
        self.assertEqual(self.sensor.last_reply[2], Command.WORKING_MODE.value)
        self.__check_reply_id_reply_valid()

    def test_working_mode(self):
        """ Test working mode commands """
        # Set Sleep Mode
        working_mode = WorkingMode.SLEEP_MODE
        self.sensor.set_working_mode(working_mode)
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[4], working_mode.value)
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)
        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[4], working_mode.value)
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        time.sleep(2)

        # # Get Sleep Mode (Get Working Mode not working with my device, when in sleep mode.
        #                   But it should work, like I understand the manual.)
        # self.sensor.get_working_mode()
        # print(self.sensor.last_reply)
        # self.__check_working_mode_command()
        # self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)
        # self.__check_working_mode_reply()
        # self.assertEqual(self.sensor.last_reply[4], working_mode.value)
        # self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        # Set Work Mode
        working_mode = WorkingMode.WORK_MODE
        self.sensor.set_working_mode(working_mode)
        self.assertEqual(self.sensor.last_command[4], working_mode.value)
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)
        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[4], working_mode.value)
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Work Mode
        self.sensor.get_working_mode()
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)
        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[4], working_mode.value)
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)


    def __check_report_mode_command(self):
        """ Check report mode command """
        self.assertEqual(self.sensor.last_command[2], Command.REPORT_MODE.value)
        self.__check_command_id_command_valid()

    def __check_report_mode_reply(self):
        """ Check report mode reply """
        self.assertEqual(self.sensor.last_reply[2], Command.REPORT_MODE.value)
        self.__check_reply_id_reply_valid()

    def test_report_mode(self):
        """ Test report mode commands """
        # Set Report Mode Active
        report_mode = ReportMode.REPORT_ACTIVE_MODE
        self.sensor.set_report_mode(report_mode)
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[4], report_mode.value)
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)
        self.assertEqual(self.sensor.last_reply[4], report_mode.value)

        # Get Report Mode Active
        self.sensor.get_report_mode()
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)
        self.assertEqual(self.sensor.last_reply[4], report_mode.value)

        # Check read and decode
        for _ in range(2):
            self.sensor.read_and_decode_data()
            self.sensor.print_data()

        # Set Report Mode Query
        report_mode = ReportMode.REPORT_QUERY_MODE
        self.sensor.set_report_mode(report_mode)
        self.assertEqual(self.sensor.last_command[4], report_mode.value)
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)
        self.assertEqual(self.sensor.last_reply[4], report_mode.value)

        # Get Report Mode Query
        self.sensor.get_report_mode()
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)
        self.assertEqual(self.sensor.last_reply[4], report_mode.value)

        # Set to Remort Mode Active
        self.sensor.set_report_mode(ReportMode.REPORT_ACTIVE_MODE)

    def test_query_data(self):
        """ Test query data command and reply """
        self.sensor.query_data()
        self.assertEqual(self.sensor.last_command[2], Command.QUERY_DATA.value)
        self.__check_command_id_command_valid()
        self.sensor.decode_data()
        self.sensor.print_data()

    def __check_working_period_command(self):
        """ Check working period command"""
        self.assertEqual(self.sensor.last_command[2], Command.WORKING_PERIOD.value)
        self.__check_command_id_command_valid()

    def __check_working_period_reply(self):
        """ Check working period reply"""
        self.assertEqual(self.sensor.last_reply[2], Command.WORKING_PERIOD.value)
        self.__check_reply_id_reply_valid()

    def test_woring_period(self):
        """ Test working period commands """
        # Set Working Period 0 (continuous)
        working_period = 0
        self.sensor.set_working_period(working_period)
        self.__check_working_period_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)
        self.assertEqual(self.sensor.last_command[4], working_period)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)
        self.assertEqual(self.sensor.last_reply[4], working_period)

        # Get Working Period
        self.sensor.get_working_period()
        self.__check_working_period_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[4], working_period)
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

        time.sleep(1)

        # # Set Working Period 1-30 minutes (periodic) work 30 seconds and sleep n*60-30 seconds
        working_period = 5
        self.sensor.set_working_period(working_period)
        self.__check_working_period_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)
        self.assertEqual(self.sensor.last_command[4], working_period)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)
        self.assertEqual(self.sensor.last_reply[4], working_period)

        # Get Working Period
        self.sensor.get_working_period()
        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[4], working_period)
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

        # Set to default after test
        self.sensor.set_working_period(0)

    def test_set_device_id(self):
        """ Test set device id command and reply """
        # Check set device id command
        old_device_id = self.sensor.device_id
        new_device_id = [20, 21]
        self.sensor.set_device_id(new_device_id=new_device_id, device_id=old_device_id)
        self.assertEqual(self.sensor.last_command[2], Command.SET_DEVICE_ID.value)
        self.assertEqual(self.sensor.last_command[13:15], bytes(new_device_id))
        self.assertEqual(self.sensor.last_command[15:17], bytes(old_device_id))
        self.assertTrue(self.sensor.command_message_valid())
        self.assertEqual(self.sensor.device_id, new_device_id)

        # Check set device id reply
        self.assertEqual(self.sensor.last_reply[2], Command.SET_DEVICE_ID.value)
        self.assertEqual(self.sensor.last_reply[-4:-2], bytes(new_device_id))
        self.assertTrue(self.sensor.reply_message_valid())

        time.sleep(1)

        # Set the original device id again [112, 80]
        self.sensor.set_device_id(new_device_id=[112, 80], device_id=new_device_id)

    def test_firmware(self):
        """ Test get firmware command and reply """
        # Check get firmware command
        self.sensor.get_firmware_version()
        self.assertEqual(self.sensor.last_command[2], Command.GET_FIRMWARE.value)
        self.assertEqual(self.sensor.last_command[-4:-2], bytes([255, 255]))
        self.assertEqual(self.sensor.last_command[3:15], bytes([0]*12))
        self.assertTrue(self.sensor.command_message_valid())

        # Check get firmware reply
        self.assertEqual(self.sensor.last_reply[2], Command.GET_FIRMWARE.value)
        self.assertEqual(self.sensor.last_reply[3:6], bytes([21, 1, 12]))
        self.assertEqual(self.sensor.last_reply[-4:-2], bytes(self.sensor.device_id))
        self.assertTrue(self.sensor.reply_message_valid())

        self.sensor.print_firmware()
        print('Device ID: ' + self.sensor.get_device_id())

if __name__ == '__main__':
    unittest.main()
