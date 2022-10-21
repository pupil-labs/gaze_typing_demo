import cv2
import numpy as np

horizontal_slots = 10
vertical_slots = 5
display_resolution = (3840, 2160)
marker_size = 300

num_markers = 2 * (horizontal_slots + vertical_slots - 2)
marker_names = [f"tag36_11_{str(i).zfill(5)}.png" for i in range(num_markers)]
marker_imgs = [cv2.imread(f"markers/{marker_name}") for marker_name in marker_names]
marker_imgs = [
    cv2.resize(img, (marker_size, marker_size), interpolation=cv2.INTER_NEAREST)
    for img in marker_imgs
]


def get_marker_coordinates(
    horizontal_slots, vertical_slots, display_resolution, marker_size
):
    xlist = np.linspace(0, 1, horizontal_slots)
    ylist = np.linspace(0, 1, vertical_slots)
    marker_poitions = [(x, 0) for x in xlist]
    marker_poitions += [(x, 1) for x in xlist]
    marker_poitions += [(0, y) for y in ylist[1:-1]]
    marker_poitions += [(1, y) for y in ylist[1:-1]]
    marker_poitions = np.array(marker_poitions, dtype=np.float32)

    marker_poitions[:, 0] *= display_resolution[0] - marker_size
    marker_poitions[:, 1] *= display_resolution[1] - marker_size
    marker_poitions = marker_poitions.astype(np.int32)

    return marker_poitions


marker_coordinates = get_marker_coordinates(
    horizontal_slots, vertical_slots, display_resolution, marker_size
)

img = np.ones((display_resolution[1], display_resolution[0], 3), dtype=np.uint8) * 255
for marker_coordinate, marker_img in zip(marker_coordinates, marker_imgs):
    img[
        marker_coordinate[1] : marker_coordinate[1] + marker_size,
        marker_coordinate[0] : marker_coordinate[0] + marker_size,
        :,
    ] = marker_img

cv2.imwrite("markers.png", img)
