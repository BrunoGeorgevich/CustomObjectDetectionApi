# Object Detection Base

This repository was based on: [original github](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10)

## Steps
### 0. Set Environment Variables

- Linux

```shell
export PYTHONPATH=$PYTHONPATH:$PWD:$PWD/slim:$PWD/object_detection
```

- Windows
	- cmd
		```cmd
		set PYTHONPATH=%CD%;%CD%\slim;%CD%\object_detection
		```
	- powershell
		```powershell
		$env:PYTHONPATH = (Get-Item -Path ".\").FullName + ';' + (Get-Item -Path ".\slim").FullName + ';' + (Get-Item -Path ".\object_detection").FullName
		```

### 1. Choose the model

Tensorflow provides a series of pre-trained models: [model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md). 

### 2. Gather and Label Pictures

Retrieve the images and label them. 
Possible tools:
 - [LabelImg GitHub link](https://github.com/tzutalin/labelImg)
 - [CVAT GitHub link](https://github.com/openvinotoolkit/cvat)
 - [EVA GitHub link](https://github.com/Ericsson/eva)

### 3. Generate Training Data

First covert all the labeled data (.xml) into a .csv
```
python xml_to_csv.py [-f] 'folder1,folder2,...,folderN' -im images
```
Then, edit the **label_map.txt**, located in the training folder, with the classes of interest.
```
item {
  id: 1
  name: 'firstclass'
}

item {
  id: 2
  name: 'secondclass'
}

...

item {
  id: 4
  name: 'fourthclass'
}

```
After this, edit the **generate_tfrecord.py** with the same classes and ids of the **label_map.txt**.
```
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
```

If your annotation files are in the YOLO Format, edit the **yolo_to_csv.py** with the same classes and ids of the **label_map.txt**.
```
def class_int_to_text(row_label):
    if row_label == 1:
        return 'firstclass'
    elif row_label == 2:
        return 'secondclass'
        ...
    elif row_label == 'fourthclass':
        return 4
    else:
        raise_excep(f"THIS CLASS {row_label} DOES NOT EXIST")
```
Then, generate the TF_record files:
```
python generate_tfrecord.py --csv_input=images/train_labels.csv --image_dir=images/ --output_path=train.record
python generate_tfrecord.py --csv_input=images/test_labels.csv --image_dir=images/ --output_path=test.record
```

### 5. Configure training
Finally, its time to configure the training step.

First, you will edit the .config file that you choosed:

- Change num_classes to the number of different objects you want the classifier to detect. **Line 9**.

- Set the right path to the .ckpt file. **Line 110**.
 	- fine_tune_checkpoint : "*DOWNLOADED_PRETRAINED_MODEL_PATH*/model.ckpt"

- Set train input path to the train.record. **Line 126**.
	- input_path : ".../train.record"
	
- Set label map path to the training/labelmap.pbtxt. **Line 128**.
	- label_map_path: ".../training/labelmap.pbtxt"

- Change num_examples to the number of images you have in the \images\test directory. **Line 132**.


- Set test input path to the train.record. **Line 140**.
	- input_path : ".../test.record"
	
- Set label map path to the training/labelmap.pbtxt. **Line 142**.
	- label_map_path: ".../training/labelmap.pbtxt"

Save the file after the changes have been made. That’s it! The training job is all configured and ready to go!

### 6. Run the Training

Start the training:

```
python .\model_main_tf2.py --pipeline_config_path MODEL_DIR/pipeline.config --model_dir CKPT_OUTPUT_PATH --alsologtostderr
```

Start the evaluation:

```
python .\model_main_tf2.py --pipeline_config_path MODEL_DIR/pipeline.config --model_dir CKPT_OUTPUT_PATH  --checkpoint_dir CKPT_OUTPUT_PATH--alsologtostderr
```
To open the tensorboard:
```
tensorboard --logdir=results
```

### 7. Export Inference Graph

To export the model trained:

```
python .\exporter_main_v2.py --input_type image_tensor --pipeline_config_path MODEL_DIR\pipeline.config --trained_checkpoint_dir CKPT_OUTPUT_PATH --output_directory OUTPUT_DIR
```

### 8. Test Inference Graph

To export the model trained:

Process an image

```
python Object_detection_image.py --ckpt_model_path CKPT_OUTPUT_PATH --config_model_path MODEL_DIR/pipeline.config --image_path IMAGE_PATH
```

Process a video

```
python Object_detection_image.py --ckpt_model_path CKPT_OUTPUT_PATH --config_model_path MODEL_DIR/pipeline.config --video_path VIDEO_PATH
```
