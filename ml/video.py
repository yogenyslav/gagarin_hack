import subprocess

import ffmpeg


def save_bin(src: str, out: str, idx: int, fps: int):
    start_sec = f"0{idx}"
    start_min = f"0{idx // 60}"
    if idx >= 60:
        start_sec = f"{idx % 60}"
        start_min = f"{idx // 60}"
    elif idx >= 10:
        start_sec = f"{idx}"

    end_sec = f"0{idx + 1}"
    end_min = f"0{(idx + 1) // 60}"
    if idx >= 59:
        end_sec = f"{(idx + 1) % 60}"
        end_min = f"{(idx + 1) // 60}"
    elif idx >= 9:
        end_sec = f"{idx + 1}"

    bin_name = f"{out}/frame-{idx}.bin"

    command = (
        ffmpeg.input(src)
        .output(
            bin_name,
            format="h264",
            ss=f"{start_min}:{start_sec}",
            t=f"{end_min}:{end_sec}",
            vframes=fps,
            loglevel='error',
        )
        .overwrite_output()
        .compile()
    )
    subprocess.run(command)

    return bin_name
