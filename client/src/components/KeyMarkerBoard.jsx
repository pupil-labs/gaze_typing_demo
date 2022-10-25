import React from 'react'
import Key from './Key'
import "./KeyMarkerBoard.css"



export default function KeyMarkerBoard({ cursorPosition }) {
    const [text, setText] = React.useState("")
    const marker_names = ['tag36_11_00000.png', 'tag36_11_00001.png', 'tag36_11_00002.png', 'tag36_11_00003.png', 'tag36_11_00004.png', 'tag36_11_00005.png', 'tag36_11_00006.png', 'tag36_11_00007.png', 'tag36_11_00008.png', 'tag36_11_00009.png', 'tag36_11_00010.png', 'tag36_11_00011.png', 'tag36_11_00012.png', 'tag36_11_00013.png', 'tag36_11_00014.png', 'tag36_11_00015.png', 'tag36_11_00016.png', 'tag36_11_00017.png', 'tag36_11_00018.png', 'tag36_11_00019.png', 'tag36_11_00020.png', 'tag36_11_00021.png', 'tag36_11_00022.png', 'tag36_11_00023.png', 'tag36_11_00024.png', 'tag36_11_00025.png']
    const letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",]

    const boardItems = letters.map((l, i) => (
        <div className="gridItem">
            <Key key={i} value={l} onTrigger={appendValue} cursorPosition={cursorPosition} />
        </div>
    ))


    function insertMarker(markerName, index) {
        const marker = (
            <div
                className="gridItem"
                style={{ "--background-image": `url(markers_resized/${markerName})` }}
            >
            </div>
        )
        boardItems.splice(index, 0, marker);
    }

    insertMarker(marker_names[0], 0);
    insertMarker(marker_names[1], 6);
    insertMarker(marker_names[2], 8);
    insertMarker(marker_names[3], 12);
    insertMarker(marker_names[4], 14);
    insertMarker(marker_names[5], 20);
    insertMarker(marker_names[6], 24);
    insertMarker(marker_names[7], 28);
    insertMarker(marker_names[8], 34);

    function appendValue(value) {
        setText(prevText => prevText + value)
    }

    function resetText() {
        setText("")
    }

    return (
        <div className='gridContainer'>
            {boardItems.map((key, i) => (
                <div className="gridItem">
                    {key}
                </div>
            ))}
            <div className="gridItem">
                <Key key={"space"} value={"space"} onTrigger={() => appendValue(" ")} cursorPosition={cursorPosition} />
            </div>
            <div className="gridItem input">
                <input type="text" value={text} onChange={() => null} />
            </div>

            <div className="gridItem">
                <Key key={"reset"} value={"reset"} onTrigger={resetText} cursorPosition={cursorPosition} />
            </div>
        </ div>
    )
}
