import pandas as pd

from Tripartite import makedir
from feat import Detector
import json
import pandas as pd
import numpy as np
import re

import os

import sys

#
# os.environ["JAVA_HOME"] = "C:/Users/Administrator/Java/jdk-1.8"
# os.environ['PYSPARK_PYTHON'] = sys.executable
# os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
# os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages com.databricks:spark-xml_2.11:0.4.1 pyspark-shell'
# # os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


# import sparknlp
# import pyspark.sql.functions as F
#
# from pyspark.ml import Pipeline
# from pyspark.sql import SparkSession
# from E:/year3_sem1/SA/video_image/splitsparknlp.annotator import *
# from sparknlp.base import *
# from sparknlp.pretrained import PretrainedPipeline
# from pyspark.sql.types import StringType, IntegerType

path = "/transcript/video/3000147510/SPEAKER_01/3000147510_1_(000013-000036).mp4"


# def start():
#     builder = SparkSession.builder \
#         .appName("Spark NLP Licensed") \
#         .master("local[*]") \
#         .config("spark.driver.memory", "15G") \
#         .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
#         .config("spark.kryoserializer.buffer.max", "2000M") \
#         .config("spark.jars", "/year3_sem1/SA/video_image/split/spark-nlp-assembly-5.1.3.jar")
#     return builder.getOrCreate()


def analyseVideo(path, skip_frames):
    detector = Detector(
        face_model="retinaface",
        landmark_model="mobilefacenet",
        au_model='xgb',
        emotion_model="resmasknet",
        facepose_model="img2pose",
    )
    emotion_list = ["anger", "disgust", "fear", "happiness", "sadness", "surprise", "neutral"]

    video_prediction = detector.detect_video(path, skip_frames=skip_frames)
    emotions = video_prediction.emotions
    #emotions.dropna(axis=0, how="all")
    video_emotion_lst = []
    for index, row in emotions.iterrows():
        num = 0
        max_confidence = row["anger"]
        emotion = "anger"

        for number in row:
            if number > max_confidence:
                max_confidence = number
                emotion = emotion_list[num]
            num += 1
        video_emotion_lst.append(emotion)

    emotions.loc[:, "video"] = video_emotion_lst
    time = os.path.splitext(path)[0].split('_')[-1]
    time_lst = [time for i in range(emotions.shape[0])]
    emotions.loc[:, "time"] = time_lst
    #emotions.loc[:, "index"] = int(path.split("/")[-1].split("_")[1])
    print(emotions)

    return emotions[["time", "video"]]


# # text
# def run_pipeline(text, results):
#     model = "bert_sequence_classifier_emotion"
#     spark = start()
#     document_assembler = DocumentAssembler() \
#         .setInputCol('text') \
#         .setOutputCol('document')
#
#     tokenizer = Tokenizer() \
#         .setInputCols(['document']) \
#         .setOutputCol('token')
#
#     sequenceClassifier = PerceptronModel.load("/year3_sem1/SA/video_image/split/Emotion_Detection_Classifier/") \
#         .setInputCols(['token', 'document']) \
#         .setOutputCol('pred_class')
#
#     # french_pos = PerceptronModel.load("/year3_sem1/SA/video_image/split/Emotion_Detection_Classifier/")
#     # PipelineModel.load("/year3_sem1/SA/video_image/split/Emotion_Detection_Classifier/")
#
#     pipeline = Pipeline(
#         stages=[
#             document_assembler,
#             tokenizer,
#             sequenceClassifier])
#
#     df = spark.createDataFrame(text, StringType()).toDF("text")
#     results[model] = (pipeline.fit(df).transform(df))


def analyseText(path):
    with open(path, "r", encoding='utf-8') as file:
        txt = file.read()
    results = {}
    run_pipeline(txt, results)

    for model_name, result in zip(results.keys(), results.values()):
        res = result.select(F.explode(F.arrays_zip(result.document.result,
                                                   result.pred_class.result,
                                                   result.pred_class.metadata)).alias("col")) \
            .select(F.expr("col['1']").alias("prediction"),
                    F.expr("col['2']").alias("confidence"),
                    F.expr("col['0']").alias("sentence"))

        prediction = res.collect()[0][0]
        return prediction


def bubble(lst):
    n = len(lst)
    for i in range(n):
        for j in range(0, n-i-1):
            index_j = int(lst[j].split("_")[1])
            index_j1 = int(lst[j+1].split("_")[1])
            if index_j > index_j1:
                temp = lst[j]
                lst[j] = lst[j+1]
                lst[j+1] = temp


def findSpeaker(path):
    speaker_path_dic = {}
    handle_path = f"{path}/transcript/handle"
    video_lst = os.listdir(handle_path)
    for video in video_lst:
        specific_video_path = f"{handle_path}/{video}"
        with open(f"{specific_video_path}/Interviewee_Cap.txt", 'r') as f:
            answer = f.read()
            f.close()
        pattern = r'\[SPEAKER_\d{2}]\s-\sInterviewee'
        match = re.search(pattern, answer)
        interviewee = match.group()[1:11]
        speaker_path_dic[video] = interviewee
    return speaker_path_dic


def getSpeaker(path, speaker_dic, channel):
    channel_paths = []
    handle_speaker_lst = os.listdir(f"{path}/transcript/{channel}")
    for i in handle_speaker_lst:
        speaker = speaker_dic[i]
        channel_paths.append(f"{path}/transcript/{channel}/{speaker}")
    return channel_paths


def analyzeVideos(path):
    result_path = f"{path}/result"
    makedir(result_path)

    speaker_path_dic = findSpeaker(path)
    video_paths = getSpeaker(path, speaker_path_dic, "video")
    for video_path in video_paths:
        video_lst = os.listdir(video_path)
        bubble(video_lst)
        final = analyseVideo(f"{video_path}/{video_lst[0]}", 24)
        for video in video_lst[1:]:
            specific_video_path = f"{video_path}/{video}"
            result = analyseVideo(specific_video_path, 24)
            final = pd.concat([final, result], axis=0, ignore_index=True)
        video_name = os.path.splitext(video_lst[0])[0].split("_")[0]
        final.to_csv(f"{result_path}/{video_name}.csv")


analyzeVideos("E:/year3_sem1/SA/video_image/split")
