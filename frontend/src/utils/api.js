import axios from 'axios'

const api = axios.create({
  baseURL: '/admin',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Endpoints API
export const endpointsApi = {
  getAll: () => api.get('/endpoints'),
  getById: (id) => api.get(`/endpoints/${id}`),
  create: (data) => api.post('/endpoints', data),
  update: (id, data) => api.put(`/endpoints/${id}`, data),
  delete: (id) => api.delete(`/endpoints/${id}`),

  // Schema management
  createSchema: (endpointId, data) => api.post(`/endpoints/${endpointId}/schemas`, data),
  deleteSchema: (schemaId) => api.delete(`/schemas/${schemaId}`),

  // Template management
  createTemplate: (endpointId, data) => api.post(`/endpoints/${endpointId}/templates`, data),
  deleteTemplate: (templateId) => api.delete(`/templates/${templateId}`),

  // Template validation
  validateTemplate: (template) => api.post('/templates/validate', { template }),

  // OpenAPI import operations
  validateOpenAPISpec: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/import/openapi/validate', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  importOpenAPISpec: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/import/openapi', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}

export default api