import os
import glob
import argparse
import pandas as pd
import xml.etree.ElementTree as ET

def process(path, prefix):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (prefix + root.find('filename').text,
					     int(root.find('size')[0].text),
					     int(root.find('size')[1].text),
					     member[0].text,
					     int(member[4][0].text),
					     int(member[4][1].text),
					     int(member[4][2].text),
					     int(member[4][3].text)
					     )
            xml_list.append(value)
    return xml_list

def xml_to_csv(path, subfolders, folder):
    xml_list = []

    if subfolders is None or len(subfolders) == 0:
        xml_list += process(path + '/' + folder, '')
        column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
        xml_df = pd.DataFrame(xml_list, columns=column_name)
        return xml_df

    for subfolder in subfolders:
        xml_list += process(path + '/' + subfolder + '/' + folder, subfolder + '/' + folder + '/')
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

parser = argparse.ArgumentParser(description='Convert .xml files into .csv.')
parser.add_argument('-f','--folders', required=True, type=str, help='The folders that will be used in the convertion.')
parser.add_argument('-im','--images', required=True, type=str, help='The path to the images folder.')
args = parser.parse_args()

subfolders = args.folders.split(',')

for folder in ['train','test']:
	image_path = os.path.join(args.images)
	xml_df = xml_to_csv(image_path, subfolders, folder)
	xml_df.to_csv((args.images + '/' + folder + '_labels.csv'), index=None)
	print('Successfully converted xml to csv.')

