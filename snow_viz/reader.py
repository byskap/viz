import struct
import serial
from cobs import cobs
from typing import Generator, Tuple, List

# struct ImuData {
#     tmp: f32,       // 4 bytes
#     acc: [f64; 3],  // 24 bytes
#     gyro: [f64; 3], // 24 bytes
# }
# // Total payload: 52 bytes + 1 byte COBS overhead + 1 byte delimiter

class SerialReader:
    def __init__(self, port: str = '/dev/ttyACM0', baud: int = 115200):
        self.port = port
        self.baud = baud
        self.ser = None
        self.buffer = bytearray()

    def __enter__(self):
        self.ser = serial.Serial(self.port, self.baud, timeout=1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def read_data(self) -> Generator[Tuple[float, List[float], List[float]], None, None]:
        if not self.ser:
            raise RuntimeError("Serial port not opened. Use as a context manager.")

        while True:
            byte = self.ser.read(1)
            if byte == b'':
                continue

            if byte == b'\x00':
                if self.buffer:
                    try:
                        # 1. Remove COBS framing
                        raw_binary_data = cobs.decode(self.buffer)
                        
                        # 2. Unpack the bytes
                        # '<' = Little Endian
                        # 'f' = 32-bit float (tmp)
                        # 'd' = 64-bit float (acc[3], gyro[3])
                        # Payload: 4 (f32) + 24 ([f64; 3]) + 24 ([f64; 3]) = 52 bytes
                        data = struct.unpack('<fdddddd', raw_binary_data)
                        
                        temp = data[0]
                        acc = list(data[1:4])
                        gyro = list(data[4:7])
                        
                        yield temp, acc, gyro
                        
                    except Exception as e:
                        print(f"Decode Error: {e}")
                    
                    self.buffer.clear()
            else:
                self.buffer.extend(byte)
