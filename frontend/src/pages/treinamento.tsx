import { FormEvent, useState } from 'react'
import { runDetection } from '../components/api'

export default function TreinamentoPage() {
  const [tags, setTags] = useState('')
  const [status, setStatus] = useState<string>('')

  const handleDetect = async (event: FormEvent) => {
    event.preventDefault()
    const tagList = tags.split(',').map((t) => t.trim()).filter(Boolean)
    if (!tagList.length) return
    const response = await runDetection(tagList)
    setStatus(`Execução ${response.id} - ${response.status}`)
  }

  return (
    <div>
      <h2>Treinamento</h2>
      <div className="card">
        <p>Espelha a tela de treinamento do dashboard Dash com filtros e disparo manual.</p>
        <form className="filters" onSubmit={handleDetect}>
          <input
            className="input"
            placeholder="Tags separadas por vírgula"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
          />
          <button type="submit">Executar detecção</button>
        </form>
        {status && <p>{status}</p>}
      </div>
    </div>
  )
}
