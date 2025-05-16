import numpy as np
import json
from datetime import datetime

# GLOBAL CONSTANTS
C_e = 38000  # Carbon emission (ppm)
V = 6000     # Volume of room (m3)
q_i = [0.04583, 0.2597, 0.6514, 0.1389, 0.0027778]  # Quanta generation rate (per second)
B_0 = 0.65   # Initial breathing rate (per hour)

# TEST DATA
test_co2_in = [650, 660, 800, 680, 689, 680, 400, 700, 690, 700, 712, 713, 714, 715, 715, 716, 717, 710, 712, 712]
test_co2_out = [425, 430, 430, 426, 428, 420, 425, 415, 420, 425, 420, 430, 440, 430, 425, 410, 413, 417, 419, 450]
delta_t = 5   # Time interval (minutes)
total_t = 60  # Total time (minutes)
n = 15        # Number of people
N = 12        # Data points for analysis

# Data buffers
co2_in = []
co2_out = []

def vent_rate(N, n, B, co2_in, co2_out, delta_t):
    A, B_sum, C = 0, 0, 0
    for i in range(N):
        delta = co2_in[i] - co2_in[i-1] if i > 0 else co2_in[i]
        A += (B * C_e * delta) / (3600 * V * delta_t)
        B_sum += ((B * C_e) / (3600 * V)) ** 2
        C += (B * C_e * (co2_out[i] - co2_in[i])) / (3600 * V)
    return (A - (B_sum * n)) / C if C != 0 else 0

def breath_rate(N, n, lam, co2_in, co2_out, total_t):
    A = (co2_in[-1] - co2_in[0]) / total_t
    B = (co2_in[-1] - co2_out[-1]) * lam
    return ((A + B) * V) / (n * C_e)

def vent_rate_ss(N, n, B, co2_ss, co2_out):
    co2_out_avg = np.mean(co2_out)
    return (n * C_e * B) / (V * (co2_ss - co2_out_avg)) if (co2_ss - co2_out_avg) != 0 else 0

def infection_risk_calculation(lam, B, total_t):
    return [1 - np.exp(-((q * B) / (lam * V)) * total_t) for q in q_i]

# JSON Payload base
payload = {
    "source": "room308-esp32-gateway-teamF6",
    "local_time": "",
    "type": "data"
}

# Main processing loop
B_i = 0
lam = 0

for i in range(len(test_co2_in)):
    print(f"Loop {i}")
    co2_in_read = test_co2_in[i]
    co2_out_read = test_co2_out[i]

    if not co2_in or abs(co2_in_read - co2_in[0]) < 150:
        if len(co2_in) == N:
            co2_in.pop()
        co2_in.insert(0, co2_in_read)

    if not co2_out or abs(co2_out_read - co2_out[0]) < 150:
        if len(co2_out) == N:
            co2_out.pop()
        co2_out.insert(0, co2_out_read)

    if len(co2_in) == N and len(co2_out) == N:
        mean = np.mean(co2_in)
        std_dev = np.std(co2_in)

        if std_dev > 10:
            if B_i == 0:
                lam = vent_rate(N, n, B_0, co2_in, co2_out, delta_t)
                B_i = breath_rate(N, n, lam, co2_in, co2_out, total_t)
            else:
                lam = vent_rate(N, n, B_i, co2_in, co2_out, delta_t)
                B_i = breath_rate(N, n, lam, co2_in, co2_out, total_t)
        else:
            lam = vent_rate_ss(N, n, B_i, mean, co2_out)
            B_i = breath_rate(N, n, lam, co2_in, co2_out, total_t)

        infection_risk = infection_risk_calculation(lam, B_i, total_t)

        # Update payload
        payload.update({
            "local_time": datetime.now().isoformat(),
            "C02_Indoor_Average": co2_in_read,
            "PM2.5": 1000,
            "Gateway_AlphaVariant": infection_risk[0],
            "Delta_Variant": infection_risk[1],
            "Omicron_Variant": infection_risk[2],
            "Tuberculosis": infection_risk[3],
            "Rhinovirus": infection_risk[4],
            "Breathing_Rate": B_i,
            "Ventilation_Rate": lam
        })

        print("Payload:", json.dumps(payload, indent=2))