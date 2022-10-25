import React from 'react'
import MarkerBorder from './components/MarkerBorder';
import KeyBoard from './components/KeyBoard';
import "./App.css";
import useMousePosition from './hooks/useMousePosition';
import useWindowDimensions from './hooks/useWindowDimensions';
import useWebSocket, { ReadyState } from 'react-use-websocket';


function App() {
  const { height: windowHeight, width: windowWidth } = useWindowDimensions();
  // const cursorPosition = useMousePosition();
  const { lastJsonMessage } = useWebSocket('ws://localhost:8001');
  const cursorPosition = React.useMemo(() => {

    let point = {
      x: 0,
      y: 0,
    }
    if (lastJsonMessage) {
      point = {
        x: lastJsonMessage.x * windowWidth,
        y: windowHeight - lastJsonMessage.y * windowHeight,
      }
    }
    console.log(point);
    return point;
  }, [lastJsonMessage]);


  return (
    <>
      <MarkerBorder markerSize="8vw">
        <KeyBoard cursorPosition={cursorPosition} />
      </MarkerBorder>
      <div className="cursor" style={{ "--cursorX": cursorPosition.x + "px", "--cursorY": cursorPosition.y + "px" }}></div>
    </>
  )
}

export default App
