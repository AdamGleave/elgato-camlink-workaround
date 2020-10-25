#!/usr/bin/env python3

import logging
import os
import re
import subprocess
import time
from typing import Tuple

TIME_DELAY = 1.0  # in seconds

WORKING_INPUT_PIX_FMTS = {
    # Pixel formats that (a) Elgato Cam Link declares as supported; (b) actually work.
    # They vary based on resolution (this may be specific to my camera, Sony A6500).
    (1920, 1080): "yuyv422",
    (3840, 2160): "nv12",
}
OUTPUT_PIX_FMT = "yuv420p"  # seems to be supported everywhere (Chrome, Zoom, etc)


def find_device(v4l2_output: str, name: str) -> str:
    v4l2_output = v4l2_output.split("\n")
    idx = None
    for i, line in enumerate(v4l2_output):
        if line.startswith(name):
            if idx is not None:
                raise ValueError(f"Found multiple devices named {name}")
            idx = i
    if idx is None:
        raise ValueError("Did not find a device named {name}")

    device_line = v4l2_output[idx + 1]
    device_path = device_line.strip()
    assert device_path.startswith("/dev"), device_path
    assert os.path.exists(device_path)
    return device_path


def find_video_settings(v4l2_output: str) -> Tuple[int, int, int]:
    v4l2_output = v4l2_output.split("\n")
    matches = [
        re.match(r"[.\n\t]*Size: Discrete ([0-9]+)x([0-9]+)", x) for x in v4l2_output
    ]
    matches = [(match[1], match[2]) for match in matches if match is not None]
    assert len(set(matches)) == 1, "resolution not unique"
    width, height = int(matches[0][0]), int(matches[0][1])

    matches = [
        re.match(r"[.\n\t]*Interval: Discrete [0-9\.]+s \(([0-9\.]+) fps\)", x)
        for x in v4l2_output
    ]
    matches = [match[1] for match in matches if match is not None]
    fps = float(matches[0])

    return width, height, fps


def setup_loopback() -> None:
    v4l2_output = subprocess.check_output(["v4l2-ctl", "--list-devices"]).decode()
    dummy_device = find_device(v4l2_output, "Dummy video device (0x0000)")
    elgato_device = find_device(v4l2_output, "Cam Link 4K: Cam Link 4K")

    elgato_info = subprocess.check_output(
        ["v4l2-ctl", "--list-formats-ext", "-d", elgato_device]
    ).decode()
    width, height, fps = find_video_settings(elgato_info)

    pix_fmt = WORKING_INPUT_PIX_FMTS[(width, height)]
    try:
        args = [
            "ffmpeg",
            "-f",
            "v4l2",
            "-framerate",
            str(fps),
            "-pix_fmt",
            pix_fmt,
            "-video_size",
            f"{width}x{height}",
            "-i",
            elgato_device,
            "-f",
            "v4l2",
            "-vcodec",
            "rawvideo",
            "-pix_fmt",
            OUTPUT_PIX_FMT,
            dummy_device,
        ]
        logging.info("Executing: %s", args)
        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        logging.warning("ffmpeg terminated abnormally: %s", e)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    while True:
        setup_loopback()
        time.sleep(TIME_DELAY)


if __name__ == "__main__":
    main()
