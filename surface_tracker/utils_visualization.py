import functools

import cv2
import numpy as np
import numpy.typing as npt
from pupil_labs.realtime_api import GazeData
from pupil_labs.surface_tracker import SurfaceLocation

from marker_mapper_lib import MarkerMappedGaze, RadialDistorsionCamera


def draw_aoi(
    img,
    location: SurfaceLocation,
    camera: RadialDistorsionCamera,
    num_points_per_edge=20,
    fill: bool = False,
):
    edges, top_indices = _edge_points(num_points_per_edge)  # .copy()
    points = location._map_from_surface_to_image(edges)
    points = camera.distort_points_on_image_plane(points)

    num_points_edge = points.shape[0] // 4

    outline = np.asarray(points, dtype="int32").reshape((1, -1, 2))

    if fill:
        alpha = 0.5
        img_filled = img.copy()
        cv2.fillPoly(img_filled, outline, color=(255, 255, 0))
        cv2.addWeighted(img_filled, alpha, img, (1.0 - alpha), gamma=0, dst=img)

    cv2.polylines(
        img,
        outline,
        isClosed=False,
        color=(255, 255, 0),
        thickness=5,
    )
    # draw top edge in red
    cv2.polylines(
        img,
        np.asarray(points[top_indices], dtype="int32").reshape((1, -1, 2)),
        isClosed=False,
        color=(0, 0, 255),
        thickness=5,
    )

    return img


@functools.lru_cache()
def _edge_points(num_points_per_edge: int):
    zero_to_one = np.linspace(0, 1, num_points_per_edge)
    one_to_zero = np.linspace(1, 0, num_points_per_edge)

    points = np.zeros((num_points_per_edge * 4, 2))
    # bottom, left-to-right
    points[num_points_per_edge * 0 : num_points_per_edge * 1, 0] = zero_to_one
    points[num_points_per_edge * 0 : num_points_per_edge * 1, 1] = 0
    # right, bot-to-top
    points[num_points_per_edge * 1 : num_points_per_edge * 2, 0] = 1
    points[num_points_per_edge * 1 : num_points_per_edge * 2, 1] = zero_to_one
    # top, right-to-left
    points[num_points_per_edge * 2 : num_points_per_edge * 3, 0] = one_to_zero
    points[num_points_per_edge * 2 : num_points_per_edge * 3, 1] = 1
    # left, top-to-bot
    points[num_points_per_edge * 3 : num_points_per_edge * 4, 0] = 0
    points[num_points_per_edge * 3 : num_points_per_edge * 4, 1] = one_to_zero
    return points, np.arange(num_points_per_edge * 2, num_points_per_edge * 3)


def draw_gaze_point(img, gaze: GazeData):
    cv2.circle(
        img, (int(gaze.x), int(gaze.y)), radius=80, color=(0, 0, 255), thickness=15
    )


def draw_mapped_gaze_point(img: npt.NDArray[np.uint8], gaze: MarkerMappedGaze):
    img = img.copy()
    x = int(gaze.x * img.shape[1])
    y = int((1.0 - gaze.y) * img.shape[0])
    cv2.circle(img, (x, y), radius=40, color=(0, 0, 255), thickness=10)
    return img


def draw_marker_outlines(img, markers, camera: RadialDistorsionCamera):
    for marker in markers:
        cv2.polylines(
            img,
            np.array(
                camera.distort_points_on_image_plane(marker.vertices()),
                dtype="int32",
            ).reshape((-1, 4, 2)),
            isClosed=True,
            color=(0, 255, 0),
            thickness=1,
        )
