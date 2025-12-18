import { useEffect, useState } from 'react'
import { fetchTags } from '../components/api'

export default function HomePage() {
  const [tags, setTags] = useState<string[]>([])

  useEffect(() => {
    fetchTags().then((data) => setTags(data.map((t: any) => t.name))).catch(() => setTags([]))
  }, [])

  return (
    <div>
      <div className="card">
        <h2>Bem-vindo</h2>
        <p>Interface React reimplementando as rotas do dashboard Dash.</p>
      </div>
      <div className="card">
        <h3>Tags monitoradas</h3>
        <ul>
          {tags.map((tag) => (
            <li key={tag}>{tag}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
