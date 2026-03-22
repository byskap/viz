import struct
import serial
from cobs import cobs
from typing import Generator, Tuple, List


class SerialReader:
    def __init__(self, port: str = "/dev/ttyACM0", baud: int = 115200):
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

    def read_data(
        self,
    ) -> Generator[Tuple[float, List[float], List[float]], None, None]:
        if not self.ser:
            raise RuntimeError("Serial port not opened. Use as a context manager.")

        while True:
            # Read until COBS delimiter
            raw_packet = self.ser.read_until(b"\x00")
            if not raw_packet or raw_packet == b"\x00":
                continue

            try:
                # 2. Decode (strip the \x00)
                pkt = cobs.decode(raw_packet[:-1])

                # 3. Unpack based on your 76-byte Rust struct (Q3f3f3f4f3fI)
                data = struct.unpack("<Q3f3f3f4f3fI", pkt)

                yield {
                    "loop_time": data[0],
                    "accel": data[1:4],
                    "gyro": data[4:7],
                    "mag": data[7:10],
                    "ego": data[10:14],
                    "pos": data[14:17],
                    "is_stationary": data[17],
                }


            except Exception as e:
                print(f"Decoding error: {e}")
                continue
