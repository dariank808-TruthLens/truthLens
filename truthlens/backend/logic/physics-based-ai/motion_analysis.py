import cv2
import numpy as np

def compute_optical_flow(frames):
    flows = []

    for i in range(len(frames) - 1):
        flow = cv2.calcOpticalFlowFarneback(
            frames[i],
            frames[i + 1],
            None,
            0.5,
            3,
            15,
            3,
            5,
            1.2,
            0
        )
        flows.append(flow)

    return flows
