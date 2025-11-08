import React, { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Bills = lazy(() => import('./pages/Bills'))
const Analysis = lazy(() => import('./pages/Analysis'))
const AIAssistant = lazy(() => import('./pages/AIAssistant'))
const Assistant = lazy(() => import('./pages/Assistant'))
const Recommendations = lazy(() => import('./pages/Recommendations'))
const Community = lazy(() => import('./pages/Community'))
const Groups = lazy(() => import('./pages/Groups'))
const Health = lazy(() => import('./pages/Health'))
const EvalPage = lazy(() => import('./pages/Eval'))

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <Suspense fallback={<div style={{ padding: 24 }}>加载中...</div>}>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/assistant" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="bills" element={<Bills />} />
            <Route path="analysis" element={<Analysis />} />
            <Route path="ai-assistant" element={<AIAssistant />} />
            <Route path="assistant" element={<Assistant />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="community" element={<Community />} />
            <Route path="groups" element={<Groups />} />
            <Route path="groups/:id" element={<Groups />} />
            <Route path="health" element={<Health />} />
            <Route path="eval" element={<EvalPage />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}

export default App

