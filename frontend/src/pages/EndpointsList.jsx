import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Edit, Trash2, Play, Pause, FileText } from 'lucide-react'
import { endpointsApi } from '../utils/api'
import OpenAPIImport from '../components/OpenAPIImport'

const EndpointsList = () => {
  const [showImport, setShowImport] = useState(false)
  const queryClient = useQueryClient()

  const { data: endpoints, isLoading, error } = useQuery({
    queryKey: ['endpoints'],
    queryFn: () => endpointsApi.getAll().then(res => res.data)
  })

  const deleteMutation = useMutation({
    mutationFn: endpointsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries(['endpoints'])
    }
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }) => endpointsApi.update(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries(['endpoints'])
    }
  })

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this endpoint?')) {
      deleteMutation.mutate(id)
    }
  }

  const handleToggle = (endpoint) => {
    toggleMutation.mutate({ id: endpoint.id, is_active: !endpoint.is_active })
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <h3 className="text-red-800 font-medium">Error loading endpoints</h3>
        <p className="text-red-600">{error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">API Endpoints</h2>
          <p className="text-gray-600 mt-1">Manage your dynamic API endpoints</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowImport(true)}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <FileText className="w-4 h-4 mr-2" />
            Import OpenAPI
          </button>
          <Link
            to="/endpoints/new"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Endpoint
          </Link>
        </div>
      </div>

      {/* Endpoints List */}
      {endpoints && endpoints.length > 0 ? (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {endpoints.map((endpoint) => (
              <li key={endpoint.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
                        endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800' :
                        endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
                        endpoint.method === 'DELETE' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {endpoint.method}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <Link
                        to={`/endpoints/${endpoint.id}`}
                        className="block focus:outline-none"
                      >
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {endpoint.name}
                          </p>
                          {!endpoint.is_active && (
                            <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                              Inactive
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 truncate">{endpoint.path}</p>
                        {endpoint.description && (
                          <p className="text-xs text-gray-400 truncate">{endpoint.description}</p>
                        )}
                      </Link>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggle(endpoint)}
                      className={`p-2 rounded-full ${
                        endpoint.is_active
                          ? 'text-green-600 hover:bg-green-100'
                          : 'text-red-600 hover:bg-red-100'
                      }`}
                      title={endpoint.is_active ? 'Deactivate' : 'Activate'}
                    >
                      {endpoint.is_active ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                    </button>
                    <Link
                      to={`/endpoints/${endpoint.id}`}
                      className="p-2 text-blue-600 hover:bg-blue-100 rounded-full"
                      title="Edit"
                    >
                      <Edit className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => handleDelete(endpoint.id)}
                      className="p-2 text-red-600 hover:bg-red-100 rounded-full"
                      title="Delete"
                      disabled={deleteMutation.isLoading}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Plus className="w-8 h-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No endpoints yet</h3>
          <p className="text-gray-500 mb-6">Get started by creating your first API endpoint.</p>
          <Link
            to="/endpoints/new"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Endpoint
          </Link>
        </div>
      )}

      {/* OpenAPI Import Modal */}
      {showImport && (
        <OpenAPIImport
          onClose={() => setShowImport(false)}
          onSuccess={(result) => {
            setShowImport(false)
            // Optionally show success message
            console.log('Import successful:', result)
          }}
        />
      )}
    </div>
  )
}

export default EndpointsList