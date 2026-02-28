import rerun as rr
import rerun.blueprint as rrb

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
                    origin="logs/loop_time",
                    name="Loop Time (ms)",
                    axis_y=rrb.ScalarAxis(range=(0, 100)),
                ),
                rrb.Horizontal(
                    rrb.TimeSeriesView(
                        origin="logs/accel",
                        name="Accelerometer (m/s²)",
                        axis_y=rrb.ScalarAxis(range=(-20, 20)),
                    ),
                    rrb.TimeSeriesView(
                        origin="logs/gyro",
                        name="Gyroscope (dps)",
                        axis_y=rrb.ScalarAxis(range=(-500, 500)),
                    ),
                    rrb.TimeSeriesView(
                        origin="logs/mag",
                        name="Magnetometer (G)",
                        axis_y=rrb.ScalarAxis(range=(-2, 2)),
                    ),
                ),
                rrb.Spatial3DView(
                    origin="logs/ego",
                    name="Egostate",
                    overrides={
                        "logs/ego": [
                            rrb.components.VisualizerOverride(["Transform3D"])
                        ]
                    }
                ),
            ),
        )

        rr.send_blueprint(blueprint)

        rr.log(
            "logs/ego", 
            rr.Boxes3D(half_sizes=[0.5, 0.2, 0.1], colors=[255, 0, 0]), 
            static=True
        )

    def log(self, data: dict):
        loop_time = data["loop_time"]
        accel = data["accel"]
        gyro = data["gyro"]
        mag = data["mag"]
        ego = data["ego"]

        # Loop Time
        rr.log("logs/loop_time", rr.Scalars(loop_time))

        # Accelerometer
        rr.log("logs/accel/x", rr.Scalars(accel[0]))
        rr.log("logs/accel/y", rr.Scalars(accel[1]))
        rr.log("logs/accel/z", rr.Scalars(accel[2]))

        # Gyroscope
        rr.log("logs/gyro/x", rr.Scalars(gyro[0]))
        rr.log("logs/gyro/y", rr.Scalars(gyro[1]))
        rr.log("logs/gyro/z", rr.Scalars(gyro[2]))

        # Magnetometer
        rr.log("logs/mag/x", rr.Scalars(mag[0]))
        rr.log("logs/mag/y", rr.Scalars(mag[1]))
        rr.log("logs/mag/z", rr.Scalars(mag[2]))

        # Egostate
        rr.log("logs/ego", rr.Transform3D(rotation=rr.components.RotationQuat(xyzw=ego)))
