import os

import Diarization
from Tripartite import tripartite, makedir



# 為video,audio,text都創一個新視頻的記錄文檔
def makedirs(path_list, num):
    for path in path_list:
        makedir(f"{path}/video{num}")


def main():
    input_path = "L:/year3_sem1/SA/video_image/split/video"
    output_path = "L:/year3_sem1/SA/video_image/split/transcript"
    makedir(output_path)
    makedir(f"{output_path}/handle")

    split_path = ["video", "audio", "text"]
    video_path = f"{output_path}/{split_path[0]}"
    audio_path = f"{output_path}/{split_path[1]}"
    text_path = f"{output_path}/{split_path[2]}"
    for i in split_path:
        makedir(f"{output_path}/{i}")
    path_list = [video_path, audio_path, text_path]

    Diarization.configurate()

    video_list = os.listdir(input_path)
    num = 1
    for video in video_list:
        original_video_path = f"{input_path}/{video}"
        Diarization.speakerDiarization(original_video_path, output_path, num)
        makedirs(path_list, num)
        tripartite(f"{input_path}/{video}", output_path, path_list, num)
        num += 1


if __name__ == '__main__':
    main()
