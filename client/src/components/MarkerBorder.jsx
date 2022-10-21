import React from 'react'




export default function MarkerBorder({ children, markerSize }) {
    const marker_names = ['tag36_11_00000.png', 'tag36_11_00001.png', 'tag36_11_00002.png', 'tag36_11_00003.png', 'tag36_11_00004.png', 'tag36_11_00005.png', 'tag36_11_00006.png', 'tag36_11_00007.png', 'tag36_11_00008.png', 'tag36_11_00009.png', 'tag36_11_00010.png', 'tag36_11_00011.png', 'tag36_11_00012.png', 'tag36_11_00013.png', 'tag36_11_00014.png', 'tag36_11_00015.png', 'tag36_11_00016.png', 'tag36_11_00017.png', 'tag36_11_00018.png', 'tag36_11_00019.png', 'tag36_11_00020.png', 'tag36_11_00021.png', 'tag36_11_00022.png', 'tag36_11_00023.png', 'tag36_11_00024.png', 'tag36_11_00025.png']
    const marker_positions = [
        [0., 0.],
        [0.11111111, 0.],
        [0.22222222, 0.],
        [0.33333334, 0.],
        [0.44444445, 0.],
        [0.5555556, 0.],
        [0.6666667, 0.],
        [0.7777778, 0.],
        [0.8888889, 0.],
        [1., 0.],
        [0., 1.],
        [0.11111111, 1.],
        [0.22222222, 1.],
        [0.33333334, 1.],
        [0.44444445, 1.],
        [0.5555556, 1.],
        [0.6666667, 1.],
        [0.7777778, 1.],
        [0.8888889, 1.],
        [1., 1.],
        [0., 0.25],
        [0., 0.5],
        [0., 0.75],
        [1., 0.25],
        [1., 0.5],
        [1., 0.75],
    ]
    const markers = []
    for (let i = 0; i < marker_names.length; i++) {
        const marker_name = marker_names[i]
        const marker_position = marker_positions[i]
        const marker_x = marker_position[0]
        const marker_y = marker_position[1]
        const left = `calc(${marker_x} * (100vw - ${markerSize})`
        const top = `calc(${marker_y} * (100vh - ${markerSize})`
        const marker = <img
            key={i}
            src={"markers_resized/" + marker_name}
            style={{ position: "absolute", left: left, top: top, width: markerSize, height: markerSize }}
        />
        markers.push(marker)
    }

    const innerContainerStyle = {
        position: "absolute",
        left: markerSize,
        top: markerSize,
        width: `calc(100vw - 2 * ${markerSize})`,
        height: `calc(100vh - 2 * ${markerSize})`,
        border: "1px solid black",
    }

    return (
        <>
            {markers}
            <div style={innerContainerStyle}>{children}</div>
        </>
    )
}
