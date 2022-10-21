import cv2
import numpy as np

marker_size = 500
marker_names = [f"tag36_11_{str(i).zfill(5)}.png" for i in range(50)]
marker_imgs = [cv2.imread(f"markers/{marker_name}") for marker_name in marker_names]
marker_imgs = [
    cv2.resize(img, (marker_size, marker_size), interpolation=cv2.INTER_NEAREST)
    for img in marker_imgs
]

for name, img in zip(marker_names, marker_imgs):
    cv2.imwrite(f"markers_resized/{name}", img)
