import os
import sys
import uuid
from typing import Dict, Iterable, List, Mapping, NamedTuple, Optional, Tuple

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

import cv2
import msgpack
import numpy as np
import numpy.typing as npt
import pupil_apriltags
from pupil_labs.realtime_api import GazeData
from pupil_labs.surface_tracker import (
    CoordinateSpace,
    CornerId,
    Marker,
    MarkerId,
    Surface,
    SurfaceId,
    SurfaceLocation,
    SurfaceOrientation,
    SurfaceTracker,
    marker,
)


class MarkerMapper:
    def __init__(
        self,
        camera: Optional["RadialDistorsionCamera"],
        surfaces: Iterable[Surface] = (),
    ) -> None:
        self._camera: Optional[RadialDistorsionCamera]
        self._detector: Optional[ApriltagDetector]
        self._tracker = SurfaceTracker()

        self.camera = camera
        self._surfaces: List[Surface] = list(surfaces)
        self._recent_result: Optional[MarkerMapperResult] = None

    def process_frame(
        self, frame: npt.NDArray[np.uint8], gaze: Iterable[GazeData] = ()
    ) -> Optional["MarkerMapperResult"]:
        """
        1. Detect markers
        2. Locate defined surfaces
        3. (Optional) Map gaze to each located surface
        """
        if not all((self._camera, self._detector)):
            return

        is_gray = (frame.ndim == 2) or (frame.shape[2] == 1)
        if is_gray:
            markers = self._detector.detect_from_gray(frame)
        else:
            markers = self._detector.detect_from_image(frame)

        surface_locations = {
            surface.uid: self._tracker.locate_surface(
                surface=surface,
                markers=markers,
            )
            for surface in self._surfaces
        }

        gaze_undistorted = self._camera.undistort_points_on_image_plane(
            [[g.x, g.y] for g in gaze]
        )

        gaze_mapped_norm: npt.NDArray[np.float32]
        mapped_gaze: Dict[SurfaceId, List[MarkerMappedGaze]] = {}
        for surface_uid, location in surface_locations.items():
            if location is None:
                mapped_gaze[surface_uid] = []
                continue

            gaze_mapped_norm = location._map_from_image_to_surface(gaze_undistorted)
            mapped_gaze[location.surface_uid] = [
                MarkerMappedGaze.from_norm_pos(surface_uid, norm, base)
                for base, norm in zip(gaze, gaze_mapped_norm.tolist())
            ]

        return MarkerMapperResult(markers, surface_locations, mapped_gaze)

    def add_core_surface_definitions_from_file(self, path: str) -> None:
        path = os.path.expanduser(path)
        with open(path, "rb") as fh:
            surface_definitions = msgpack.unpack(fh)
            surfaces = [
                _CoreSurface.from_dict(surf) for surf in surface_definitions["surfaces"]
            ]
            self._surfaces.extend(surfaces)

    @property
    def camera(self) -> Optional["RadialDistorsionCamera"]:
        return self._camera

    @camera.setter
    def camera(self, camera: Optional["RadialDistorsionCamera"]) -> None:
        self._camera = camera
        if camera is None:
            self._detector = None
        else:
            self._detector = ApriltagDetector(camera)

    @property
    def surfaces(self) -> Tuple[Surface]:
        return tuple(self._surfaces)


class MarkerMappedGaze(NamedTuple):
    aoi_id: SurfaceId
    x: float
    y: float
    is_on_aoi: bool
    base_datum: GazeData

    @classmethod
    def from_norm_pos(
        cls, aoi_id: SurfaceId, norm_pos: Tuple[float, float], base_datum: GazeData
    ):
        on_surface = (0.0 <= norm_pos[0] <= 1.0) and (0.0 <= norm_pos[1] <= 1.0)
        return cls(aoi_id, *norm_pos, on_surface, base_datum)


class MarkerMapperResult(NamedTuple):
    markers: List[Marker]
    located_aois: Dict[SurfaceId, Optional[SurfaceLocation]]
    mapped_gaze: Dict[SurfaceId, List[MarkerMappedGaze]]


