import React from 'react'
import markersImg from './assets/markers.png'
import "./App.css"
import Key from './components/Key'
import MarkerBorder from './components/MarkerBorder';

const useMousePosition = () => {
  const [
    mousePosition,
    setMousePosition
  ] = React.useState({ x: null, y: null });
  React.useEffect(() => {
    const updateMousePosition = ev => {
      setMousePosition({ x: ev.clientX, y: ev.clientY });
    };
    window.addEventListener('mousemove', updateMousePosition);
    return () => {
      window.removeEventListener('mousemove', updateMousePosition);
    };
  }, []);
  return mousePosition;
};

function App() {
  const [text, setText] = React.useState("")
  // const mousePosition = useMousePosition();
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
    ["A", "B", "C", "D", "E", "F", "G", "H"],
    ["I", "J", "K", "L", "M", "N", "O", "P"],
    ["Q", "R", "S", "T", "U", "V", "W", "X"],
    ["Y", "Z"],
  ]

  function inputKey(value) {
    setText(prevText => prevText + value)
  }

  return (
    <>
      <MarkerBorder markerSize="8vw">
        <div className="container">
          {rows.map((row, index) => {
            return (
              <div className="keyRow">
                {row.map((v, i) => <Key key={i} value={v} onTrigger={inputKey} />)}
              </div>
            )
          })}
          {/* <div className="keyRow">
            {secondRowValues.map((v, i) => <Key key={i} value={v} onTrigger={inputKey} />)}
          </div>
          <div className="keyRow">
            {thirdRowValues.map((v, i) => <Key key={i} value={v} onTrigger={inputKey} />)}
          </div> */}
          {/* <input type="text" className="input" value={text} onChange={() => null} /> */}

        </ div>
      </MarkerBorder>
      {/* <div className="cursor" style={{ "--cursorX": mousePosition.x + "px", "--cursorY": mousePosition.y + "px" }}></div> */}

    </>
  )
}

export default App
