import cv2
import numpy as np
import argparse
import os
import math
import json
import colorsys

def show_knots(idx, knots_info, dir, save=True):
    # Annotate all the images in /images using exported pixels from images/knots_info.json
    image_filename = "{0:06d}_rgb.png".format(idx)
    img = cv2.imread('{}/{}'.format(dir, image_filename))
    pixels = knots_info[str(idx)]
    pixels = [i[0] for i in pixels]
    vis = img.copy()
    print("Annotating %06d"%idx)
    for i, (u, v) in enumerate(pixels):
        (r, g, b) = colorsys.hsv_to_rgb(float(i)/len(pixels), 1.0, 1.0)
        R, G, B = int(255 * r), int(255 * g), int(255 * b)
        cv2.circle(vis,(int(u), int(v)), 1, (R, G, B), -1)
    if save:
    	annotated_filename = "{0:06d}_annotated.png".format(idx)
    	cv2.imwrite('./annotated/{}'.format(annotated_filename), vis)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num', type=int, default=len(os.listdir('./images')) - 1)
    parser.add_argument('-d', '--dir', type=str, default='images')
    args = parser.parse_args()
    if not os.path.exists("./annotated"):
        os.makedirs('./annotated')
    else:
        os.system("rm -rf ./annotated")
        os.makedirs("./annotated")
    print("parsed")
    with open("{}/knots_info.json".format(args.dir), "r") as stream:
    	knots_info = json.load(stream)
    print("loaded knots info")
    for i in range(args.num):
        show_knots(i, knots_info, args.dir)