# Source: pupil/pupil_src/shared_modules/camera_model.py
# TODO: Use https://github.com/pupil-labs/camera instead
class RadialDistorsionCamera:
    """Camera model assuming a lense with radial distortion (this is the defaut model in opencv).
    Provides functionality to make use of a pinhole camera calibration that is also compensating for lense distortion
    """

    def __init__(self, K: npt.ArrayLike, D: npt.ArrayLike):
        self.K = np.array(K)
        self.D = np.array(D)

    # CameraModel Interface

    def undistort_points_on_image_plane(self, points):
        points = self.__unprojectPoints(points, use_distortion=True)
        points = self.__projectPoints(points, use_distortion=False)
        return points

    def distort_points_on_image_plane(self, points):
        points = self.__unprojectPoints(points, use_distortion=False)
        points = self.__projectPoints(points, use_distortion=True)
        return points

    def distort_and_project(self, *args, **kwargs):
        return self.distort_points_on_image_plane(*args, **kwargs)

    def undistort_image(self, img):
        return cv2.undistort(img, self.K, self.D)

    # Private

    def __projectPoints(self, object_points, rvec=None, tvec=None, use_distortion=True):
        """
        Projects a set of points onto the camera plane as defined by the camera model.
        :param object_points: Set of 3D world points
        :param rvec: Set of vectors describing the rotation of the camera when recording the corresponding object point
        :param tvec: Set of vectors describing the translation of the camera when recording the corresponding object point
        :return: Projected 2D points
        """
        input_dim = object_points.ndim

        object_points = object_points.reshape((1, -1, 3))

        if rvec is None:
            rvec = np.zeros(3).reshape(1, 1, 3)
        else:
            rvec = np.array(rvec).reshape(1, 1, 3)

        if tvec is None:
            tvec = np.zeros(3).reshape(1, 1, 3)
        else:
            tvec = np.array(tvec).reshape(1, 1, 3)

        if use_distortion:
            _D = self.D
        else:
            _D = np.asarray([[0.0, 0.0, 0.0, 0.0, 0.0]])

        image_points, jacobian = cv2.projectPoints(
            object_points, rvec, tvec, self.K, _D
        )

        if input_dim == 2:
            image_points.shape = (-1, 2)
        elif input_dim == 3:
            image_points.shape = (-1, 1, 2)
        return image_points

    def __unprojectPoints(self, pts_2d, use_distortion=True, normalize=False):
        """
        Undistorts points according to the camera model.
        :param pts_2d, shape: Nx2
        :return: Array of unprojected 3d points, shape: Nx3
        """
        pts_2d = np.array(pts_2d, dtype=np.float32)

        # Delete any posibly wrong 3rd dimension
        if pts_2d.ndim == 1 or pts_2d.ndim == 3:
            pts_2d = pts_2d.reshape((-1, 2))

        # Add third dimension the way cv2 wants it
        if pts_2d.ndim == 2:
            pts_2d = pts_2d.reshape((-1, 1, 2))

        if use_distortion:
            _D = self.D
        else:
            _D = np.asarray([[0.0, 0.0, 0.0, 0.0, 0.0]])

        pts_2d_undist = cv2.undistortPoints(pts_2d, self.K, _D)

        pts_3d = cv2.convertPointsToHomogeneous(pts_2d_undist)
        pts_3d.shape = -1, 3

        if normalize:
            pts_3d /= np.linalg.norm(pts_3d, axis=1)[:, np.newaxis]

        return pts_3d


def create_apriltag_marker_uid(tag_family: str, tag_id: int) -> MarkerId:
    # Construct the UID by concatinating the tag family and the tag id
    return MarkerId(f"{tag_family}:{tag_id}")


class ApriltagDetector:
    def __init__(self, camera_model: RadialDistorsionCamera):
        families = "tag36h11"
        self._camera_model = camera_model
        self._detector = pupil_apriltags.Detector(
            families=families, nthreads=2, quad_decimate=2.0, decode_sharpening=1.0
        )

    def detect_from_image(self, image: npt.NDArray[np.uint8]) -> List[Marker]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return self.detect_from_gray(gray)

    def detect_from_gray(self, gray: npt.NDArray[np.uint8]) -> List[Marker]:
        # Detect apriltag markers from the gray image
        markers = self._detector.detect(gray)

        # Ensure detected markers are unique
        # TODO: Between deplicate markers, pick the one with higher confidence
        uid_fn = self.__apiltag_marker_uid
        markers = {uid_fn(m): m for m in markers}.values()

        # Convert apriltag markers into surface tracker markers
        marker_fn = self.__apriltag_marker_to_surface_marker
        markers = [marker_fn(m) for m in markers]

        return markers

    @staticmethod
    def __apiltag_marker_uid(
        apriltag_marker: pupil_apriltags.Detection,
    ) -> MarkerId:
        family = apriltag_marker.tag_family.decode("utf-8")
        tag_id = int(apriltag_marker.tag_id)
        return create_apriltag_marker_uid(family, tag_id)

    def __apriltag_marker_to_surface_marker(
        self, apriltag_marker: pupil_apriltags.Detection
    ) -> Marker:

        # Construct the surface tracker marker UID
        uid = ApriltagDetector.__apiltag_marker_uid(apriltag_marker)

        # Extract vertices in the correct format form apriltag marker
        vertices = [[point] for point in apriltag_marker.corners]
        vertices = self._camera_model.undistort_points_on_image_plane(vertices)

        # TODO: Verify this is correct...
        starting_with = CornerId.TOP_LEFT
        clockwise = True

        return Marker.from_vertices(
            uid=uid,
            undistorted_image_space_vertices=vertices,
            starting_with=starting_with,
            clockwise=clockwise,
        )


