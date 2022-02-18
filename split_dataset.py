#%%
from email.mime import base
from os.path import join, splitext, basename
from os import makedirs

import shutil

from random import sample
from glob import glob
from tqdm import tqdm

def change_to_txt(name):
    path, ext = splitext(name)
    path = path.replace("Images", "Annotations")
    return f"{path}.txt"

def diff(li1, li2):
    return list(set(li1) - set(li2)) + list(set(li2) - set(li1))

images = glob(join("dataset", "Images", "**", "*.*"), recursive=True)

train_images = sample(images, int(0.9 * len(images)))
train_annots = [change_to_txt(image) for image in train_images]

test_images = diff(images, train_images)
test_annots = [change_to_txt(image) for image in test_images]

makedirs(join("dataset", "train"), exist_ok=True)
for i, (annot, image) in tqdm(enumerate(zip(train_annots, train_images))):
    _, ext = splitext(image)
    shutil.copy2(image, join("dataset", "train", f"{i}{ext}"))
    shutil.copy2(annot, join("dataset", "train", f"{i}.txt"))
    
makedirs(join("dataset", "test"), exist_ok=True)
for i, (annot, image) in tqdm(enumerate(zip(test_annots, test_images))):
    _, ext = splitext(image)
    shutil.copy2(image, join("dataset", "test", f"{i}{ext}"))
    shutil.copy2(annot, join("dataset", "test", f"{i}.txt"))


