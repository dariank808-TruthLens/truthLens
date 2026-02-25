from video_loader import extract_frames
from motion_analysis import compute_optical_flow
from physics_checks import (
    velocity_continuity_score,
    acceleration_spike_score,
    motion_divergence_score
)
from scorer import compute_ai_probability

def analyze_video(video_path):
    frames = extract_frames(video_path, frame_skip=5)
    flows = compute_optical_flow(frames)

    metrics = {
        "velocity": velocity_continuity_score(flows),
        "acceleration": acceleration_spike_score(flows),
        "divergence": motion_divergence_score(flows)
    }

    ai_prob = compute_ai_probability(metrics)

    return metrics, ai_prob


if __name__ == "__main__":
    video_path = "sample.mp4"
    metrics, probability = analyze_video(video_path)

    print("Physics Metrics:", metrics)
    print("AI Probability:", probability)
