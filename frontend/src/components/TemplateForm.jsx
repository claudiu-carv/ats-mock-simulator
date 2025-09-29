import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { X, Eye, Check } from 'lucide-react'
import { endpointsApi } from '../utils/api'

const TemplateForm = ({ endpointId, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    template: JSON.stringify({
      success: true,
      message: 'Request processed successfully',
      data: {
        id: '${mock.uuid}',
        timestamp: '${mock.timestamp}',
        email: '${request.email}',
        name: '${request.name}',
        status: '${mock.enum[active,inactive,pending]}'
      }
    }, null, 2),
    status_code: 200,
    content_type: 'application/json',
    is_default: false
  })

  const [validation, setValidation] = useState(null)
  const [showPreview, setShowPreview] = useState(false)

  const createMutation = useMutation({
    mutationFn: (data) => endpointsApi.createTemplate(endpointId, data),
    onSuccess: () => {
      onSuccess()
    }
  })

  const validateMutation = useMutation({
    mutationFn: endpointsApi.validateTemplate,
    onSuccess: (response) => {
      setValidation(response.data)
    }
  })

  const handleValidate = () => {
    validateMutation.mutate(formData.template)
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const templateExamples = {
    success: JSON.stringify({
      success: true,
      message: 'Request processed successfully',
      data: {
        id: '${mock.uuid}',
        timestamp: '${mock.timestamp}',
        email: '${request.email}',
        name: '${request.name}',
        status: 'active'
      }
    }, null, 2),
    error: JSON.stringify({
      error: true,
      message: 'Validation failed',
      code: 'VALIDATION_ERROR',
      timestamp: '${mock.timestamp}'
    }, null, 2),
    webhook: JSON.stringify({
      event: 'candidate.created',
      data: {
        candidate_id: '${mock.uuid}',
        email: '${request.email}',
        name: '${request.name}',
        phone: '${mock.phone}',
        created_at: '${mock.date.now}',
        source: '${request.source}',
        tags: ['${mock.enum[junior,senior,lead]}', '${mock.enum[remote,onsite,hybrid]}']
      },
      metadata: {
        request_id: '${mock.uuid}',
        timestamp: '${mock.timestamp}'
      }
    }, null, 2)
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-full max-w-6xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">Create Response Template</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Form */}
          <div className="col-span-2">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Template Name</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="e.g., Success Response"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status Code</label>
                  <select
                    value={formData.status_code}
                    onChange={(e) => setFormData({ ...formData, status_code: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="200">200 - OK</option>
                    <option value="201">201 - Created</option>
                    <option value="202">202 - Accepted</option>
                    <option value="400">400 - Bad Request</option>
                    <option value="401">401 - Unauthorized</option>
                    <option value="403">403 - Forbidden</option>
                    <option value="404">404 - Not Found</option>
                    <option value="500">500 - Internal Server Error</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_default}
                  onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Use as default template
                </label>
              </div>

              {/* Template Editor */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-gray-700">Response Template</label>
                  <div className="flex space-x-2">
                    <button
                      type="button"
                      onClick={handleValidate}
                      disabled={validateMutation.isLoading}
                      className="inline-flex items-center px-2 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                    >
                      {validateMutation.isLoading ? 'Validating...' : 'Validate'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowPreview(!showPreview)}
                      className="inline-flex items-center px-2 py-1 border border-gray-300 rounded text-xs font-medium text-gray-700 hover:bg-gray-50"
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      {showPreview ? 'Hide' : 'Preview'}
                    </button>
                  </div>
                </div>

                <textarea
                  value={formData.template}
                  onChange={(e) => setFormData({ ...formData, template: e.target.value })}
                  rows={20}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                  placeholder="Enter your JSON template here..."
                  required
                />

                <div className="mt-2 text-xs text-gray-500">
                  <p className="mb-1">Available placeholders:</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <code>${'{request.field_name}'}</code>
                    <code>${'{mock.uuid}'}</code>
                    <code>${'{mock.int}'}</code>
                    <code>${'{mock.string[6-10]}'}</code>
                    <code>${'{mock.email}'}</code>
                    <code>${'{mock.name}'}</code>
                    <code>${'{mock.date.now}'}</code>
                    <code>${'{mock.timestamp}'}</code>
                    <code>${'{mock.phone}'}</code>
                    <code>${'{mock.bool}'}</code>
                    <code>${'{mock.enum[val1,val2]}'}</code>
                  </div>
                </div>
              </div>

              {/* Validation Results */}
              {validation && (
                <div className={`p-3 rounded-md ${
                  validation.valid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center">
                    {validation.valid ? (
                      <Check className="w-4 h-4 text-green-600 mr-2" />
                    ) : (
                      <X className="w-4 h-4 text-red-600 mr-2" />
                    )}
                    <span className={`text-sm font-medium ${
                      validation.valid ? 'text-green-800' : 'text-red-800'
                    }`}>
                      {validation.valid ? 'Template is valid' : 'Template has errors'}
                    </span>
                  </div>

                  {!validation.valid && validation.errors && (
                    <div className="mt-2">
                      {validation.errors.map((error, index) => (
                        <p key={index} className="text-red-600 text-sm">• {error}</p>
                      ))}
                    </div>
                  )}

                  {validation.valid && (
                    <div className="mt-2 text-sm text-green-700">
                      <p>Found {validation.placeholders.length} placeholders:</p>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {validation.placeholders.map((placeholder, index) => (
                          <code key={index} className="bg-green-100 px-1 rounded text-xs">
                            ${'{' + placeholder + '}'}
                          </code>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Error Display */}
              {createMutation.error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                  <h4 className="text-red-800 font-medium text-sm">Error creating template</h4>
                  <p className="text-red-600 text-sm">{createMutation.error.message}</p>
                </div>
              )}

              {/* Submit */}
              <div className="flex justify-end space-x-3 pt-4 border-t">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isLoading}
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {createMutation.isLoading ? 'Creating...' : 'Create Template'}
                </button>
              </div>
            </form>
          </div>

          {/* Sidebar with examples and preview */}
          <div className="space-y-6">
            {/* Template Examples */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Template Examples</h4>
              <div className="space-y-2">
                {Object.entries(templateExamples).map(([name, template]) => (
                  <button
                    key={name}
                    type="button"
                    onClick={() => setFormData({ ...formData, template })}
                    className="w-full text-left px-2 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
                  >
                    {name.charAt(0).toUpperCase() + name.slice(1)} Response
                  </button>
                ))}
              </div>
            </div>

            {/* Preview */}
            {showPreview && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Preview</h4>
                <div className="bg-white border rounded p-2 text-xs">
                  <pre className="whitespace-pre-wrap font-mono text-gray-800 overflow-x-auto">
                    {formData.template}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TemplateForm