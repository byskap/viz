import rerun as rr
import rerun.blueprint as rrb
import random
import time

def main():
    # Initialize the recording
    rr.init("snow")
    rr.connect_grpc()

    # 1. Define the Blueprint (Layout)
    # This creates a vertical stack of two separate graphs
    blueprint = rrb.Blueprint(
        rrb.Vertical(
            rrb.TimeSeriesView(origin="logs/accel", name="Accelerometer"),
            rrb.TimeSeriesView(origin="logs/gyro", name="Gyroscope"),
        ),
    )
    
    # Send the layout configuration to the viewer
    rr.send_blueprint(blueprint)

    print("Streaming data to Rerun...")

    try:
        while True:
            # Set the custom timeline (equivalent to set_time in Rust)
            # Python's time.time() returns seconds as float
            current_time = time.time()
            rr.set_time("time", duration=current_time)

            log_xyz("logs/accel")
            log_xyz("logs/gyro")

            time.sleep(0.02) # 20ms

    except KeyboardInterrupt:
        print("Stopped.")

def log_xyz(base_path: str):
    # Generate random values similar to the glam::Vec3 logic
    x = random.uniform(-1.0, 1.0)
    y = random.uniform(-1.0, 1.0)
    z = random.uniform(-1.0, 1.0)

    # Logging individual components
    # Rerun Python SDK automatically handles the scalar conversion
    rr.log(f"{base_path}/x", rr.Scalars(x))
    rr.log(f"{base_path}/y", rr.Scalars(y))
    rr.log(f"{base_path}/z", rr.Scalars(z))

if __name__ == "__main__":
    main()