#!/usr/bin/env python3

from definitions import WorkingMode, ReportMode, Modifier, Frame, MessageType, Command
           
    
class SDS011:

    def __init__(self, serial):
        self.device_id = [255, 255]
        self.firmware = None
        self.serial = serial
        self.serial.flushInput()
        self.device_id = None
        self.data = {'PM2.5': 0.0, 'PM10': 0.0}
        self.last_command = b''
        self.last_reply = b''
        self.get_firmware_version()
    
    def read_message(self):
        header = 0
        while header != bytes([Frame.HEADER.value]):
            header = self.serial.read(size=1)
        message_type = self.serial.read(size=1)
        self.last_reply = header + message_type + self.serial.read(size=8)         
    
    def command_message_valid(self) -> bool:
        if len(self.last_command) == 19:
            if self.last_command[0] == Frame.HEADER.value and self.last_command[1] == MessageType.COMMAND.value and self.last_command[-1] == Frame.TAIL.value:
                if self.valid_checksum(self.last_command):
                    return True
        return False
    
    def reply_message_valid(self) -> bool:
        if len(self.last_reply) == 10:
            if self.last_reply[0] == Frame.HEADER.value and self.last_reply[-1] == Frame.TAIL.value:
                if self.last_reply[1] == MessageType.COMMAND_REPLY.value or self.last_reply[1] == MessageType.DATA.value:
                    if self.valid_checksum(self.last_reply):
                        return True
        return False
    
    def calculate_checksum(message_data) -> int:
        return sum(message_data) % 256
    
    def valid_checksum(self, message) -> bool:
        message_data = []
        for i in range(len(message[2:-2])):
            message_data.append(message[2+i])
        if SDS011.calculate_checksum(message_data) == message[-2]:
            return True
        else:
            return False
        
    def decode_data(self) -> None:
        if self.reply_message_valid():
            self.data['PM2.5'] = ((self.last_reply[3] << 8) + self.last_reply[2])/10
            self.data['PM10'] = ((self.last_reply[5] << 8) + self.last_reply[4])/10
            
    def read_and_decode_data(self):
        self.read_message()
        self.decode_data()
                    
    def print_firmware(self):
        firmware = 'Firmware (YY-MM-DD): ' 
        firmware += str(self.firmware['year']) + '-' 
        firmware += str(self.firmware['month']) + '-'
        firmware += str(self.firmware['day'])
        print(firmware)
        
    def print_data(self):
        print('Measured PM2.5 value is: ' + str(self.data['PM2.5']) + ' ug/m^3')
        print('Measured PM10  value is: ' + str(self.data['PM10']) + ' ug/m^3')
           
    def decode_device_id(self):
        if self.reply_message_valid():
            self.device_id = [self.last_reply[6], self.last_reply[7]]
            
    def get_device_id(self) -> str:
        return str(bytes(self.device_id).hex()).upper()
    
    def prepare_command(self, command: Command, data=[], device_id: [int, int] = [255, 255]):
        assert len(data) <= 12
        data += [0,]*(12-len(data)) + device_id
        command_message = [Frame.HEADER.value, MessageType.COMMAND.value, command.value]
        command_message += data
        command_message.append(SDS011.calculate_checksum([command.value] + data))
        command_message.append(Frame.TAIL.value)
        self.last_command = bytes(command_message)
        if not self.command_message_valid():
            self.last_command = None

    def polling_for_reply(self):
        for message_cont in range(10):
            self.read_message()
            if self.last_reply[2] == self.last_command[2]:
                break
            elif self.last_command[2] == Command.QUERY_DATA.value and self.last_reply[1] == MessageType.DATA.value:
                break
        else:
            raise TimeoutError('No reply received from sensor!')
    
    def write_and_wait_reply(self):
        if self.last_command:
            self.serial.write(self.last_command)
            self.polling_for_reply()
         
    def set_report_mode(self, report_mode: ReportMode, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.REPORT_MODE, 
                              [Modifier.SET.value, report_mode.value], 
                              device_id=device_id)
        self.write_and_wait_reply()
         
    def get_report_mode(self, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.REPORT_MODE, 
                              [Modifier.GET.value], 
                              device_id=device_id)
        self.write_and_wait_reply()
          
    def query_data(self, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.QUERY_DATA, 
                              [], 
                              device_id=device_id)
        self.write_and_wait_reply()
    
    def set_device_id(self, new_device_id: [int, int], device_id: [int, int] = [255, 255]):
        data = [0]*10 + new_device_id
        self.prepare_command(Command.SET_DEVICE_ID, 
                             data, 
                             device_id=device_id)
        self.write_and_wait_reply()
        self.decode_device_id()
        
    
    def set_working_mode(self, working_mode: WorkingMode, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.WORKING_MODE, 
                             [Modifier.SET.value, working_mode.value], 
                             device_id=device_id)
        self.write_and_wait_reply()
    
    def get_working_mode(self, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.WORKING_MODE, 
                             [Modifier.GET.value], 
                             device_id=device_id)
        self.write_and_wait_reply()
        
    def get_firmware_version(self, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.GET_FIRMWARE, 
                             [], 
                             device_id=device_id)
        self.write_and_wait_reply()
        self.firmware = {'year': self.last_reply[3], 
                         'month': self.last_reply[4], 
                         'day': self.last_reply[5]}
        self.decode_device_id()
        
    def set_working_period(self, working_period: int = 0, device_id: [int, int] = [255, 255]):
        # valid values 1 min to 30 min and 0 for continuous
        # work 30 seconds and sleep n*60-30 seconds】
        assert 0 <= working_period <= 30 
        self.prepare_command(Command.WORKING_PERIOD, 
                             [Modifier.SET.value, working_period], 
                             device_id=device_id) 
        self.write_and_wait_reply()
    
    def get_working_period(self, device_id: [int, int] = [255, 255]):
        self.prepare_command(Command.WORKING_PERIOD, 
                             [Modifier.GET.value], 
                             device_id=device_id)
        self.write_and_wait_reply()
