import { useEffect, useState } from 'react'
import PlotCard from '../components/PlotCard'
import { fetchSeries } from '../components/api'

export default function DashboardPage() {
  const [series, setSeries] = useState<Record<string, { timestamp: string; value: number }[]>>({})

  useEffect(() => {
    fetchSeries(['tag-1', 'tag-2'])
      .then(setSeries)
      .catch(() => setSeries({}))
  }, [])

  return (
    <div>
      <h2>Dashboard</h2>
      {Object.entries(series).map(([tag, points]) => (
        <PlotCard key={tag} title={tag} x={points.map((p) => p.timestamp)} y={points.map((p) => p.value)} />
      ))}
    </div>
  )
}
