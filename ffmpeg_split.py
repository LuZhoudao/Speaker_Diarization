import os, sys


def call_command(cmd_content, call_path=None):
    """
    调用命令行
    call_path: 执行命令的目录
    """
    print(f"执行：{cmd_content}")
    import subprocess
    if call_path == None:
        this_file_dir_path = os.getcwd()
    # result = subprocess.run(f'ffmpeg -i video.m4s -i audio.m4s -codec copy {file_path}', shell=True, stdout=subprocess.PIPE, cwd=this_file_dir_path)
    return subprocess.run(cmd_content, shell=True, stdout=subprocess.PIPE, cwd=this_file_dir_path)


def get_video_seconds(filename):
    """
    pip install moviepy
    获取视频时长，返回的单位是秒（s:秒）,如果需要换算成时分秒，则调用time_convert()即可
    """
    from moviepy.editor import VideoFileClip
    video_clip = VideoFileClip(filename)
    duration = video_clip.duration
    video_clip.reader.close()
    video_clip.audio.reader.close_proc()
    print(f"{duration}-{type(duration)}")
    return duration


def to_hms_str(times):
    """
    转换为"时:分:秒"的形式的字符串
    """
    h = times[:2]
    m = times[3:5]
    s = times[7:9]
    if times[10] >= "5":
        s2 = int(times[8]) + 1
        s = f"{times[7]}{s2}"

    return f"{h}:{m}:{s}"


def splitVideo(split_list, video_path, output_path, video):
    index = 0
    for fragment in split_list:
        start_time = fragment[0]
        end_time = fragment[1]
        path_name, suffix = os.path.splitext(video_path)
        file_name = path_name.split("/")[-1]
        out_start_time = start_time
        out_end_time = end_time

        call_command(
            f'ffmpeg -i {video_path} -vcodec copy -an -ss {start_time} -to {end_time} {output_path}/{os.path.splitext(video)[0]}/{fragment[2]}/{file_name}_{index}_({out_start_time.replace(":", "")}-{out_end_time.replace(":", "")}){suffix} -y')
        index += 1


def splitAudio(split_list, video_path, output_path, video):
    index = 0
    for fragment in split_list:
        start_time = fragment[0]
        end_time = fragment[1]
        path_name, suffix = os.path.splitext(video_path)
        file_name = path_name.split("/")[-1]
        out_start_time = start_time
        out_end_time = end_time

        call_command(
            f'ffmpeg -i {video_path} -vn -acodec copy -ss {start_time} -to {end_time} {output_path}/{os.path.splitext(video)[0]}/{fragment[2]}/{file_name}_{index}_({out_start_time.replace(":", "")}-{out_end_time.replace(":", "")}).wav -y')
        index += 1



