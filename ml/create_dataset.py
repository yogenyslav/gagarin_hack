import cv2
import numpy as np
import random
import ffmpeg
import subprocess
from pathlib import Path
import os
import pandas as pd


def get_frame(idx: int, fps: int, src: str, dst: str):
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

    command = (
        ffmpeg.input(src)
        .output(
            f"{dst}/frame-{idx}.bin",
            format="h264",
            ss=f"{start_min}:{start_sec}",
            t=f"{end_min}:{end_sec}",
            vframes=fps,
        )
        .overwrite_output()
        .compile()
    )
    subprocess.run(command)


def process_source(src: str, dst: str):
    probe = ffmpeg.probe(src)
    video_info = next(s for s in probe["streams"] if s["codec_type"] == "video")
    fps = int(video_info["r_frame_rate"].split("/")[0])
    num_frames = int(video_info["nb_frames"])

    frames_to_read = list(range(num_frames // fps))
    for idx in frames_to_read:
        get_frame(idx, fps, src, dst)


def select_chunk(
    chunk_duration: int,
    video_duration: int,
) -> tuple[int, int]:
    chunk_start = random.randint(0, video_duration - chunk_duration - 1)
    chunk_end = chunk_start + chunk_duration
    return chunk_start, chunk_end


def get_frame_rate(video_file):

    probe = ffmpeg.probe(video_file)

    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )

    if video_stream is not None and "r_frame_rate" in video_stream:
        frame_rate = video_stream["r_frame_rate"]
        return int(frame_rate.split("/")[0])
    else:
        return None


def select_anomaly_subchunk(
    chunk_start: int,
    chunk_end: int,
    anomaly_duration: int,
) -> tuple[int, int]:
    anomaly_start = random.randint(chunk_start, chunk_end - anomaly_duration - 1)
    anomaly_end = anomaly_start + anomaly_duration
    return anomaly_start, anomaly_end


def apply_specific_highlight(frame, highlight_intensity):
    highlighted_frame = cv2.addWeighted(
        frame, 1 + highlight_intensity / 10, np.zeros(frame.shape, frame.dtype), 0, 0
    )
    return highlighted_frame


def apply_specific_blur(frame, blur_intensity):
    kernel_size = (blur_intensity * 2 + 1, blur_intensity * 2 + 1)
    blurred_frame = cv2.GaussianBlur(frame, kernel_size, 0)
    return blurred_frame


def apply_specific_crop(frame, crop_width, crop_height, start_x, start_y):

    # Crop the frame
    cropped_frame = frame[
        start_y : start_y + crop_height, start_x : start_x + crop_width
    ]

    # Upscale cropped frame to match initial width and height of the frame
    upscaled_frame = cv2.resize(
        cropped_frame, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST
    )

    return upscaled_frame


def generate_noise_image(shape):
    noise = np.random.randint(0, 255, shape, dtype=np.uint8)
    return noise


def apply_specific_overlap(frame, radius, center_x, center_y, noise_image):
    overlay = frame.copy()
    height, width = frame.shape[0], frame.shape[1]

    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, 255, -1)
    cv2.circle(overlay, (center_x, center_y), radius, 0, -1)
    circle_filled_with_noise = cv2.bitwise_and(noise_image, noise_image, mask=mask)
    blurred_circle = cv2.GaussianBlur(
        circle_filled_with_noise, (21, 21), random.randint(10, 20)
    )

    cv2.addWeighted(blurred_circle, 1, overlay, 1, 0, frame)

    return frame


