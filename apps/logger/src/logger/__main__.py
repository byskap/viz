import argparse
import json
import time
from datetime import datetime
from mcap.writer import Writer
from serial_parser.reader import SerialReader

def main():
    parser = argparse.ArgumentParser(description="MCAP Logger for serial data")
    parser.add_argument("--port", type=str, default="/dev/tty.usbmodem21103", help="Serial port")
    parser.add_argument("--baud", type=int, default=460800, help="Baud rate")
    parser.add_argument("--output", "-o", type=str, help="Output MCAP file name (default: auto-generated timestamp)")
    args = parser.parse_args()

    filename = args.output
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.mcap"

    schema = {
        "type": "object",
        "title": "SensorData",
        "properties": {
            "loop_time": {"type": "number"},
            "accel": {"type": "array", "items": {"type": "number"}},
            "gyro": {"type": "array", "items": {"type": "number"}},
            "mag": {"type": "array", "items": {"type": "number"}},
            "ego": {"type": "array", "items": {"type": "number"}},
            "pos": {"type": "array", "items": {"type": "number"}},
            "is_stationary": {"type": "boolean"}
        }
    }

    print(f"Connecting to {args.port} at {args.baud} baud...")
    
    try:
        with SerialReader(port=args.port, baud=args.baud) as reader:
            print(f"Writing MCAP log to {filename}... (Press Ctrl+C to stop)")
            
            with open(filename, "wb") as f:
                writer = Writer(f)
                writer.start()

                schema_id = writer.register_schema(
                    name="eskf.SensorData",
                    encoding="jsonschema",
                    data=json.dumps(schema).encode("utf-8")
                )

                channel_id = writer.register_channel(
                    topic="/sensor_data",
                    message_encoding="json",
                    schema_id=schema_id
                )

                count = 0
                for data in reader.read_data():
                    # Map is_stationary to boolean for valid JSON
                    data["is_stationary"] = data["is_stationary"] > 0
                    
                    # current time in nanoseconds
                    now_ns = time.time_ns()
                    
                    writer.add_message(
                        channel_id=channel_id,
                        log_time=now_ns,
                        data=json.dumps(data).encode("utf-8"),
                        publish_time=now_ns
                    )
                    
                    count += 1
                    if count % 100 == 0:
                        print(f"\rLogged {count} messages...", end="", flush=True)

                writer.finish()

    except KeyboardInterrupt:
        print("\nStopped by user.")
        # File handles are closed by context managers
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
