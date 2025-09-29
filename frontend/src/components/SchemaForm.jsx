import React, { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { X, Plus, Trash2 } from 'lucide-react'
import { endpointsApi } from '../utils/api'

const SchemaForm = ({ endpointId, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    is_default: false,
    validations: [
      {
        field_name: '',
        field_type: 'string',
        required: true,
        min_length: '',
        max_length: '',
        min_value: '',
        max_value: '',
        pattern: '',
        choices: []
      }
    ]
  })

  const createMutation = useMutation({
    mutationFn: (data) => endpointsApi.createSchema(endpointId, data),
    onSuccess: () => {
      onSuccess()
    }
  })

  const addValidation = () => {
    setFormData({
      ...formData,
      validations: [
        ...formData.validations,
        {
          field_name: '',
          field_type: 'string',
          required: true,
          min_length: '',
          max_length: '',
          min_value: '',
          max_value: '',
          pattern: '',
          choices: []
        }
      ]
    })
  }

  const removeValidation = (index) => {
    const newValidations = formData.validations.filter((_, i) => i !== index)
    setFormData({ ...formData, validations: newValidations })
  }

  const updateValidation = (index, field, value) => {
    const newValidations = [...formData.validations]
    if (field === 'choices') {
      // Parse comma-separated choices
      newValidations[index][field] = value.split(',').map(s => s.trim()).filter(s => s)
    } else {
      newValidations[index][field] = value
    }
    setFormData({ ...formData, validations: newValidations })
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    // Clean up validations
    const cleanValidations = formData.validations.map(validation => {
      const clean = { ...validation }

      // Remove empty string values and convert to proper types
      Object.keys(clean).forEach(key => {
        if (clean[key] === '' || clean[key] === null) {
          delete clean[key]
        } else if (key === 'min_length' || key === 'max_length' || key === 'min_value' || key === 'max_value') {
          if (clean[key] !== '') {
            clean[key] = parseFloat(clean[key])
          } else {
            delete clean[key]
          }
        }
      })

      return clean
    })

    const payload = {
      name: formData.name,
      is_default: formData.is_default,
      validations: JSON.stringify(cleanValidations)
    }

    createMutation.mutate(payload)
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-medium text-gray-900">Create Request Schema</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Schema Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Candidate Data Schema"
                required
              />
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={formData.is_default}
                onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Use as default schema
              </label>
            </div>
          </div>

          {/* Validations */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h4 className="text-md font-medium text-gray-900">Field Validations</h4>
              <button
                type="button"
                onClick={addValidation}
                className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-600 hover:text-blue-500"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add Field
              </button>
            </div>

            <div className="space-y-4 max-h-96 overflow-y-auto">
              {formData.validations.map((validation, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-4">
                    <h5 className="text-sm font-medium text-gray-700">Field {index + 1}</h5>
                    {formData.validations.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeValidation(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    {/* Field Name */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Field Name</label>
                      <input
                        type="text"
                        value={validation.field_name}
                        onChange={(e) => updateValidation(index, 'field_name', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="email"
                        required
                      />
                    </div>

                    {/* Field Type */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Type</label>
                      <select
                        value={validation.field_type}
                        onChange={(e) => updateValidation(index, 'field_type', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="string">String</option>
                        <option value="int">Integer</option>
                        <option value="float">Float</option>
                        <option value="bool">Boolean</option>
                        <option value="email">Email</option>
                      </select>
                    </div>

                    {/* Required */}
                    <div className="col-span-2">
                      <label className="inline-flex items-center">
                        <input
                          type="checkbox"
                          checked={validation.required}
                          onChange={(e) => updateValidation(index, 'required', e.target.checked)}
                          className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-xs text-gray-700">Required</span>
                      </label>
                    </div>

                    {/* Length constraints for strings */}
                    {validation.field_type === 'string' && (
                      <>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Min Length</label>
                          <input
                            type="number"
                            value={validation.min_length}
                            onChange={(e) => updateValidation(index, 'min_length', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Max Length</label>
                          <input
                            type="number"
                            value={validation.max_length}
                            onChange={(e) => updateValidation(index, 'max_length', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </>
                    )}

                    {/* Value constraints for numbers */}
                    {(validation.field_type === 'int' || validation.field_type === 'float') && (
                      <>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Min Value</label>
                          <input
                            type="number"
                            step={validation.field_type === 'float' ? '0.01' : '1'}
                            value={validation.min_value}
                            onChange={(e) => updateValidation(index, 'min_value', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Max Value</label>
                          <input
                            type="number"
                            step={validation.field_type === 'float' ? '0.01' : '1'}
                            value={validation.max_value}
                            onChange={(e) => updateValidation(index, 'max_value', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </>
                    )}

                    {/* Pattern for strings */}
                    {validation.field_type === 'string' && (
                      <div className="col-span-2">
                        <label className="block text-xs font-medium text-gray-700 mb-1">Regex Pattern (optional)</label>
                        <input
                          type="text"
                          value={validation.pattern}
                          onChange={(e) => updateValidation(index, 'pattern', e.target.value)}
                          className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                          placeholder="^[A-Z][a-z]+$"
                        />
                      </div>
                    )}

                    {/* Choices */}
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Allowed Values (comma-separated, optional)
                      </label>
                      <input
                        type="text"
                        value={validation.choices?.join(', ') || ''}
                        onChange={(e) => updateValidation(index, 'choices', e.target.value)}
                        className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="active, inactive, pending"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {createMutation.error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <h4 className="text-red-800 font-medium text-sm">Error creating schema</h4>
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
              {createMutation.isLoading ? 'Creating...' : 'Create Schema'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default SchemaForm