import argparse
import time
from serial_parser.reader import SerialReader
from .logger import RerunLogger


def main():
    # serialPort = "/dev/ttyACM0"
    serialPort = "/dev/tty.usbmodem21103"

    parser = argparse.ArgumentParser(description="Visualization")
    parser.add_argument("--port", type=str, default=serialPort, help="Serial port")
    parser.add_argument("--baud", type=int, default=460800, help="Baud rate")
    args = parser.parse_args()

    logger = RerunLogger()
    logger.connect()

    print(f"Connecting to {args.port} at {args.baud} baud...")

    try:
        with SerialReader(port=args.port, baud=args.baud) as reader:
            print("Listening for data... (Press Ctrl+C to stop)")
            for data in reader.read_data():
                logger.log(data)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
