"""
Usage:
  # From tensorflow/models/
  # Create train data:
  python generate_tfrecord.py --csv_input=images/train_labels.csv --image_dir=images/train --output_path=train.record

  # Create test data:
  python generate_tfrecord.py --csv_input=images/test_labels.csv  --image_dir=images/test --output_path=test.record
"""
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import cv2
import pandas as pd
from tqdm import tqdm
import tensorflow.compat.v1 as tf

from PIL import Image
from utils import dataset_util
from collections import namedtuple, OrderedDict

flags = tf.app.flags
flags.DEFINE_string('csv_input', '', 'Path to the CSV input')
flags.DEFINE_string('image_dir', '', 'Path to the image directory')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

def raise_excep(error_msg):
    Ex = ValueError()
    Ex.strerror = error_msg
    raise Ex

def class_text_to_int(row_label):
    if row_label == 'firstclass':
        return 1
    elif row_label == 'secondclass':
        return 2
        ...
    elif row_label == 'fourthclass':
        return 4
    else:
        raise_excep(f"THIS CLASS {row_label} DOES NOT EXIST")

def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]

def verify_boundaries(val):
    if val > 1:
        return 1.0
    if val < 0:
        return 0.0
    return val


def create_tf_example(group, path):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size
    _, ext = os.path.splitext(path)

    filename = group.filename.encode('utf8')
    image_format = ext.encode('utf8')
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for _, row in group.object.iterrows():
        xmins.append(verify_boundaries(row['xmin'] / width))
        xmaxs.append(verify_boundaries(row['xmax'] / width))
        ymins.append(verify_boundaries(row['ymin'] / height))
        ymaxs.append(verify_boundaries(row['ymax'] / height))
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main(_):
    path = os.path.join(os.getcwd(), FLAGS.image_dir)
    examples = pd.read_csv(FLAGS.csv_input)
    data = split(examples, 'filename')
    chunks = [data[x:x+20] for x in range(0, len(data), 20)]
    chunk_index = 0
    os.makedirs("tfrecords", exist_ok=True)
    for chunk in tqdm(chunks):
        tfrecord_path, _ = os.path.splitext(FLAGS.output_path)
        writer = tf.python_io.TFRecordWriter(f"{tfrecord_path}_{chunk_index:05}.tfrecord")
        for el in chunk:
            tf_example = create_tf_example(el, path)
            writer.write(tf_example.SerializeToString())

        writer.close()
        chunk_index += 1

    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    print('Successfully created the TFRecords: {}'.format(output_path))


if __name__ == '__main__':
    tf.app.run()