def apply_anomaly(video_capture, out, anomaly_start, anomaly_end, type, fps):
    video_duration = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) // fps
    anomaly_duration = anomaly_end - anomaly_start
    intensity = random.randint(20, 30)

    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    crop_width = random.randint(frame_width // 3, frame_width // 2)
    crop_height = random.randint(frame_height // 3, frame_height // 2)
    noise_image = generate_noise_image((frame_height, frame_width, 3))
    start_x = (
        random.randint(0, frame_width - crop_width)
        if type == "crop"
        else random.randint(0, frame_width)
    )
    start_y = (
        random.randint(0, frame_height - crop_height)
        if type == "crop"
        else random.randint(0, frame_height)
    )
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    radius = random.randint(frame_width // 4, frame_width // 2)
    anomalies = []
    for frame_number in range(video_duration * fps):
        success, frame = video_capture.read()
        if frame_number >= anomaly_start * fps and frame_number <= anomaly_end * fps:
            if type == "blur":
                processed_frame = apply_specific_blur(frame, blur_intensity=intensity)
            elif type == "highlight":
                processed_frame = apply_specific_highlight(
                    frame, highlight_intensity=intensity
                )
            elif type == "crop":
                processed_frame = apply_specific_crop(
                    frame,
                    crop_width=crop_width,
                    crop_height=crop_height,
                    start_x=start_x,
                    start_y=start_y,
                )
            elif type == "overlap":
                processed_frame = apply_specific_overlap(
                    frame,
                    radius,
                    start_x,
                    start_y,
                    noise_image,
                )
            else:
                processed_frame = frame

            out.write(processed_frame)

        else:
            out.write(frame)

    for i in range(video_duration):
        if anomaly_start <= i < anomaly_end:
            anomalies.append(1)
        else:
            anomalies.append(0)
    # Создание DataFrame
    df = pd.DataFrame(
        {
            "filename": [f"frame-{i}.bin" for i in range(video_duration)],
            "anomaly": anomalies,
        }
    )

    return df


def create_new_cap_from_end(cap, start_seconds, end_seconds, fps):
    # Get total frames and frame rate of the original capture
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = fps
    # Calculate the frame indices corresponding to start and end times
    start_frame = int(start_seconds * frame_rate)
    end_frame = int(end_seconds * frame_rate)
    # Create a new video writer with the same properties as the original capture
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"H264")  # Define the codec for MP4 format

    new_cap = cv2.VideoWriter(f"new_capture.mp4", fourcc, frame_rate, (width, height))
    # Set the frame position to the start frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    for i in range(start_frame, end_frame + 1):
        ret, frame = cap.read()
        if not ret:
            break
        new_cap.write(frame)
    new_cap.release()
    new_cap = cv2.VideoCapture(f"new_capture.mp4")
    return new_cap


def create_directories(
    output_dir,
    n_chunks,
    n_subchunks,
):

    for i in range(n_chunks):
        for j in range(n_subchunks):
            (Path(output_dir) / f"chunk{i}" / f"subchunk{j}").mkdir(
                parents=True, exist_ok=True
            )


def process_one_chunk(
    chunk_start,
    chunk_end,
    video_capture,
    chunk_duration,
    anomaly_duration,
    type,
    out_path,
    fps,
):

    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    new_cap = create_new_cap_from_end(video_capture, chunk_start, chunk_end, fps)
    out = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*"H264"),
        fps,
        (frame_width, frame_height),
    )
    anomaly_start, anomaly_end = select_anomaly_subchunk(
        0, (chunk_end - chunk_start), anomaly_duration
    )
    df = apply_anomaly(new_cap, out, anomaly_start, anomaly_end, type, fps)
    out.release()
    new_cap.release()
    return df


def process_one_video(
    input_path: str,
    output_path: str,
    n_chunks: int,
    n_subchunks: int,
    chunk_duration: int,
    anomaly_duration: int,
    type: str,
):
    cap = cv2.VideoCapture(input_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    output_path = Path(output_path)
    create_directories(output_path, n_chunks, n_subchunks)
    filenames = []
    anomalies = []
    video_duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // fps
    for i in range(n_chunks):
        chunk_start, chunk_end = select_chunk(chunk_duration, video_duration)
        for j in range(n_subchunks - 1):
            subchunk_path = output_path / f"chunk{i}" / f"subchunk{j}" / f"{i}_{j}.mp4"
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            df = process_one_chunk(
                chunk_start,
                chunk_end,
                cap,
                chunk_duration,
                anomaly_duration,
                type,
                str(subchunk_path),
                fps,
            )
            # df.to_csv(subchunk_path.parent / "labels.csv", index=False)
            df["filename"] = df["filename"].apply(
                lambda x: str(subchunk_path.parent) + "/" + x
            )
            filenames += list(df["filename"])
            anomalies += list(df["anomaly"])
            process_source(subchunk_path, subchunk_path.parent)
            os.remove(subchunk_path)
        subchunk_path = (
            output_path
            / f"chunk{i}"
            / f"subchunk{n_subchunks - 1}"
            / f"{i}_{n_subchunks - 1}.mp4"
        )
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        df = process_one_chunk(
            chunk_start,
            chunk_end,
            cap,
            chunk_duration,
            0,
            type,
            str(subchunk_path),
            fps,
        )
        # df.to_csv(subchunk_path.parent / "labels.csv", index=False)
        df["filename"] = df["filename"].apply(
            lambda x: str(subchunk_path.parent) + "/" + x
        )
        filenames += list(df["filename"])
        anomalies += list(df["anomaly"])

        process_source(subchunk_path, subchunk_path.parent)
        os.remove(subchunk_path)
    final_df = pd.DataFrame({"filename": filenames, "anomaly": anomalies})
    # final_df.to_csv(output_path / "labels.csv", index=False)
    os.remove(Path(__file__).parent / "new_capture.mp4")
    return final_df


if __name__ == "__main__":
    input_path = Path("./Train/not_anomaly/")
    outp_path = Path("./final_dataset/")
    N_CHUNKS = 10
    N_SUBCHUNKS = 4
    CHUNK_DURATION = 10
    ANOMALY_DURATION = 3

    anomalies_types = ["highlight", "blur"]

    type_df = pd.DataFrame()
    for type in anomalies_types:
        type_output = outp_path / type
        mp4_files = [file for file in os.listdir(input_path) if file.endswith(".mp4")]

        for file in mp4_files:
            filename = file.split(".mp4")[0]
            tmp_output_path = type_output / filename
            tmp_output_path.mkdir(parents=True, exist_ok=True)
            print(tmp_output_path)
            input_file = input_path / file
            tmp_df = process_one_video(
                str(input_file),
                str(tmp_output_path),
                N_CHUNKS,
                N_SUBCHUNKS,
                CHUNK_DURATION,
                ANOMALY_DURATION,
                type,
            )
            mapping = {0: "normal", 1: type}
            tmp_df["anomaly"] = tmp_df["anomaly"].map(mapping)
            type_df = pd.concat([type_df, tmp_df]).reset_index(drop=True)
    type_df.to_csv(outp_path / "labels.csv", index=False)
