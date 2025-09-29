import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Plus, Settings, Database } from 'lucide-react'

const Layout = ({ children }) => {
  const location = useLocation()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Database className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">ATS Mock API</h1>
            </div>
            <nav className="flex space-x-4">
              <Link
                to="/endpoints"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  location.pathname.startsWith('/endpoints')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Endpoints
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}

export default Layout