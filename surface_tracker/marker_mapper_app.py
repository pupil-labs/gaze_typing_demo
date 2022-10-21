import cv2

# from pupil_labs import surface_tracker
from pupil_labs.realtime_api.simple import discover_one_device

import marker_mapper_lib
import utils_cloud_api
from utils_visualization import (
    draw_aoi,
    draw_gaze_point,
    draw_mapped_gaze_point,
    draw_marker_outlines,
)


def main():
    # Look for devices. Returns as soon as it has found the first device.
    print("Looking for the next best device...")
    device = discover_one_device(max_search_duration_seconds=10)
    if device is None:
        print("No device found.")
        raise SystemExit(-1)

    try:
        # Pull scene camera serial to fetch accurate camera intrinsics
        serial_number_scene_cam = device.serial_number_scene_cam
        if not serial_number_scene_cam:
            print("Scene camera not connected")
            device.close()
            raise SystemExit(-2)

        # Setup area of interest (AoI) tracking
        camera = utils_cloud_api.camera_for_scene_cam_serial(serial_number_scene_cam)
        mapper = marker_mapper_lib.MarkerMapper(camera)
        mapper.add_core_surface_definitions_from_file(
            "~/pupil_capture_settings/surface_definitions_v01"
        )
        surface_uid_by_name = {s.name: s.uid for s in mapper.surfaces}

        # Load reference images
        areas_of_interest = {"reference aoi": cv2.imread("markers.png")}

        # Prepare and position main window
        main_title = f"Realtime-Marker-Tracking-Monitor on {device.address}"
        cv2.namedWindow(main_title)
        cv2.moveWindow(main_title, 100, 50)

        # Prepare and position reference image windows
        screen_position = 1250  # horizontal starting position
        for name, ref_img in areas_of_interest.items():
            cv2.namedWindow(name)
            cv2.moveWindow(name, screen_position, 50)
            screen_position += ref_img.shape[1] + 50

        # Main event loop:
        while True:
            # Wait for scene camera image and corresponding gaze position
            frame, gaze = device.receive_matched_scene_video_frame_and_gaze()

            # Process frame and gaze
            # 1. Marker detection
            # 2. AoI localisation
            # 3. Mapping gaze to AoI
            result = mapper.process_frame(frame.bgr_pixels, [gaze])

            if result is None:
                continue

            # Draw detected markers
            draw_marker_outlines(frame.bgr_pixels, result.markers, camera=camera)

            # Draw localised surfaces (fill if gaze is on AoI)
            for aoi_id, location in result.located_aois.items():
                if location is None:
                    continue
                any_gaze_on_aoi = any(g.is_on_aoi for g in result.mapped_gaze[aoi_id])
                draw_aoi(
                    frame.bgr_pixels, location, camera=camera, fill=any_gaze_on_aoi
                )

            # Draw gaze and display main window
            draw_gaze_point(frame.bgr_pixels, gaze)
            cv2.imshow(main_title, frame.bgr_pixels)

            # Draw AoI-mapped gaze and display reference image
            for name, img in areas_of_interest.items():
                for gaze in result.mapped_gaze[surface_uid_by_name[name]]:
                    if gaze.is_on_aoi:
                        img = draw_mapped_gaze_point(img, gaze)
                cv2.imshow(name, img)

            pressed_key = cv2.waitKey(1)
            if pressed_key == 27:  # ESC
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping...")
        device.close()  # explicitly stop auto-update


if __name__ == "__main__":
    main()
