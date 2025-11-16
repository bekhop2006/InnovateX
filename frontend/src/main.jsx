import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import './App.scss'
import './components/MultiUploadCard.scss'
import './components/DocumentsList.scss'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)