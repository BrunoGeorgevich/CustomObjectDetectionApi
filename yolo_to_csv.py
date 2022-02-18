from tqdm import tqdm
from glob import glob
import pandas as pd
import argparse
import cv2
import os

def raise_excep(error_msg):
    Ex = ValueError()
    Ex.strerror = error_msg
    raise Ex

def class_int_to_text(row_label):
    if row_label == 1:
        return 'firstclass'
    elif row_label == 2:
        return 'secondclass'
        ...
    elif row_label == 4:
        return 'fourthclass'
    else:
        raise_excep(f"THIS CLASS {row_label} DOES NOT EXIST")

def process(path):
    yolo_list = []
    for filepath in tqdm(glob(os.path.join(path , '*.txt'))):
        with open(filepath, "r") as file:
            for row in file.read().split("\n"):
                
                row = row.strip()
                if len(row) == 0: continue
                
                c, x, y, w, h = row.split(" ")
                c = int(c)
                x, y, w, h = float(x), float(y), float(w), float(h)
                filename,_ = os.path.splitext(filepath)
                image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
                image_exists = False
                for ext in image_extensions:
                    imagename = f"{filename}{ext}"
                    if os.path.exists(imagename):
                        image_exists = True
                        break
                
                if not image_exists:
                    raise_excep(f"IMAGEM PARA A ANOTAÇÃO {filename} NÃO EXISTE!")

                img_h, img_w, _ = cv2.imread(imagename).shape
                yolo_list.append((imagename, class_int_to_text(c), (x - w/2) * img_w, (x + w/2) * img_w, (y - h/2) * img_h, (y + h/2) * img_h))
    return yolo_list

def yolo_to_csv(subfolders, folder):
    yolo_list = []

    if subfolders is None or len(subfolders) == 0:
        yolo_list += process(folder)
        column_name = ['filename', 'class', 'xmin', 'xmax', 'ymin', 'ymax']
        yolo_df = pd.DataFrame(yolo_list, columns=column_name)
        return yolo_df

    for subfolder in subfolders:
        yolo_list += process(os.path.join(subfolder, folder))
        column_name = ['filename', 'class', 'xmin', 'xmax', 'ymin', 'ymax']
    yolo_df = pd.DataFrame(yolo_list, columns=column_name)
    return yolo_df

parser = argparse.ArgumentParser(description='Convert .xml files into .csv.')
parser.add_argument('-f','--folders', required=True, type=str, help='The folders that will be used in the convertion.')
args = parser.parse_args()

subfolders = args.folders.split(',')

for folder in ['train','test']:
	xml_df = yolo_to_csv(subfolders, folder)
	xml_df.to_csv(f"{folder}_labels.csv", index=None)
	print('Successfully converted xml to csv.')

