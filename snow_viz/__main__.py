import argparse
import time
from .reader import SerialReader
from .logger import RerunLogger


def main():
    parser = argparse.ArgumentParser(description="Snow IMU Visualization")
    parser.add_argument("--port", type=str, default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate")
    args = parser.parse_args()

    logger = RerunLogger()
    logger.connect()

    print(f"Connecting to {args.port} at {args.baud} baud...")

    try:
        with SerialReader(port=args.port, baud=args.baud) as reader:
            print("Listening for Snow data... (Press Ctrl+C to stop)")
            for temp, acc, gyro, mag in reader.read_data():
                logger.log_imu(temp, acc, gyro, mag)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
