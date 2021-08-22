import serial
import sds011

def run() -> None:
    try:
        ser = serial.Serial('COM4', 9600) 
        ser.flushInput()
        sensor = sds011.SDS011(ser)
        print('Connected to SDS011 with id: ' + sensor.get_device_id())
        sensor.print_firmware()
        
        while True:
            sensor.read_and_decode_data()
            sensor.print_data()
            print('----------------------------')
            
    except KeyboardInterrupt:
        print('interrupted!')
        ser.close()
        
if __name__ == '__main__':
    run()