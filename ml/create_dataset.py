import cv2
import numpy as np
import random
import ffmpeg
import subprocess
from pathlib import Path
import os
import pandas as pd


def get_frame(idx: int, fps: int, src: str, dst: str):
    """
    Convert video to binary frames

    Args:
        idx (int): id of the frame
        fps (int): framerate of the video
        src (str): path to video
        dst (str): path to the result file
    """
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
    """
    Convert video to binary frames

    Args:
        src (str): path to the video
        dst (str): path to the result file
    """
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
    """
    Select random chunk from video


    Args:
        chunk_duration (int): chunk duration
        video_duration (int): video duration

    Returns:
        tuple[int, int]: start and stop of chunk
    """
    chunk_start = random.randint(0, video_duration - chunk_duration - 1)
    chunk_end = chunk_start + chunk_duration
    return chunk_start, chunk_end


def select_anomaly_subchunk(
    chunk_start: int,
    chunk_end: int,
    anomaly_duration: int,
) -> tuple[int, int]:
    """
    Select subchunk inside chunk

    Args:
        chunk_start (int): beginning of chunk
        chunk_end (int): end of chunk
        anomaly_duration (int): duration of anomal part in subchunk

    Returns:
        tuple[int, int]: start and stop of subchunk in seconds
    """
    anomaly_start = random.randint(chunk_start, chunk_end - anomaly_duration - 1)
    anomaly_end = anomaly_start + anomaly_duration
    return anomaly_start, anomaly_end


def apply_specific_highlight(frame, highlight_intensity: int):
    """
    Apply highlight anomaly to frame

    Args:
        frame: cv2 frame
        highlight_intensity (int): highlight intencity

    Returns:
        processed cv2 frame
    """

    highlighted_frame = cv2.addWeighted(
        frame, 1 + highlight_intensity / 10, np.zeros(frame.shape, frame.dtype), 0, 0
    )
    return highlighted_frame


def apply_specific_blur(frame, blur_intensity: int):
    """
    Apply blur anomaly to frame

    Args:
        frame: cv2 frame
        blur_intensity (int): blur intencity

    Returns:
        processed cv2 frame
    """
    kernel_size = (blur_intensity * 2 + 1, blur_intensity * 2 + 1)
    blurred_frame = cv2.GaussianBlur(frame, kernel_size, 0)
    return blurred_frame


def apply_specific_crop(
    frame, crop_width: int, crop_height: int, start_x: int, start_y: int
):
    """
    Apply crop anomaly to frame

    Args:
        frame: cv2 frame
        crop_width (int): crop width
        crop_height (int): crop height
        start_x (int): initial x-coord of crop
        start_y (int): initial y-coord of crop

    Returns:
        processed cv2 frame
    """

    cropped_frame = frame[
        start_y : start_y + crop_height, start_x : start_x + crop_width
    ]

    upscaled_frame = cv2.resize(
        cropped_frame, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST
    )

    return upscaled_frame


def generate_noise_image(shape):
    """
    Generate noised image

    Args:
        shape: shape of target image

    Returns:
        noised image
    """
    noise = np.random.randint(0, 255, shape, dtype=np.uint8)
    return noise


def apply_specific_overlap(
    frame, radius: int, center_x: int, center_y: int, noise_image
):
    """
    Apply overlap anomaly to frame

    Args:
        frame: cv2 frame
        radius (int): radius of overlapping circle
        center_x (int): center of overlapping circle
        center_y (int): center of overlapping circle
        noise_image: noized image (circle filling)

    Returns:
        processed cv2 frame
    """

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


def apply_anomaly(
    video_capture, out, anomaly_start: int, anomaly_end: int, type: str, fps: int
) -> pd.DataFrame:
    """
    Apply anomaly to video capture

    Args:
        video_capture: cv2 video capture
        out: cv2 video writer
        anomaly_start (int): start of anomaly (in seconds)
        anomaly_end (int): end of anomaly (in seconds)
        type (str): type of anomaly to be applied
        fps (int): fps of capture

    Returns:
        (pd.DataFrame) dataframe with labeling
    """
    video_duration = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) // fps
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

    df = pd.DataFrame(
        {
            "filename": [f"frame-{i}.bin" for i in range(video_duration)],
            "anomaly": anomalies,
        }
    )

    return df


def create_new_cap_from_end(cap, start_seconds: int, end_seconds: int, fps: int):
    """
    Create new cap from start and end in seconds

    Args:
        cap: initial cv2 video capture
        start_seconds (int): start of new capture in seconds
        end_seconds (int): end of new capture in seconds
        fps (int): framerate

    Returns:
        new cv2 video capture
    """

    frame_rate = fps

    start_frame = int(start_seconds * frame_rate)
    end_frame = int(end_seconds * frame_rate)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"avc1")

    new_cap = cv2.VideoWriter(f"new_capture.mp4", fourcc, frame_rate, (width, height))

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
    output_dir: str,
    n_chunks: int,
    n_subchunks: int,
):
    """
    Generate directories structure for dataset

    Args:
        output_dir (str): output directory
        n_chunks (int): number of chunks
        n_subchunks (int): number of subchunks
    """

    for i in range(n_chunks):
        for j in range(n_subchunks):
            (Path(output_dir) / f"chunk{i}" / f"subchunk{j}").mkdir(
                parents=True, exist_ok=True
            )


def process_one_chunk(
    chunk_start: int,
    chunk_end: int,
    video_capture,
    chunk_duration: int,
    anomaly_duration: int,
    type: str,
    out_path: str,
    fps: int,
) -> pd.DataFrame:
    """
    Process one chunk of video capture

    Args:
        chunk_start (int): start of chunk in seconds
        chunk_end (int): end of chunk in seconds
        video_capture: cv2 video capture
        chunk_duration (int): chunk duration in seconds
        anomaly_duration (int): anomaly duration in seconds
        type (str): type of anomaly to be generated
        out_path (str): output dir
        fps (int): framerate of video capture

    Returns:
        (pd.DataFrame): labels dataframe
    """

    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    new_cap = create_new_cap_from_end(video_capture, chunk_start, chunk_end, fps)
    out = cv2.VideoWriter(
        out_path,
        cv2.VideoWriter_fourcc(*"avc1"),
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
) -> pd.DataFrame:
    """
    Process one video

    Args:
        input_path (str): path to video to be processed
        output_path (str): path to dataset to be saved
        n_chunks (int): number of chunks
        n_subchunks (int): number of subchunks
        chunk_duration (int): chunk duration in seconds
        anomaly_duration (int): anomaly duration in seconds
        type (str): type of anomaly to be applied

    Returns:
        pd.DataFrame: labeling dataframe
    """
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
    # пример генерации датасета
    input_path = Path("./data/Train/not_anomaly/")
    outp_path = Path("./data/final_dataset2/")
    N_CHUNKS = 10
    N_SUBCHUNKS = 4
    CHUNK_DURATION = 10
    ANOMALY_DURATION = 3

    anomalies_types = ["highlight", "blur", "crop", "overlap"]

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
