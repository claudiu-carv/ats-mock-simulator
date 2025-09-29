import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Upload, FileText, CheckCircle, XCircle, AlertTriangle, X } from 'lucide-react'
import { endpointsApi } from '../utils/api'

const OpenAPIImport = ({ onClose, onSuccess }) => {
  const [file, setFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const [validationResult, setValidationResult] = useState(null)
  const queryClient = useQueryClient()

  const validateMutation = useMutation({
    mutationFn: endpointsApi.validateOpenAPISpec,
    onSuccess: (data) => {
      setValidationResult(data)
    },
    onError: (error) => {
      setValidationResult({
        valid: false,
        error: error.response?.data?.error || 'Validation failed'
      })
    }
  })

  const importMutation = useMutation({
    mutationFn: endpointsApi.importOpenAPISpec,
    onSuccess: (data) => {
      queryClient.invalidateQueries(['endpoints'])
      onSuccess(data)
    }
  })

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.name.endsWith('.yml') || droppedFile.name.endsWith('.yaml') || droppedFile.name.endsWith('.json'))) {
      setFile(droppedFile)
      validateFile(droppedFile)
    }
  }

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      validateFile(selectedFile)
    }
  }

  const validateFile = (fileToValidate) => {
    setValidationResult(null)
    validateMutation.mutate(fileToValidate)
  }

  const handleImport = () => {
    if (file && validationResult?.valid) {
      importMutation.mutate(file)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Import OpenAPI Specification</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>
          <p className="mt-1 text-sm text-gray-500">
            Upload a YAML or JSON OpenAPI specification to automatically generate endpoints, schemas, and response templates.
          </p>
        </div>

        <div className="p-6">
          {/* File Upload Area */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? 'border-blue-400 bg-blue-50'
                : file
                ? 'border-green-300 bg-green-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="space-y-2">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
                <p className="text-sm font-medium text-gray-900">{file.name}</p>
                <p className="text-xs text-gray-500">File selected</p>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                <div>
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-500 font-medium">
                      Click to upload
                    </span>
                    <span className="text-gray-500"> or drag and drop</span>
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    className="sr-only"
                    accept=".yml,.yaml,.json"
                    onChange={handleFileSelect}
                  />
                </div>
                <p className="text-xs text-gray-500">YAML or JSON files only</p>
              </div>
            )}
          </div>

          {/* Validation Results */}
          {validateMutation.isLoading && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-sm text-blue-700">Validating OpenAPI specification...</span>
              </div>
            </div>
          )}

          {validationResult && (
            <div className="mt-4">
              {validationResult.valid ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <div className="ml-3 flex-1">
                      <h4 className="text-sm font-medium text-green-800">Valid OpenAPI Specification</h4>
                      <div className="mt-2 text-sm text-green-700">
                        <p>Found {validationResult.endpoints_found} endpoints:</p>
                        <ul className="mt-2 max-h-32 overflow-y-auto space-y-1">
                          {validationResult.endpoints.map((ep, index) => (
                            <li key={index} className="flex items-center justify-between">
                              <span className="font-mono text-xs">
                                {ep.method} {ep.path}
                              </span>
                              <div className="flex space-x-2 text-xs">
                                {ep.has_schema && <span className="bg-blue-100 text-blue-800 px-1 rounded">Schema</span>}
                                {ep.templates_count > 0 && (
                                  <span className="bg-purple-100 text-purple-800 px-1 rounded">
                                    {ep.templates_count} Templates
                                  </span>
                                )}
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {validationResult.warnings?.length > 0 && (
                        <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                          <div className="flex items-start">
                            <AlertTriangle className="w-4 h-4 text-yellow-500 mt-0.5" />
                            <div className="ml-2">
                              <p className="text-xs font-medium text-yellow-800">Warnings:</p>
                              <ul className="text-xs text-yellow-700 list-disc list-inside">
                                {validationResult.warnings.map((warning, i) => (
                                  <li key={i}>{warning}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                    <div className="ml-3">
                      <h4 className="text-sm font-medium text-red-800">Invalid OpenAPI Specification</h4>
                      <div className="mt-2 text-sm text-red-700">
                        <p>{validationResult.error}</p>
                        {validationResult.errors?.map((error, index) => (
                          <p key={index} className="mt-1">{error}</p>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Import Results */}
          {importMutation.isLoading && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="ml-2 text-sm text-blue-700">Importing endpoints...</span>
              </div>
            </div>
          )}

          {importMutation.isSuccess && (
            <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-green-800">Import Successful</h4>
                  <p className="mt-1 text-sm text-green-700">
                    Created {importMutation.data?.total_created} endpoints successfully.
                  </p>
                  {importMutation.data?.errors?.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm font-medium text-red-800">Some errors occurred:</p>
                      <ul className="text-sm text-red-700 list-disc list-inside">
                        {importMutation.data.errors.map((error, i) => (
                          <li key={i}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {importMutation.isError && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start">
                <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                <div className="ml-3">
                  <h4 className="text-sm font-medium text-red-800">Import Failed</h4>
                  <p className="mt-1 text-sm text-red-700">
                    {importMutation.error?.response?.data?.error || 'An error occurred during import'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {importMutation.isSuccess ? 'Close' : 'Cancel'}
          </button>

          {!importMutation.isSuccess && (
            <button
              onClick={handleImport}
              disabled={!file || !validationResult?.valid || importMutation.isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {importMutation.isLoading ? 'Importing...' : 'Import Endpoints'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default OpenAPIImport