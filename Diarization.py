import os
from ffmpeg_split import call_command
from pathlib import Path
import torch
from Tripartite import makedir


def configurate():
    call_command("pip install pydub")
    call_command("pip install light-the-torch")
    call_command("ltt install torch torchvision torchaudio")
    call_command("pip install  git+https://github.com/hmmlearn/hmmlearn.git")
    call_command("pip install  git+https://github.com/pyannote/pyannote-audio.git@develop")
    call_command("pip install git+https://github.com/openai/whisper.git")


# @markdown Enter the URL of the YouTube video, or the path to the video/audio file you want to transcribe, give the output path, etc. and run the cell. HTML file embeds the video for YouTube, and audio for media files.

video_path = "L:/year3_sem1/SA/video_image/split/video/3000277524.mp4"  # @param {type:"string"}
# @markdown ---
output_path = "L:/year3_sem1/SA/video_image/split/transcript"  # @param {type:"string"}
output_path = str(Path(output_path))
# @markdown ---
# @markdown #### **Title for transcription of media file**
audio_title = "Sample Order Taking"  # @param {type:"string"}
# @markdown ---
# @markdown #### Copy a token from your [Hugging Face tokens page](https://huggingface.co/settings/tokens) and paste it below.
access_token = "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"  # @param {type:"string"}


# @markdown ---
# @markdown **Run this cell again if you change the video.**


def speakerDiarization(video_path, output_path, num):
    import locale

    locale.getpreferredencoding = lambda: "UTF-8"

    # 儲存處理中產生的文件
    makedir(f"{output_path}/handle/video{num}")

    input_wav_path = f"{output_path}/handle/video{num}"

    call_command(f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 -y {input_wav_path}/input.wav")

    # Prepending spacer
    from pydub import AudioSegment

    spacermilli = 2000
    spacer = AudioSegment.silent(duration=spacermilli)
    audio = AudioSegment.from_wav(f"{input_wav_path}/input.wav")
    audio = spacer.append(audio, crossfade=0)
    audio.export(f'{input_wav_path}/input_prep.wav', format='wav')

    # Pyannote's Diarization
    from pyannote.audio import Pipeline

    # accept the user conditions on both hf.co/pyannote/speaker-diarization and hf.co/pyannote/segmentation.
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=(access_token) or True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipeline.to(device)

    DEMO_FILE = {'uri': 'blabla', 'audio': f'{input_wav_path}/input_prep.wav'}
    dz = pipeline(DEMO_FILE)

    with open(f"{input_wav_path}/diarization.txt", "w") as text_file:
        text_file.write(str(dz))

    # Preparing audio files according to the diarization
    def millisec(timeStr):
        spl = timeStr.split(":")
        s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2])) * 1000)
        return s

    import re

    dzs = open(f'{input_wav_path}/diarization.txt').read().splitlines()

    groups = []
    g = []
    lastend = 0

    for d in dzs:
        if g and (g[0].split()[-1] != d.split()[-1]):  # same speaker
            groups.append(g)
            g = []

        g.append(d)

        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
        end = millisec(end)
        if lastend > end:  # segment engulfed by a previous segment
            groups.append(g)
            g = []
        else:
            lastend = end
    if g:
        groups.append(g)

    audio = AudioSegment.from_wav(f"{input_wav_path}/input_prep.wav")
    gidx = -1
    for g in groups:
        start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
        start = millisec(start)  # - spacermilli
        end = millisec(end)  # - spacermilli
        gidx += 1
        audio[start:end].export(f"{input_wav_path}/{str(gidx)}.wav", format='wav')

    # import webvtt
    from datetime import timedelta
    import whisper
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model('large', device=device)
    import json
    for i in range(len(groups)):
        audiof = f"{input_wav_path}/{str(i)}.wav"
        result = model.transcribe(audio=audiof, language='en',
                                  word_timestamps=True)  # , initial_prompt=result.get('text', ""))
        with open(f"{input_wav_path}/{str(i)}.json", "w") as outfile:
            json.dump(result, outfile, indent=4)

    def timeStr(t):
        return '{0:02d}:{1:02d}:{2:06.2f}'.format(round(t // 3600),
                                                  round(t % 3600 // 60),
                                                  t % 60)

    txt = list("")
    gidx = -1
    for g in groups:
        shift = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        shift = millisec(shift) - spacermilli  # the start time in the original video
        shift = max(shift, 0)
        gidx += 1
        captions = json.load(open(f"{input_wav_path}/{str(gidx)}.json"))['segments']

        if captions:
            speaker = g[0].split()[-1]

        for c in captions:
            start = shift + c['start'] * 1000.0
            start = start / 1000.0  # time resolution ot youtube is Second.
            end = (shift + c['end'] * 1000.0) / 1000.0
            txt.append(f'[{timeStr(start)} --> {timeStr(end)}] [{speaker}] {c["text"]}\n')

    with open(f"{input_wav_path}/capspeaker{num}.txt", "w", encoding='utf-8') as file:
        s = "".join(txt)
        file.write(s)



