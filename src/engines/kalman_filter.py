"""
1D Recursive Kalman Filter for Telemetry Sensor Noise Rejection
eRTMAC-NWIS | Oil India Limited (OIL)

Eliminates transient sensor spikes, mud motor pulsation noise, and top-drive vibration
to keep telemetry false alarms below 5%.
"""

from typing import Dict, Any


class TelemetryKalmanFilter:
    """
    1D discrete Kalman filter maintaining estimated true latent state and covariance.
    """

    def __init__(self, process_variance: float = 1e-3, measurement_variance: float = 0.08):
        self.q = process_variance       # Process variance (how fast true value changes)
        self.r = measurement_variance   # Measurement variance (sensor noise level)
        
        # State trackers for key sensor metrics
        self.states: Dict[str, Dict[str, float]] = {
            "torque_knm": {"x": 18.4, "p": 1.0},
            "rop_mph": {"x": 14.2, "p": 1.0},
            "flow_in_gpm": {"x": 520.0, "p": 1.0},
            "flow_out_gpm": {"x": 520.0, "p": 1.0},
            "spp_psi": {"x": 2850.0, "p": 5.0},
            "ecd_ppg": {"x": 11.85, "p": 0.1}
        }

    def update_sensor(self, metric: str, measurement: float) -> float:
        """
        Executes Kalman predict and update cycle on a single measurement.
        """
        if metric not in self.states:
            self.states[metric] = {"x": measurement, "p": 1.0}

        x = self.states[metric]["x"]
        p = self.states[metric]["p"]

        # 1. Predict
        p_prior = p + self.q

        # 2. Update (Kalman Gain)
        k_gain = p_prior / (p_prior + self.r)
        x_posterior = x + k_gain * (measurement - x)
        p_posterior = (1.0 - k_gain) * p_prior

        self.states[metric]["x"] = x_posterior
        self.states[metric]["p"] = p_posterior

        return round(float(x_posterior), 2)

    def filter_telemetry_packet(self, raw_telemetry: Dict[str, float]) -> Dict[str, float]:
        """
        Filters all continuous channels in an incoming telemetry packet.
        """
        filtered = dict(raw_telemetry)
        for key in ["torque_knm", "rop_mph", "flow_in_gpm", "flow_out_gpm", "spp_psi", "ecd_ppg"]:
            if key in raw_telemetry:
                filtered[key] = self.update_sensor(key, float(raw_telemetry[key]))
        return filtered
