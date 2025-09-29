import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import EndpointsList from './pages/EndpointsList'
import EndpointDetail from './pages/EndpointDetail'
import CreateEndpoint from './pages/CreateEndpoint'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/endpoints" replace />} />
        <Route path="/endpoints" element={<EndpointsList />} />
        <Route path="/endpoints/new" element={<CreateEndpoint />} />
        <Route path="/endpoints/:id" element={<EndpointDetail />} />
      </Routes>
    </Layout>
  )
}

export default App