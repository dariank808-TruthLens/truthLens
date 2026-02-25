import numpy as np

def normalize(value, scale=1.0):
    return min(value / scale, 1.0)

def compute_ai_probability(metrics):
    # rough scaling constants (tune later)
    v = normalize(metrics["velocity"], 5)
    a = normalize(metrics["acceleration"], 5)
    d = normalize(metrics["divergence"], 5)
    l = normalize(metrics.get("lens_distortion", 0), 0.1)
    c = normalize(metrics.get("chromatic_aberration", 0), 0.1)
    r = normalize(metrics.get("rolling_shutter", 0), 0.1)
    b = normalize(metrics.get("blur_variance", 0), 0.1)

    combined = (0.4 * v) + (0.4 * a) + (0.2 * d)

    return float(1 / (1 + np.exp(-5 * (combined - 0.5))))
