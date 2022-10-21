import React from 'react'

export default function Key({ value, onTrigger }) {
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

    return (
        <div className='keyContainer'>
            <div style={style} className='key' onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>{value}</div>
        </div>
    )
}
