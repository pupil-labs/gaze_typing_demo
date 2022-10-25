import React from 'react'
import Key from './Key'
import "./KeyBoard.css"
import { Grid, TextField } from '@mui/material'


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
        <Grid container columns={8} spacing={0} style={{ height: "100%" }}>
            {keys.map((key, i) => <Grid item xs={1} key={i}>{key}</Grid>)}
            <Grid item xs={4} className="gridItem-input">
                <input type="text" value={text} onChange={() => null} />
            </Grid>

        </ Grid>
    )
}
