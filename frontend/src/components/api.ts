import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
})

export async function fetchTags() {
  const { data } = await api.get('/tags')
  return data
}

export async function createTag(name: string, description?: string) {
  const { data } = await api.post('/tags', { name, description })
  return data
}

export async function fetchSeries(tags: string[]) {
  const { data } = await api.get('/series', {
    params: {
      tags: tags.join(','),
    },
  })
  return data.series
}

export async function runDetection(tags: string[]) {
  const { data } = await api.post('/detect', { tags, model_name: 'frontend-trigger' })
  return data
}

export async function fetchAnomalies(tag?: string) {
  const { data } = await api.get('/anomalies', { params: tag ? { tag } : {} })
  return data
}
