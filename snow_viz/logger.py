import rerun as rr
import rerun.blueprint as rrb
from typing import List

class RerunLogger:
    def __init__(self, application_id: str = "snow"):
        self.application_id = application_id

    def connect(self):
        rr.init(self.application_id)
        rr.connect_grpc()
        self._setup_blueprint()

    def _setup_blueprint(self):
        blueprint = rrb.Blueprint(
            rrb.Vertical(
                rrb.TimeSeriesView(
                    origin="logs/temp", 
                    name="Temperature",
                    axis_y=rrb.ScalarAxis(range=(-5, 30))
                ),
                rrb.Horizontal(
                    rrb.TimeSeriesView(
                        origin="logs/accel", 
                        name="Accelerometer (m/s²)",
                        axis_y=rrb.ScalarAxis(range=(-20, 20))
                    ),
                    rrb.TimeSeriesView(
                        origin="logs/gyro", 
                        name="Gyroscope (dps)",
                        axis_y=rrb.ScalarAxis(range=(-500, 500))
                    ),
                ),
            ),
        )
        rr.send_blueprint(blueprint)

    def log_imu(self, temp: float, acc: List[float], gyro: List[float]):
        # Set time to current (default in SDK if not specified, 
        # but maintaining user preference for explicit time if needed)
        # However, rr.set_time is usually global.
        
        # Accelerometer
        rr.log("logs/accel/x", rr.Scalars(acc[0]))
        rr.log("logs/accel/y", rr.Scalars(acc[1]))
        rr.log("logs/accel/z", rr.Scalars(acc[2]))

        # Gyroscope
        rr.log("logs/gyro/x", rr.Scalars(gyro[0]))
        rr.log("logs/gyro/y", rr.Scalars(gyro[1]))
        rr.log("logs/gyro/z", rr.Scalars(gyro[2]))

        # Temperature
        rr.log("logs/temp", rr.Scalars(temp))
