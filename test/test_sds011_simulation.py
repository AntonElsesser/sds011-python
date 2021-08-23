#!/usr/bin/env python3

""" Test simulation and control for SDS011 sensor """

import unittest
from sds011 import SDS011, WorkingMode, ReportMode, Modifier, Command, SimulationSDS011


class TestSDS011Simulation(unittest.TestCase):
    """ Tests SDS011 class and SDS011Simulation class """
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.sensor_simulation = SimulationSDS011()
        self.sensor = SDS011(self.sensor_simulation)

    def tearDown(self):
        self.sensor_simulation.close()

    def test_simulation_read_write(self):
        """ Test read() write() funktion of SDS011Simulation """
        self.sensor_simulation.flushInput()
        self.sensor_simulation.data = b'\x10\x11\x00'
        self.assertEqual(self.sensor_simulation.read(), b'\x10')
        self.assertEqual(self.sensor_simulation.read(2), b'\x11\x00')
        self.assertEqual(self.sensor_simulation.read(), b'\x10')
        self.assertEqual(self.sensor_simulation.read(5), b'\x11\x00\x10\x11\x00')
        self.assertEqual(self.sensor_simulation.write(self.sensor_simulation.data), 3)

    def test_read_sample_data_sds011(self):
        """ Load and verify sample data from file  """
        self.sensor_simulation.read_sample_data_sds011()
        self.sensor.read_message()
        self.assertEqual(self.sensor.last_reply.hex(), 'aac02200280070500aab')
        self.assertTrue(self.sensor.reply_message_valid())
        self.sensor.read_message()
        self.assertEqual(self.sensor.serial.read(), b'\xaa')
        self.sensor.read_message()
        self.assertEqual(self.sensor.last_reply.hex(), 'aac021002800705009ab')
        self.assertTrue(self.sensor.reply_message_valid())
        self.sensor.decode_data()
        self.sensor.print_data()
        self.sensor.serial.offset = 0
        self.assertEqual(self.sensor.serial.read(545)[-1:].hex(), '28')
        for _ in range(3):
            self.sensor.read_and_decode_data()
            self.sensor.print_data()

    def test_print_data(self):
        """ Test print of measurement values """
        self.sensor_simulation.read_sample_data_sds011()
        self.sensor.read_message()
        self.sensor.print_data()
        self.sensor.decode_data()
        self.sensor.print_data()

    def test_reply_message_valid(self):
        """ Test validation of reply message """
        # Valid reply
        self.sensor.last_reply = b'\xaa\xc0\x22\x00\x28\x00\x70\x50\x0a\xab'
        self.assertTrue(self.sensor.reply_message_valid())
        # Wrong header
        self.sensor.last_reply = b'\xda\xc0\x22\x00\x28\x00\x70\x50\x0a\xab'
        self.assertFalse(self.sensor.reply_message_valid())
        # Wrong tail
        self.sensor.last_reply = b'\xaa\xc0\x22\x00\x28\x00\x70\x50\x0a\x2b'
        self.assertFalse(self.sensor.reply_message_valid())
        # Wrong length
        self.sensor.last_reply = b'\xaa\xc0\x22\x00\x28\x70\x50\x0a\xab'
        self.assertFalse(self.sensor.reply_message_valid())
        # Wrong message type
        self.sensor.last_reply = b'\xaa\xc2\x22\x00\x28\x00\x70\x50\x0a\xab'
        self.assertFalse(self.sensor.reply_message_valid())
        # Wrong checksum
        self.sensor.last_reply = b'\xaa\xc0\x22\x00\x28\x00\x70\x50\x1a\xab'
        self.assertFalse(self.sensor.reply_message_valid())


    def __check_command_id_command_valid(self):
        """ Check command id is b'\xff\xff' and command is valid """
        self.assertEqual(self.sensor.last_command[-4:-2], bytes([255, 255]))
        self.assertTrue(self.sensor.command_message_valid())

    def __check_reply_id_reply_valid(self):
        """ Check command id is id from simulated device and reply is valid """
        self.assertEqual(self.sensor.last_reply[-4:-2], bytes(self.sensor_simulation.device_id))
        self.assertTrue(self.sensor.reply_message_valid())

    def __check_working_mode_command(self):
        """ Check working mode command """
        self.assertEqual(self.sensor.last_command[2], Command.WORKING_MODE.value)
        self.__check_command_id_command_valid()

    def __check_working_mode_reply(self):
        """ Check working mode reply """
        self.assertEqual(self.sensor.last_reply[2], Command.WORKING_MODE.value)
        self.assertEqual(self.sensor.last_reply[4], self.sensor_simulation.working_mode.value)
        self.__check_reply_id_reply_valid()

    def test_working_mode(self):
        """ Test working mode commands """
        # Set Sleep Mode
        self.sensor.set_working_mode(WorkingMode.SLEEP_MODE)
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[4], self.sensor_simulation.working_mode.value)
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Sleep Mode
        self.sensor.get_working_mode()
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

        # Set Work Mode
        self.sensor.set_working_mode(WorkingMode.WORK_MODE)
        self.assertEqual(self.sensor.last_command[4], self.sensor_simulation.working_mode.value)
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Work Mode
        self.sensor.get_working_mode()
        self.__check_working_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_working_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)


    def __check_report_mode_command(self):
        """ Check report mode command """
        self.assertEqual(self.sensor.last_command[2], Command.REPORT_MODE.value)
        self.__check_command_id_command_valid()

    def __check_report_mode_reply(self):
        """ Check report mode reply """
        self.assertEqual(self.sensor.last_reply[2], Command.REPORT_MODE.value)
        self.assertEqual(self.sensor.last_reply[4], self.sensor_simulation.report_mode.value)
        self.__check_reply_id_reply_valid()

    def test_report_mode(self):
        """ Test report mode commands """
        # Set Report Mode Active
        self.sensor.set_report_mode(ReportMode.REPORT_ACTIVE_MODE)
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[4], self.sensor_simulation.report_mode.value)
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Report Mode Active
        self.sensor.get_report_mode()
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

        # Set Report Mode Query
        self.sensor.set_report_mode(ReportMode.REPORT_QUERY_MODE)
        self.assertEqual(self.sensor.last_command[4], self.sensor_simulation.report_mode.value)
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Report Mode Query
        self.sensor.get_report_mode()
        self.__check_report_mode_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_report_mode_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

    def test_query_data(self):
        """ Test query data command and reply """
        self.sensor.query_data()
        self.assertEqual(self.sensor.last_command[2], Command.QUERY_DATA.value)
        self.__check_command_id_command_valid()
        self.assertEqual(self.sensor.last_reply[2:6],
                         bytes(self.sensor_simulation.measurement_data))
        self.assertTrue(self.sensor.reply_message_valid())

    def __check_working_period_command(self):
        """ Check working period command"""
        self.assertEqual(self.sensor.last_command[2], Command.WORKING_PERIOD.value)
        self.__check_command_id_command_valid()

    def __check_working_period_reply(self):
        """ Check working period reply"""
        self.assertEqual(self.sensor.last_reply[2], Command.WORKING_PERIOD.value)
        self.assertEqual(self.sensor.last_reply[4], self.sensor_simulation.working_period)
        self.__check_reply_id_reply_valid()

    def test_woring_period(self):
        """ Test working period commands """
        # Set Working Period 0 (continuous)
        self.sensor.set_working_period(0)
        self.__check_working_period_command()
        self.assertEqual(self.sensor.last_command[4], self.sensor_simulation.working_period)
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Working Period
        self.sensor.get_working_period()
        self.__check_working_period_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

        # # Set Working Period 1-30 minutes (periodic) work 30 seconds and sleep n*60-30 seconds
        self.sensor.set_working_period(5)
        self.assertEqual(self.sensor.last_command[4], self.sensor_simulation.working_period)
        self.__check_working_period_command()
        self.assertEqual(self.sensor.last_command[3], Modifier.SET.value)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.SET.value)

        # Get Working Period
        self.sensor.get_working_period()
        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_command[3], Modifier.GET.value)

        self.__check_working_period_reply()
        self.assertEqual(self.sensor.last_reply[3], Modifier.GET.value)

    def test_set_device_id(self):
        """ Test set device id command and reply """
        # Check set device id command
        old_device_id = self.sensor_simulation.device_id
        new_device_id = [20, 21]
        self.sensor.set_device_id(new_device_id=new_device_id, device_id=old_device_id)
        self.assertEqual(self.sensor.last_command[2], Command.SET_DEVICE_ID.value)
        self.assertEqual(self.sensor.last_command[13:15], bytes(new_device_id))
        self.assertEqual(self.sensor.last_command[15:17], bytes(old_device_id))
        self.assertTrue(self.sensor.command_message_valid())
        self.assertEqual(self.sensor_simulation.device_id, new_device_id)

        # Check set device id reply
        self.assertEqual(self.sensor.last_reply[2], Command.SET_DEVICE_ID.value)
        self.assertEqual(self.sensor.last_reply[-4:-2], bytes(new_device_id))
        self.assertTrue(self.sensor.reply_message_valid())

    def test_firmware(self):
        """ Test get firmware command and reply """
        # Check get firmware command
        self.sensor.get_firmware_version()
        self.assertEqual(self.sensor.last_command[2], Command.GET_FIRMWARE.value)
        self.assertEqual(self.sensor.last_command[-4:-2], bytes([255, 255]))
        self.assertEqual(self.sensor_simulation.command[3:15], bytes([0]*12))
        self.assertTrue(self.sensor.command_message_valid())

        # Check get firmware reply
        self.assertEqual(self.sensor.last_reply[2], Command.GET_FIRMWARE.value)
        self.assertEqual(self.sensor.last_reply[3:6], bytes(self.sensor_simulation.firmware))
        self.assertEqual(self.sensor.last_reply[-4:-2], bytes(self.sensor_simulation.device_id))
        self.assertTrue(self.sensor.reply_message_valid())

        self.sensor.print_firmware()

if __name__ == '__main__':
    unittest.main()
