import os

import pandas as pd

import videoHandler
from emotion_recognition_using_speech_master.deep_emotion_recognition import DeepEmotionRecognizer
from emotion_recognition_using_speech_master.emotion_recognition import EmotionRecognizer
from sklearn.svm import SVC

from videoHandler import getSpeaker

# initialize instance
# inherited from emotion_recognition.EmotionRecognizer
# default parameters (LSTM: 128x2, Dense:128x2)

path = "E:/year3_sem1/SA/video_image/split/transcript/audio/3000141124/SPEAKER_01/3000141124_4_(000036-000113).wav"


def analyzeAudio(model5, model3, path):
    prediction5 = model5.predict(path)
    prediction3 = model3. predict(path)
    if prediction3 == "sad":
        prediction3 = "negative"
    elif prediction3 == "happy":
        prediction3 = "positive"
    else:
        prediction3 = "neutral"
    return prediction5, prediction3



def analyzeAudios():
    deeprec = DeepEmotionRecognizer(emotions=['angry', 'sad', 'neutral', 'ps', 'happy'], n_rnn_layers=2,
                                    n_dense_layers=2, rnn_units=128, dense_units=128)
    # train the model
    deeprec.train()

    my_model = SVC()
    rec = EmotionRecognizer(model=my_model, emotions=['sad', 'neutral', 'happy'], balance=True, verbose=0)
    rec.train()

    os.chdir("E:/year3_sem1/SA/video_image/split")
    original_path = "E:/year3_sem1/SA/video_image/split"

    speaker_path_dic = videoHandler.findSpeaker(original_path)
    audio_paths = videoHandler.getSpeaker(original_path, speaker_path_dic, "audio")
    for audio_path in audio_paths:
        audio_lst = sorted(os.listdir(audio_path))
        #analyzeAudio(deeprec, f"{audio_path}/{audio_lst[0]}")
        audio_name = audio_path.split("/")[-2]
        other_data = pd.read_csv(f"{original_path}/result/{audio_name}.csv").iloc[:, 1:]
        other_data.sort_values("Unnamed: 0", inplace=True)
        for audio in audio_lst:
            specific_audio_path = f"{audio_path}/{audio}"
            audio_time = os.path.splitext(audio)[0].split('_')[-1]
            result = analyzeAudio(deeprec, rec, specific_audio_path)
            #other_data["audio"] = None
            other_data.loc[(other_data.time == audio_time),"audio_5"] = result[0]
            other_data.loc[(other_data.time == audio_time), "audio_3"] = result[1]

        other_data.to_csv(f"{original_path}/result/{audio_name}.csv")




analyzeAudios()


# from emotion_recognition_using_speech_master.emotion_recognition import EmotionRecognizer
# from sklearn.svm import SVC
# my_model = SVC()
# # pass my model to EmotionRecognizer instance
# # and balance the dataset
# rec = EmotionRecognizer(model=my_model, emotions=['sad', 'neutral', 'happy'], balance=True, verbose=0)
# # train the model
# rec.train()
# #print(rec.confusion_matrix())
# print("Prediction:", rec.predict("E:/year3_sem1/SA/video_image/split/transcript/audio/3000141124/SPEAKER_01/3000141124_6_(000137-000224).wav"))
# # this is a sad speech from TESS from the testing set

