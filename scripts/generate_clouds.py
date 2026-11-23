import cv2
import numpy as np
from pathlib import Path

def generate_earth_clouds():
    W, H = 2048, 1024
    print(f"Generating realistic Earth clouds texture ({W}x{H})...")

    # Generate multi-scale Perlin-like fractal noise
    np.random.seed(42)
    clouds = np.zeros((H, W), dtype=np.float32)

    # Octaves of noise with spherical scaling
    octaves = [
        (16, 8, 0.40),
        (32, 16, 0.25),
        (64, 32, 0.18),
        (128, 64, 0.10),
        (256, 128, 0.05),
        (512, 256, 0.02),
    ]

    for fx, fy, weight in octaves:
        # Base random noise with wrapping on x
        raw = np.random.rand(fy, fx).astype(np.float32)
        # Periodic boundary in X for seamless wrap
        raw_padded = np.pad(raw, ((0, 0), (2, 2)), mode='wrap')
        upscaled = cv2.resize(raw_padded, (W + int(4 * W / fx), H), interpolation=cv2.INTER_CUBIC)
        upscaled = upscaled[:, int(2 * W / fx) : int(2 * W / fx) + W]
        clouds += upscaled * weight

    # Planetary circulation modulation
    latitudes = np.linspace(-np.pi / 2, np.pi / 2, H).reshape(-1, 1)
    
    # 1. Intertropical Convergence Zone (ITCZ) near equator (-10 to +10 deg)
    itcz = np.exp(-((latitudes - 0.08) ** 2) / 0.035)
    
    # 2. Mid-latitude storm tracks (35 to 60 deg N and S)
    mid_lat_n = np.exp(-((latitudes - 0.75) ** 2) / 0.08)
    mid_lat_s = np.exp(-((latitudes + 0.75) ** 2) / 0.08)
    
    # 3. Subtropical desert dry zones (15 to 30 deg N/S have fewer clouds)
    dry_zone_n = 1.0 - 0.45 * np.exp(-((latitudes - 0.35) ** 2) / 0.04)
    dry_zone_s = 1.0 - 0.45 * np.exp(-((latitudes + 0.35) ** 2) / 0.04)

    circulation = (0.2 + 0.55 * itcz + 0.45 * (mid_lat_n + mid_lat_s)) * dry_zone_n * dry_zone_s
    circulation = np.repeat(circulation, W, axis=1)

    # Combine noise and circulation
    clouds = clouds * 0.5 + circulation * 0.5

    # Swirling cyclones (cyclonic vortex swirls in mid latitudes)
    x_coords = np.linspace(0, 2 * np.pi, W).reshape(1, -1)
    wave1 = 0.12 * np.sin(x_coords * 3 + latitudes * 4)
    wave2 = 0.08 * np.sin(x_coords * 5 - latitudes * 3)
    clouds += wave1 + wave2

    # Contrast stretch and thresholding for realistic cumulus clusters
    clouds = np.clip((clouds - 0.36) / 0.42, 0.0, 1.0)
    # Apply soft S-curve
    clouds = clouds * clouds * (3.0 - 2.0 * clouds)
    clouds_img = (clouds * 255.0).astype(np.uint8)

    # Seamless horizontal blending on edges (last 64 pixels)
    blend_w = 64
    alpha = np.linspace(0, 1, blend_w).reshape(1, -1)
    blended_strip = (clouds_img[:, :blend_w].astype(float) * alpha + clouds_img[:, -blend_w:].astype(float) * (1.0 - alpha)).astype(np.uint8)
    clouds_img[:, :blend_w] = blended_strip
    clouds_img[:, -blend_w:] = blended_strip

    out_path = Path("web/assets/earth_clouds.jpg")
    cv2.imwrite(str(out_path), clouds_img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"Saved {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    generate_earth_clouds()
