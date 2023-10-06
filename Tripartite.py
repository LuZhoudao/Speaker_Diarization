import os, sys
import ffmpeg_split


def makedir(new_path):
    if not os.path.exists(new_path):
        os.makedirs(new_path)


def makedirInAllFiles(speaker, path_list, num):
    """當有新的speaker,為三個種類文檔都創一個新的speaker文件 """
    if not os.path.exists(f"{path_list[0]}/video{num}/{speaker}"):
        for path in path_list:
            makedir(f"{path}/video{num}/{speaker}")


def splitText(new_lines, num, file_name, path_list):
    index = 0
    for line in new_lines:
        start_time = line[0]
        end_time = line[1]
        speaker = line[2]
        txt = line[-1]
        makedirInAllFiles(speaker, path_list, num)
        with open(f"{path_list[2]}/video{num}/{speaker}/{file_name}_{index}_({start_time.replace(':', '')}-{end_time.replace(':', '')}).txt", "w", encoding='utf-8') as file:
            file.write(txt)

        index += 1


def tripartite(file_path, output_path, path_list, num):
    file_name = os.path.splitext(file_path)[0].split("/")[-1]
    with open(f"{output_path}/handle/video{num}/capspeaker{num}.txt", 'r') as f:
        lines = f.readlines()

    # 處理txt原文件
    new_lines = []
    speaker = ""
    for j in range(len(lines)):
        line = lines[j]
        start_time = ffmpeg_split.to_hms_str(line[1:13])
        end_time = ffmpeg_split.to_hms_str(line[18:29])
        last_speaker = speaker
        speaker = line[33:line.rfind(']')]
        txt = line[line.rfind(']') + 3:-1]
        new_line = [start_time, end_time, speaker, txt]
        if speaker == last_speaker:
            new_lines[-1][1] = end_time
            new_lines[-1][-1] += f" {txt}"
        else:
            new_lines.append(new_line)

    splitText(new_lines, num, file_name, path_list)
    ffmpeg_split.splitVideo(new_lines, file_path,
                            f"{output_path}/video", num)
    ffmpeg_split.splitAudio(new_lines, file_path,
                            f"{output_path}/audio", num)
