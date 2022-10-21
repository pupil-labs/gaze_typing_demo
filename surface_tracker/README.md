# Realtime Marker Mapper Demo for Pupil Invisible

Demo script that shows how to perform marker mapping in realtime for Pupil Invisible.

## Setup

1. Download the files in this gist via the `Download ZIP` file in the top right and
    extract the files to your disk
1. Follow the general [marker mapper setup instructions](https://docs.pupil-labs.com/invisible/explainers/enrichments/#setup)
1. Use Pupil Capture to define your surface outline
1. Setup you reference images and load them accordingly as part of the
   `areas_of_interest` object definition in `marker_mapper_app.py`.
1. Make sure that you are running Pupil Invisible Companion v1.4.14 or newer
1. Use Python 3.7 or newer
1. Install the python requirements

```
pip install -r requirements.txt
```

## Usage

1. Connect your Pupil Invisible glasses including the scene camera
1. Run `python marker_mapper_app.py`
1. Position your glasses such that the markers can be detected correctly (green outline)


**Note:** The first time a new serial number is encountered, the script will attempt to
download camera intrinsics. This requires an internet connection. See below for details.

**Caveat:** This example does not support creating new surfaces or resizing any of the
predefined surfaces.

## How It Works

### Marker Mapper Lib

The marker detection and AoI tracking complexity has been abstracted away into the
`MarkerMapper` class in `marker_mapper_lib.py`.

Its main function is `MarkerMapper.process_frame(frame, gaze=())`. It returns a
`MarkerMapperResult` tuple of the following structure:

```py
class MarkerMapperResult(NamedTuple):
    markers: List[Marker]
    located_aois: Dict[SurfaceId, Optional[SurfaceLocation]]
    mapped_gaze: Dict[SurfaceId, List[MarkerMappedGaze]]
```

If no surfaces are defined, the `MarkerMapper` will simply return the detected markers.
If surfaces are defined it will localise them based on the detected markers.
If gaze is passed, it will map the gaze to each surface.

### Python Requirements

To run this example we need the following dependencies:
```sh
# receive gaze and scene video in realtime
pupil-labs-realtime-api

# marker detection and AoI tracking
pupil-apriltags
surface-tracker

# point (un)distortion and visualization
numpy
opencv-python

# downloading scene camera intrinsics
requests

# deserialize Pupil Capture surface definitions
msgpack
```

### Scene Camera Intrinsics

In order to correct the image distortion, the script needs to know the scene camera
intrinsics. These can be accessed via the Pupil Cloud API:
```
https://api.cloud.pupil-labs.com/hardware/<SCENE CAMERA SERIAL>/calibration.v1?json
```

To avoid requesting the same intrinsics repeatedly, the script will try to download the
values the first time it encounters a new scene camera serial number and cache it to
a `intrinsics.<SCENE CAMERA SERIAL>.json` file.
