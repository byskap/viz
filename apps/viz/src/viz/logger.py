import rerun as rr
import rerun.blueprint as rrb

class RerunLogger:
    def __init__(self, application_id: str = "viz"):
        self.application_id = application_id

    def connect(self):
        rr.init(self.application_id)
        rr.connect_grpc()
        self._setup_blueprint()

    def _setup_blueprint(self):
        blueprint = rrb.Blueprint(
            rrb.Vertical(
                rrb.TextDocumentView(
                    origin="logs/hz_text",
                    name="Frequency",
                ),
                rrb.Horizontal(
                    rrb.TimeSeriesView(
                        origin="logs/accel",
                        name="Accelerometer (m/s²)",
                    ),
                    rrb.TimeSeriesView(
                        origin="logs/gyro",
                        name="Gyroscope (dps)",
                    ),
                    rrb.TimeSeriesView(
                        origin="logs/mag",
                        name="Magnetometer (G)",
                    ),
                ),
                rrb.Spatial3DView(
                    origin="logs",
                    name="3D Visualization",
                ),
                row_shares=[.3, 1, 3],
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
        pos = data["pos"]
        is_stationary = data["is_stationary"] > 0

        # Frequency (Hz)
        hz = 1000.0 / loop_time if loop_time > 0 else 0.0
        rr.log("logs/hz", rr.Scalars(hz))
        rr.log("logs/hz_text", rr.TextDocument(f"# {hz:.1f} Hz  | Stationary: {'YES' if is_stationary else 'NO'}"))

        # Accelerometer
        rr.log("logs/accel/x", rr.Scalars(accel[0]))
        rr.log("logs/accel/y", rr.Scalars(accel[1]))
        rr.log("logs/accel/z", rr.Scalars(accel[2]))
        rr.log("logs/accel/is_stationary", rr.Scalars(1.0 if is_stationary else 0.0))

        # Gyroscope
        rr.log("logs/gyro/x", rr.Scalars(gyro[0]))
        rr.log("logs/gyro/y", rr.Scalars(gyro[1]))
        rr.log("logs/gyro/z", rr.Scalars(gyro[2]))

        # Magnetometer
        rr.log("logs/mag/x", rr.Scalars(mag[0]))
        rr.log("logs/mag/y", rr.Scalars(mag[1]))
        rr.log("logs/mag/z", rr.Scalars(mag[2]))

        # Egostate
        rr.log("logs/ego", rr.Transform3D(translation=pos, rotation=rr.Quaternion(xyzw=ego)))
