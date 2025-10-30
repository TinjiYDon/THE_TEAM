import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Bills from './pages/Bills'
import Analysis from './pages/Analysis'
import AIAssistant from './pages/AIAssistant'
import Recommendations from './pages/Recommendations'
import Community from './pages/Community'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="bills" element={<Bills />} />
          <Route path="analysis" element={<Analysis />} />
          <Route path="ai-assistant" element={<AIAssistant />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="community" element={<Community />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

