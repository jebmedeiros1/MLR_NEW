import { FormEvent, useEffect, useState } from 'react'
import { createTag, fetchAnomalies, fetchTags } from '../components/api'

interface AnomalyRow {
  id: number
  tag_id: number
  run_id: number
  detected_at: string
  severity: number
  message?: string
}

export default function DadosPage() {
  const [tags, setTags] = useState<any[]>([])
  const [anomalies, setAnomalies] = useState<AnomalyRow[]>([])
  const [newTag, setNewTag] = useState('')

  useEffect(() => {
    fetchTags().then(setTags)
    fetchAnomalies().then(setAnomalies)
  }, [])

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!newTag) return
    await createTag(newTag)
    setNewTag('')
    setTags(await fetchTags())
  }

  return (
    <div>
      <h2>Dados</h2>
      <div className="card">
        <h3>Cadastrar tag</h3>
        <form onSubmit={handleSubmit} className="filters">
          <input className="input" value={newTag} onChange={(e) => setNewTag(e.target.value)} placeholder="Nome da tag" />
          <button type="submit">Salvar</button>
        </form>
      </div>
      <div className="card">
        <h3>Tags</h3>
        <ul>
          {tags.map((t) => (
            <li key={t.id}>{t.name}</li>
          ))}
        </ul>
      </div>
      <div className="card">
        <h3>Anomalias</h3>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tag</th>
              <th>Severidade</th>
              <th>Mensagem</th>
              <th>Detectado em</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.map((row) => (
              <tr key={row.id}>
                <td>{row.id}</td>
                <td>{row.tag_id}</td>
                <td>{row.severity.toFixed(2)}</td>
                <td>{row.message}</td>
                <td>{new Date(row.detected_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
