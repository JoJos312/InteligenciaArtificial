#!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="VJSv9mO3pckff11vXSOj")
project = rf.workspace("yip-chun-kit-y2buh").project("emotion-recognition-yolo-v11-fyp-2")
version = project.version(3)
dataset = version.download("yolov11")
                