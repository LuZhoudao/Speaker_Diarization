from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
import os
import pandas as pd

import videoHandler


def analyzeText(finbert, tokenizer, sentence):
    inputs = tokenizer(sentence, return_tensors="pt", padding=True)
    outputs = finbert(**inputs)[0]

    labels = {0: "neutral", 1: "positive", 2: "negative"}
    for idx, sent in enumerate(sentence):
        emotion = labels[np.argmax(outputs.detach().numpy()[idx])]
    return emotion

def analyzeTexts():
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

    original_path = "E:/year3_sem1/SA/video_image/split"

    speaker_path_dic = videoHandler.findSpeaker(original_path)
    text_paths = videoHandler.getSpeaker(original_path, speaker_path_dic, "text")
    for text_path in text_paths:
        text_lst = sorted(os.listdir(text_path))
        text_name = text_path.split("/")[-2]
        other_data = pd.read_csv(f"{original_path}/result/{text_name}.csv").iloc[:, 1:]
        sentences = []
        for text in text_lst:
            specific_text_path = f"{text_path}/{text}"
            text_time = os.path.splitext(text)[0].split('_')[-1]
            with open(specific_text_path, "r", encoding='utf-8') as file:
                txt = file.read()
                sentences.append(txt)
                file.close()
            result = analyzeText(finbert, tokenizer, sentences)

            other_data.loc[(other_data.time == text_time), "text"] = result

        other_data.to_csv(f"{original_path}/result/{text_name}.csv")

analyzeTexts()


