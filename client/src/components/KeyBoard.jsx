import React from 'react'
import Key from './Key'
import "./KeyBoard.css"


export default function KeyBoard({ cursorPosition }) {
    const [text, setText] = React.useState("")
    const keys = []

    const letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    for (let i = 0; i < letters.length; i++) {
        keys.push(<Key key={i} value={letters[i]} onTrigger={appendValue} cursorPosition={cursorPosition} />)
    }
    keys.push(<Key key={keys.length} value={"space"} onTrigger={() => appendValue(" ")} cursorPosition={cursorPosition} />)
    keys.push(<Key key={keys.length} value={"reset"} onTrigger={resetText} cursorPosition={cursorPosition} />)

    function appendValue(value) {
        setText(prevText => prevText + value)
    }

    function resetText() {
        setText("")
    }

    return (
        <div className="gridContainer">
            {keys.map((key, i) => <div key={i} className="gridItem">{key}</div>)}
            <div className="gridItem-input">
                <input type="text" className="input" value={text} onChange={() => null} />
            </div>

        </ div>
    )
}
