import argparse
import time
import cv2

from detect_table_class import NutritionTableDetector
from crop import crop
from text_detection import text_detection, load_text_model
from process import *
from regex import *
from nutrient_list import *
from spacial_map import *

def load_model():
    global obj
    obj = NutritionTableDetector()
    print("Weights Loaded!")

def detect(img_path, debug):
    start_time = time.time()
    image = cv2.imread(img_path)
    boxes, scores, classes, num = obj.get_classification(image)
    width = image.shape[1]
    height = image.shape[0]

    if debug:
        time_taken = time.time() - start_time
        print("Time taken to detect the table: %.5fs" % time_taken)

    ymin = boxes[0][0][0] * height
    xmin = boxes[0][0][1] * width
    ymax = boxes[0][0][2] * height
    xmax = boxes[0][0][3] * width
    coords = (xmin, ymin, xmax, ymax)

    cropped_image = crop(image, coords, "./data/result/output.jpg", 0, True)
    cropped_image = preprocess_for_ocr(cropped_image, 3)

    if debug:
        cv2.imwrite('./data/result/output-opt.png', cropped_image)

    text_blob_list = text_detection(cropped_image)

    if debug:
        time_taken = time.time() - start_time
        print("Time Taken to detect bounding boxes for text: %.5fs" % time_taken)

    text_location_list = []
    nutrient_dict = {}

    counter = 0
    for blob_cord in text_blob_list:
        if debug:
            counter += 1
            word_image = crop(cropped_image, blob_cord, "./data/result/{}.jpg".format(counter), 0.005, True)
        else:
            word_image = crop(cropped_image, blob_cord, "./", 0.005, False)
        word_image = preprocess_for_ocr(word_image)
        if word_image.shape[1] > 0 and word_image.shape[0] > 0:
            text = ocr(word_image, 1, 7)

            if debug:
                print(text)

            if text:
                center_x = (blob_cord[0] + blob_cord[2]) / 2
                center_y = (blob_cord[1] + blob_cord[3]) / 2
                box_center = (center_x, center_y)

                new_location = {
                    'bbox': blob_cord,
                    'text': text,
                    'box_center': box_center,
                    'string_type': string_type(text)
                }
                text_location_list.append(new_location)

    for text_dict in text_location_list:
        if text_dict['string_type'] == 2:
            for text_dict_test in text_location_list:
                if position_definer(text_dict['box_center'][1], text_dict_test['bbox'][1], text_dict_test['bbox'][3]) and text_dict_test['string_type'] == 1:
                    text_dict['text'] = text_dict['text'].__add__(' ' + text_dict_test['text'])
                    text_dict['string_type'] = 0

    fuzdict = make_fuzdict('data/nutrients.txt')

    for text_dict in text_location_list:
        if text_dict['string_type'] == 0:
            text = clean_string(text_dict['text'])

            if fuz_check_for_label(text, fuzdict, debug):
                label_name, label_value = get_fuz_label_from_string(text, fuzdict, debug)
                nutrient_dict[label_name] = separate_unit(label_value)

    if debug:
        time_taken = time.time() - start_time
        print("Total Time Taken: %.5fs" % time_taken)

    return nutrient_dict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to the input image")
    ap.add_argument("-d", "--debug", action='store_true', help="print some debug info")
    args = ap.parse_args()

    load_model()
    load_text_model()

    print(detect(args.image, args.debug))

if __name__ == '__main__':
    main()
