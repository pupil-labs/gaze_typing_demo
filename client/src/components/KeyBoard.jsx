import React from 'react'
import Key from './Key'



export default function KeyBoard({ cursorPosition }) {
    const [text, setText] = React.useState("")

    // const firstRowValues = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"]
    // const secondRowValues = ["A", "S", "D", "F", "G", "H", "J", "K", "L"]
    // const thirdRowValues = ["Z", "X", "C", "V", "B", "N", "M"]
    // const rows = [
    //   ["A", "B", "C", "D", "E", "F"],
    //   ["G", "H", "I", "J", "K", "L"],
    //   ["M", "N", "O", "P", "Q", "R"],
    //   ["S", "T", "U", "V", "W", "X"],
    //   ["Y", "Z"],
    // ]
    const rows = [
        // ["A"],
        ["A", "B", "C", "D", "E", "F", "G", "H"],
        ["I", "J", "K", "L", "M", "N", "O", "P"],
        ["Q", "R", "S", "T", "U", "V", "W", "X"],
        ["Y", "Z", " "],
    ]

    function inputKey(value) {
        setText(prevText => prevText + value)
    }

    const keyBoard = rows.map((row, i) => {
        return (
            <div className="keyRow" key={i}>
                {row.map((v, i) => <Key key={i} value={v} onTrigger={inputKey} cursorPosition={cursorPosition} />)}
            </div>
        )
    })

    return (
        <div className="container">
            {keyBoard}
            <input type="text" className="input" value={text} onChange={() => null} />

        </ div>
    )
}
