import asyncio
from pupil_labs.realtime_api.simple import discover_one_device

import marker_mapper_lib
import utils_cloud_api


class MarkerMapper:
    def __init__(self):
        self.device = discover_one_device(max_search_duration_seconds=10)
        if self.device is None:
            print("No device found.")
            raise SystemExit(-1)

        serial_number_scene_cam = self.device.serial_number_scene_cam
        if not serial_number_scene_cam:
            print("Scene camera not connected")
            self.device.close()
            raise SystemExit(-2)

        # Setup area of interest (AoI) tracking
        camera = utils_cloud_api.camera_for_scene_cam_serial(serial_number_scene_cam)
        self.mapper = marker_mapper_lib.MarkerMapper(camera)
        self.mapper.add_core_surface_definitions_from_file(
            "~/pupil_capture_settings/surface_definitions_v01"
        )
    
    def __call__(self):
        frame, gaze = self.device.receive_matched_scene_video_frame_and_gaze()

        # Process frame and gaze
        # 1. Marker detection
        # 2. AoI localisation
        # 3. Mapping gaze to AoI
        result = self.mapper.process_frame(frame.bgr_pixels, [gaze])

        return result