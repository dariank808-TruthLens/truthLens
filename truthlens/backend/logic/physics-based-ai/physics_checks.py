import numpy as np
import cv2


def lens_distortion_score(frame):
    edges = cv2.Canny(frame, 100, 200)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is None:
        return 0.5  # no lines detected

    curvature_scores = []

    h, w = frame.shape
    center_x = w / 2
    center_y = h / 2

    for line in lines:
        x1, y1, x2, y2 = line[0]

        # distance from center
        d1 = np.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
        d2 = np.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)

        # if line near edges but perfectly straight → suspicious
        if max(d1, d2) > 0.7 * max(w, h):
            curvature_scores.append(1)

    if len(curvature_scores) == 0:
        return 0

    return float(np.mean(curvature_scores))

def chromatic_aberration_score(frame_color):
    b, g, r = cv2.split(frame_color)

    edges = cv2.Canny(cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY), 100, 200)

    shift_rg = np.mean(np.abs(r.astype(float) - g.astype(float))[edges > 0])
    shift_gb = np.mean(np.abs(g.astype(float) - b.astype(float))[edges > 0])

    score = (shift_rg + shift_gb) / 255.0
    return float(score)

def rolling_shutter_score(flow):
    vertical_gradient = np.gradient(flow[:, :, 0])[0]
    skew_score = np.mean(np.abs(vertical_gradient))
    return float(skew_score)

def blur_variance_score(frame):
    laplacian = cv2.Laplacian(frame, cv2.CV_64F)
    variance = laplacian.var()

    return float(1 / (variance + 1e-6))



def velocity_continuity_score(flows):
    if len(flows) < 2:
        return 0

    diffs = []

    for i in range(len(flows) - 1):
        v1 = flows[i]
        v2 = flows[i + 1]

        diff = np.mean(np.abs(v2 - v1))
        diffs.append(diff)

    return float(np.mean(diffs))

def acceleration_spike_score(flows):
    if len(flows) < 3:
        return 0

    spikes = []

    for i in range(len(flows) - 2):
        a1 = flows[i+1] - flows[i]
        a2 = flows[i+2] - flows[i+1]

        jerk = np.mean(np.abs(a2 - a1))
        spikes.append(jerk)

    return float(np.mean(spikes))

def motion_divergence_score(flows):
    divergences = []

    for flow in flows:
        dx = np.gradient(flow[:, :, 0])[1]
        dy = np.gradient(flow[:, :, 1])[0]
        divergence = np.mean(np.abs(dx + dy))
        divergences.append(divergence)

    return float(np.mean(divergences))

