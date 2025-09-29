import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Trash2, Edit, CheckCircle, XCircle } from 'lucide-react'
import { endpointsApi } from '../utils/api'
import SchemaForm from '../components/SchemaForm'
import TemplateForm from '../components/TemplateForm'

const EndpointDetail = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [showSchemaForm, setShowSchemaForm] = useState(false)
  const [showTemplateForm, setShowTemplateForm] = useState(false)
  const [editingEndpoint, setEditingEndpoint] = useState(false)

  const { data: endpoint, isLoading, error } = useQuery({
    queryKey: ['endpoint', id],
    queryFn: () => endpointsApi.getById(id).then(res => res.data)
  })

  const deleteSchemaeMutation = useMutation({
    mutationFn: endpointsApi.deleteSchema,
    onSuccess: () => {
      queryClient.invalidateQueries(['endpoint', id])
    }
  })

  const deleteTemplateMutation = useMutation({
    mutationFn: endpointsApi.deleteTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries(['endpoint', id])
    }
  })

  const updateEndpointMutation = useMutation({
    mutationFn: (data) => endpointsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['endpoint', id])
      setEditingEndpoint(false)
    }
  })

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
        <h3 className="text-red-800 font-medium">Error loading endpoint</h3>
        <p className="text-red-600">{error.message}</p>
      </div>
    )
  }

  const handleDeleteSchema = (schemaId) => {
    if (window.confirm('Are you sure you want to delete this schema?')) {
      deleteSchemaeMutation.mutate(schemaId)
    }
  }

  const handleDeleteTemplate = (templateId) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      deleteTemplateMutation.mutate(templateId)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <button
            onClick={() => navigate('/endpoints')}
            className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Endpoints
          </button>

          <div className="flex items-center space-x-4 mb-2">
            <h2 className="text-3xl font-bold text-gray-900">{endpoint.name}</h2>
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              endpoint.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {endpoint.is_active ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Active
                </>
              ) : (
                <>
                  <XCircle className="w-4 h-4 mr-1" />
                  Inactive
                </>
              )}
            </span>
          </div>

          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
              endpoint.method === 'GET' ? 'bg-green-100 text-green-800' :
              endpoint.method === 'POST' ? 'bg-blue-100 text-blue-800' :
              endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
              endpoint.method === 'DELETE' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {endpoint.method}
            </span>
            <code className="bg-gray-100 px-2 py-1 rounded text-sm">{endpoint.path}</code>
          </div>

          {endpoint.description && (
            <p className="text-gray-600 mt-2">{endpoint.description}</p>
          )}
        </div>

        <button
          onClick={() => setEditingEndpoint(!editingEndpoint)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          <Edit className="w-4 h-4 mr-2" />
          {editingEndpoint ? 'Cancel Edit' : 'Edit Endpoint'}
        </button>
      </div>

      {/* Edit Form */}
      {editingEndpoint && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Edit Endpoint</h3>
          <EndpointEditForm
            endpoint={endpoint}
            onSubmit={(data) => updateEndpointMutation.mutate(data)}
            onCancel={() => setEditingEndpoint(false)}
            isLoading={updateEndpointMutation.isLoading}
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Schemas */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Request Schemas</h3>
              <button
                onClick={() => setShowSchemaForm(true)}
                className="inline-flex items-center px-3 py-1 border border-transparent rounded-md text-sm font-medium text-blue-600 hover:text-blue-500"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Schema
              </button>
            </div>
          </div>

          <div className="p-6">
            {endpoint.schemas && endpoint.schemas.length > 0 ? (
              <div className="space-y-4">
                {endpoint.schemas.map((schema) => (
                  <div key={schema.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900">{schema.name}</h4>
                          {schema.is_default && (
                            <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                              Default
                            </span>
                          )}
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          <pre className="whitespace-pre-wrap bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                            {JSON.stringify(JSON.parse(schema.validations), null, 2)}
                          </pre>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteSchema(schema.id)}
                        className="p-1 text-red-600 hover:bg-red-100 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No schemas configured</p>
            )}
          </div>
        </div>

        {/* Response Templates */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Response Templates</h3>
              <button
                onClick={() => setShowTemplateForm(true)}
                className="inline-flex items-center px-3 py-1 border border-transparent rounded-md text-sm font-medium text-blue-600 hover:text-blue-500"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Template
              </button>
            </div>
          </div>

          <div className="p-6">
            {endpoint.templates && endpoint.templates.length > 0 ? (
              <div className="space-y-4">
                {endpoint.templates.map((template) => (
                  <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h4 className="font-medium text-gray-900">{template.name}</h4>
                          {template.is_default && (
                            <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                              Default
                            </span>
                          )}
                          <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                            {template.status_code}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          <pre className="whitespace-pre-wrap bg-gray-50 p-2 rounded text-xs overflow-x-auto">
                            {template.template}
                          </pre>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteTemplate(template.id)}
                        className="p-1 text-red-600 hover:bg-red-100 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No templates configured</p>
            )}
          </div>
        </div>
      </div>

      {/* Schema Form Modal */}
      {showSchemaForm && (
        <SchemaForm
          endpointId={id}
          onClose={() => setShowSchemaForm(false)}
          onSuccess={() => {
            setShowSchemaForm(false)
            queryClient.invalidateQueries(['endpoint', id])
          }}
        />
      )}

      {/* Template Form Modal */}
      {showTemplateForm && (
        <TemplateForm
          endpointId={id}
          onClose={() => setShowTemplateForm(false)}
          onSuccess={() => {
            setShowTemplateForm(false)
            queryClient.invalidateQueries(['endpoint', id])
          }}
        />
      )}
    </div>
  )
}

// Endpoint Edit Form Component
const EndpointEditForm = ({ endpoint, onSubmit, onCancel, isLoading }) => {
  const [formData, setFormData] = useState({
    name: endpoint.name,
    path: endpoint.path,
    method: endpoint.method,
    description: endpoint.description || '',
    is_active: endpoint.is_active
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Path</label>
          <input
            type="text"
            value={formData.path}
            onChange={(e) => setFormData({ ...formData, path: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          checked={formData.is_active}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label className="ml-2 block text-sm text-gray-900">Active</label>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </form>
  )
}

export default EndpointDetail