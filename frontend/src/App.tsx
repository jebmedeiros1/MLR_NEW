import { Routes, Route, Link } from 'react-router-dom'
import HomePage from './pages/home'
import DashboardPage from './pages/dashboard'
import DadosPage from './pages/dados'
import TreinamentoPage from './pages/treinamento'
import ModalModelos from './pages/modal_modelos'
import ModalAnomalia from './pages/modal_anomalia'

export default function App() {
  return (
    <div>
      <header>
        <h1>Monitoramento de Anomalias</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/dados">Dados</Link>
          <Link to="/treinamento">Treinamento</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/dados" element={<DadosPage />} />
          <Route path="/treinamento" element={<TreinamentoPage />} />
          <Route path="/modal/modelos" element={<ModalModelos />} />
          <Route path="/modal/anomalia" element={<ModalAnomalia />} />
        </Routes>
      </main>
    </div>
  )
}
