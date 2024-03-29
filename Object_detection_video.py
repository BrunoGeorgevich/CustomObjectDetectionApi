# %%
import os
from os.path import join
import argparse

from time import perf_counter

import cv2

from glob import glob
from random import choice

import pathlib
import matplotlib
import matplotlib.pyplot as plt

import io
import scipy.misc
import numpy as np
from six import BytesIO
from PIL import Image, ImageDraw, ImageFont

import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
# %%


def get_keypoint_tuples(eval_config):
    """Return a tuple list of keypoint edges from the eval config.

    Args:
      eval_config: an eval config containing the keypoint edges

    Returns:
      a list of edge tuples, each in the format (start, end)
    """
    tuple_list = []
    kp_list = eval_config.keypoint_edge
    for edge in kp_list:
        tuple_list.append((edge.start, edge.end))
    return tuple_list


def get_model_detection_function(model):
    """Get a tf.function for detection."""

    @tf.function
    def detect_fn(image):
        """Detect objects in image."""

        image, shapes = model.preprocess(image)
        prediction_dict = model.predict(image, shapes)
        detections = model.postprocess(prediction_dict, shapes)

        return detections, prediction_dict, tf.reshape(shapes, [-1])

    return detect_fn


# %%

parser = argparse.ArgumentParser(description='Convert .xml files into .csv.')
parser.add_argument('-m', '--ckpt_model_path', required=True,
                    type=str, help='Inference model CKPT path')
parser.add_argument('-c', '--config_model_path', required=True,
                    type=str, help='Inference model Config path')
parser.add_argument('-v', '--video_path', required=True,
                    type=str, help='Video path that will be processed')
args = parser.parse_args()

pipeline_config = args.config_model_pathos
model_dir = args.ckpt_model_path

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(pipeline_config)
model_config = configs['model']
detection_model = model_builder.build(
    model_config=model_config, is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(
    model=detection_model)
ckpt.restore(os.path.join(model_dir, 'ckpt-0')).expect_partial()

detect_fn = get_model_detection_function(detection_model)

label_map_path = configs['eval_input_config'].label_map_path
label_map = label_map_util.load_labelmap(label_map_path)
categories = label_map_util.convert_label_map_to_categories(
    label_map,
    max_num_classes=label_map_util.get_max_label_map_index(label_map),
    use_display_name=True)
category_index = label_map_util.create_category_index(categories)
label_map_dict = label_map_util.get_label_map_dict(
    label_map, use_display_name=True)
# %%
video_path = args.video_path
cap = cv2.VideoCapture(video_path)

while True:
    initial_time = perf_counter()
    ret, frame = cap.read()

    if not ret:
        break

    image_np = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    input_tensor = tf.convert_to_tensor(
        np.expand_dims(image_np, 0), dtype=tf.float32)
    detections, predictions_dict, shapes = detect_fn(input_tensor)

    label_id_offset = 1
    image_np_with_detections = image_np.copy()

    # Use keypoints if available in detections
    keypoints, keypoint_scores = None, None
    if 'detection_keypoints' in detections:
        keypoints = detections['detection_keypoints'][0].numpy()
        keypoint_scores = detections['detection_keypoint_scores'][0].numpy()

    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections['detection_boxes'][0].numpy(),
        (detections['detection_classes']
         [0].numpy() + label_id_offset).astype(int),
        detections['detection_scores'][0].numpy(),
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=200,
        min_score_thresh=.30,
        agnostic_mode=False,
        keypoints=keypoints,
        keypoint_scores=keypoint_scores)

    elapsed_time = perf_counter() - initial_time
    elapsed_time = 0.000001 if elapsed_time == 0 else elapsed_time
    print(f"FPS :: {1/elapsed_time:.2f} || TIME :: {elapsed_time:.2f}")

    cv2.imshow("Video", cv2.cvtColor(
        image_np_with_detections, cv2.COLOR_RGB2BGR))
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cv2.destroyAllWindows()
