import React from 'react'

export default function Key({ value, onTrigger, cursorPosition }) {
    const containerRef = React.useRef(null)
    const [hover, setHover] = React.useState(false)
    const [activation, setActivation] = React.useState(0.0)
    const color = `hsl(184, 48%, ${45 + 35 * activation}%)`
    const style = { "--hover-color": color }

    function updateActivation() {
        if (!hover && activation > 0) {
            setActivation(0)
            return
        }

        if (hover && activation < 1) {
            setActivation(prevActivation => prevActivation + 0.1)
        }

        if (hover && activation >= 1) {
            onTrigger(value)
            setActivation(0)
        }
    }

    React.useEffect(() => {
        if (!containerRef.current) return

        const rect = containerRef.current.getBoundingClientRect()
        const hor_contained = cursorPosition.x >= rect.left && cursorPosition.x <= rect.right
        const ver_contained = cursorPosition.y >= rect.top && cursorPosition.y <= rect.bottom
        const contained = hor_contained && ver_contained

        if (contained) {
            setHover(true)
        } else {
            setHover(false)
            setActivation(0)
        }

    }, [cursorPosition])

    React.useEffect(() => {
        if (hover) {
            const interval = setInterval(updateActivation, 100);
            return () => clearInterval(interval);
        }
    }, [hover, activation]);

    function onMouseEnter() {
        setHover(true)
    }

    function onMouseLeave() {
        setHover(false)
        setActivation(0)
    }

    // console.log(containerRef.current?.getBoundingClientRect());

    return (
        <div className='keyContainer' ref={containerRef}>
            <div style={style} className='key' onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>{value}</div>
        </div>
    )
}
