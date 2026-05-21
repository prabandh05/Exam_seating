import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider
        theme={{
          algorithm: theme.darkAlgorithm,
          token: {
            colorPrimary: '#6366f1',
            colorBgContainer: '#1a1a2e',
            colorBgElevated: '#16213e',
            colorBgLayout: '#0f0f23',
            borderRadius: 12,
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
          },
          components: {
            Card: { colorBgContainer: '#1a1a2e' },
            Table: { colorBgContainer: '#1a1a2e' },
            Modal: { colorBgElevated: '#16213e' },
            Menu: { colorBgContainer: '#0a0a1a' },
          },
        }}
      >
        <AuthProvider>
          <App />
        </AuthProvider>
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
)
