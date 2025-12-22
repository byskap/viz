import serial
import struct
from cobs import cobs

PORT = '/dev/ttyACM0' 
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
buffer = bytearray()

print("Listening for Snow data...")

# Total payload: 52 bytes + 1 byte COBS overhead + 1 byte delimiter
# struct ImuData {
#     tmp: f32,       // 4 bytes
#     acc: [f64; 3],  // 24 bytes
#     gyro: [f64; 3], // 24 bytes
# }


while True:
    byte = ser.read(1)

    if byte == b'':
        continue

    if byte == b'\x00':
        if buffer:
            try:
                # 1. Remove COBS framing
                raw_binary_data = cobs.decode(buffer)
                
                # 2. Unpack the bytes
                # '<' = Little Endian
                # 'f' = 32-bit float (x6)
                data = struct.unpack('<fffffffffffff', raw_binary_data)
                
                tmp = data[0]
                acc = data[1:4]
                gyro = data[4:7]
                print(f"Tmp: {tmp} | Acc: {acc} | Gyro: {gyro}")
                
            except Exception as e:
                print(f"Decode Error: {e}")
            
            buffer.clear()
    else:
        buffer.extend(byte)