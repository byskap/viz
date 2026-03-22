import argparse
from datetime import datetime
import rerun as rr
from serial_parser.reader import SerialReader

def main():
    parser = argparse.ArgumentParser(description="Rerun Logger for serial data")
    parser.add_argument("--port", type=str, default="/dev/tty.usbmodem21103", help="Serial port")
    parser.add_argument("--baud", type=int, default=460800, help="Baud rate")
    parser.add_argument("--output", "-o", type=str, help="Output RRD file name (default: auto-generated timestamp)")
    args = parser.parse_args()

    filename = args.output
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.rrd"

    print(f"Connecting to {args.port} at {args.baud} baud...")
    
    try:
        with SerialReader(port=args.port, baud=args.baud) as reader:
            print(f"Writing Rerun log to {filename}... (Press Ctrl+C to stop)")
            
            rr.init("logger")
            rr.save(filename)
            
            rr.log(
                "logs/ego", 
                rr.Boxes3D(half_sizes=[0.5, 0.2, 0.1], colors=[255, 0, 0]), 
                static=True
            )
            
            count = 0
            try:
                for data in reader.read_data():
                    loop_time = data.get("loop_time", 0.0)
                    accel = data.get("accel", [0.0, 0.0, 0.0])
                    gyro = data.get("gyro", [0.0, 0.0, 0.0])
                    mag = data.get("mag", [0.0, 0.0, 0.0])
                    ego = data.get("ego", [0.0, 0.0, 0.0, 1.0])
                    pos = data.get("pos", [0.0, 0.0, 0.0])
                    is_stationary = data.get("is_stationary", 0) > 0
                    
                    hz = 1000.0 / loop_time if loop_time > 0 else 0.0
                    rr.log("logs/hz", rr.Scalars(hz))
                    rr.log("logs/hz_text", rr.TextDocument(f"# {hz:.1f} Hz  | Stationary: {'YES' if is_stationary else 'NO'}"))

                    rr.log("logs/accel/x", rr.Scalars(accel[0]))
                    rr.log("logs/accel/y", rr.Scalars(accel[1]))
                    rr.log("logs/accel/z", rr.Scalars(accel[2]))
                    rr.log("logs/accel/is_stationary", rr.Scalars(1.0 if is_stationary else 0.0))

                    rr.log("logs/gyro/x", rr.Scalars(gyro[0]))
                    rr.log("logs/gyro/y", rr.Scalars(gyro[1]))
                    rr.log("logs/gyro/z", rr.Scalars(gyro[2]))

                    rr.log("logs/mag/x", rr.Scalars(mag[0]))
                    rr.log("logs/mag/y", rr.Scalars(mag[1]))
                    rr.log("logs/mag/z", rr.Scalars(mag[2]))

                    rr.log("logs/ego", rr.Transform3D(translation=pos, rotation=rr.Quaternion(xyzw=ego)))

                    count += 1
                    if count % 100 == 0:
                        print(f"\rLogged {count} messages...", end="", flush=True)
            except KeyboardInterrupt:
                print("\nStopped by user.")

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
