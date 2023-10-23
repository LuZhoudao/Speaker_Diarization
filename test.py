import os
import pandas as pd
path = "E:/year3_sem1/SA/video_image/split/transcript/video/3000141124/SPEAKER_00/3000141124_0_(000000-000008).mp4"
#E:\year3_sem1\SA\video_image\split\transcript\video\3000141124\SPEAKER_00
df = pd.DataFrame([1,2,3,4])
df["Time"] = os.path.splitext(path)[0].split('_')[-1]
print(df)
print(path.split("/"))