class _CoreSurface(Surface):

    version = 1

    @property
    def uid(self) -> SurfaceId:
        return self.__uid

    @property
    def name(self) -> str:
        return self.__name

    @property
    def _registered_markers_by_uid_undistorted(self) -> Mapping[MarkerId, Marker]:
        return self.__registered_markers_by_uid_undistorted

    @_registered_markers_by_uid_undistorted.setter
    def _registered_markers_by_uid_undistorted(self, value: Mapping[MarkerId, Marker]):
        self.__registered_markers_by_uid_undistorted = value

    @property
    def orientation(self) -> SurfaceOrientation:
        return self.__orientation

    @orientation.setter
    def orientation(self, value: SurfaceOrientation):
        self.__orientation = value

    def as_dict(self) -> dict:
        registered_markers_undistorted = self._registered_markers_by_uid_undistorted
        registered_markers_undistorted = {
            k: v.as_dict() for k, v in registered_markers_undistorted.items()
        }
        return {
            "version": self.version,
            "uid": str(self.uid),
            "name": self.name,
            "reg_markers": registered_markers_undistorted,
            "orientation": self.orientation.as_dict(),
        }

    @staticmethod
    def from_dict(value: dict) -> "Surface":
        try:
            actual_version = value["version"]
            expected_version = _CoreSurface.version
            assert (
                expected_version == actual_version
            ), f"Surface version missmatch; expected {expected_version}, but got {actual_version}"

            for m in value["reg_markers"]:
                m["uid"] = m["uid"].replace("apriltag_v3:", "")

            registered_markers_undistorted = {
                m["uid"]: _CoreMarker.from_dict(m) for m in value["reg_markers"]
            }

            orientation_dict = value.get("orientation", None)
            if orientation_dict:
                orientation = SurfaceOrientation.from_dict(orientation_dict)
            else:
                # use default if surface was saved as dict before this change
                orientation = SurfaceOrientation()

            return _CoreSurface(
                uid=SurfaceId(value.get("uid", str(uuid.uuid4()))),
                name=value["name"],
                registered_markers_undistorted=registered_markers_undistorted,
                orientation=orientation,
            )
        except Exception as err:
            raise ValueError(err)

    def __init__(
        self,
        uid: SurfaceId,
        name: str,
        registered_markers_undistorted: Mapping[MarkerId, Marker],
        orientation: SurfaceOrientation,
    ):
        self.__uid = uid
        self.__name = name
        self.__registered_markers_by_uid_undistorted = registered_markers_undistorted
        self.__orientation = orientation
        assert all(
            m.coordinate_space == CoordinateSpace.SURFACE_UNDISTORTED
            for m in registered_markers_undistorted.values()
        )


class _CoreMarker(Marker):
    @property
    def uid(self) -> MarkerId:
        return self.__uid

    @property
    def coordinate_space(self) -> CoordinateSpace:
        return self.__coordinate_space

    def _vertices_in_order(self, order: List[CornerId]) -> List[Tuple[float, float]]:
        mapping = self.__vertices_by_corner_id
        return [mapping[c] for c in order]

    @staticmethod
    def from_dict(value: dict) -> "Marker":
        try:
            return _CoreMarker(
                uid=value["uid"],
                coordinate_space=CoordinateSpace.SURFACE_UNDISTORTED,
                vertices_by_corner_id=dict(zip(CornerId, value["verts_uv"])),
            )
        except Exception as err:
            raise ValueError(err)

    def as_dict(self) -> dict:
        return {
            "uid": self.__uid,
            "space": self.__coordinate_space,
            "vertices": self.__vertices_by_corner_id,
        }

    def __init__(
        self,
        uid: MarkerId,
        coordinate_space: CoordinateSpace,
        vertices_by_corner_id: Mapping[CornerId, Tuple[float, float]],
    ):
        self.__uid = uid
        self.__coordinate_space = coordinate_space
        self.__vertices_by_corner_id = vertices_by_corner_id


marker._Marker = _CoreMarker
