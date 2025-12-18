import Plot from 'react-plotly.js'

interface PlotCardProps {
  title: string
  x: string[]
  y: number[]
}

export default function PlotCard({ title, x, y }: PlotCardProps) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <Plot
        data={[{ x, y, type: 'scatter', mode: 'lines+markers', marker: { color: '#2563eb' } }]}
        layout={{ autosize: true, margin: { t: 20, l: 40, r: 20, b: 40 } }}
        style={{ width: '100%', height: '320px' }}
        useResizeHandler
      />
    </div>
  )
}
