import React from 'react'
import { useForm } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { endpointsApi } from '../utils/api'

const CreateEndpoint = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { register, handleSubmit, formState: { errors } } = useForm()

  const createMutation = useMutation({
    mutationFn: endpointsApi.create,
    onSuccess: (response) => {
      queryClient.invalidateQueries(['endpoints'])
      navigate(`/endpoints/${response.data.id}`)
    }
  })

  const onSubmit = (data) => {
    createMutation.mutate(data)
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/endpoints')}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Endpoints
        </button>
        <h2 className="text-3xl font-bold text-gray-900">Create New Endpoint</h2>
        <p className="text-gray-600 mt-1">Define a new API endpoint for your mock server</p>
      </div>

      {/* Form */}
      <div className="bg-white shadow rounded-lg p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Endpoint Name *
            </label>
            <input
              type="text"
              id="name"
              {...register('name', { required: 'Name is required' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., Candidate Webhook"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
            )}
          </div>

          {/* Path */}
          <div>
            <label htmlFor="path" className="block text-sm font-medium text-gray-700 mb-2">
              URL Path *
            </label>
            <input
              type="text"
              id="path"
              {...register('path', {
                required: 'Path is required',
                pattern: {
                  value: /^\/.*$/,
                  message: 'Path must start with /'
                }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="/webhook/candidate"
            />
            {errors.path && (
              <p className="mt-1 text-sm text-red-600">{errors.path.message}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              The URL path where this endpoint will be available
            </p>
          </div>

          {/* Method */}
          <div>
            <label htmlFor="method" className="block text-sm font-medium text-gray-700 mb-2">
              HTTP Method
            </label>
            <select
              id="method"
              {...register('method')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="POST">POST</option>
              <option value="GET">GET</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
              <option value="PATCH">PATCH</option>
            </select>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              {...register('description')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Optional description of what this endpoint does"
            />
          </div>

          {/* Active */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              {...register('is_active')}
              defaultChecked={true}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
              Active (endpoint will respond to requests)
            </label>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3 pt-6">
            <button
              type="button"
              onClick={() => navigate('/endpoints')}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isLoading}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createMutation.isLoading ? 'Creating...' : 'Create Endpoint'}
            </button>
          </div>
        </form>

        {/* Error Display */}
        {createMutation.error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
            <h3 className="text-red-800 font-medium">Error creating endpoint</h3>
            <p className="text-red-600">{createMutation.error.message}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CreateEndpoint