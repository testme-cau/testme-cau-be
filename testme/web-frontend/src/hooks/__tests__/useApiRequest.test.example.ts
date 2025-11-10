/**
 * Example test for useApiRequest hook
 * 
 * To run this test:
 * 1. Install dependencies: npm install --save-dev jest @testing-library/react @testing-library/react-hooks
 * 2. Setup Jest config (see TESTING.md)
 * 3. Rename this file to useApiRequest.test.ts
 * 4. Run: npm test
 */

import { renderHook, act, waitFor } from '@testing-library/react'
import { useApiRequest } from '../useApiRequest'

// Mock useToast
jest.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}))

describe('useApiRequest', () => {
  it('should initialize with default values', () => {
    const { result } = renderHook(() => useApiRequest())
    
    expect(result.current.data).toBe(null)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
  })
  
  it('should handle successful API call', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    const mockData = { id: '123', name: 'Test' }
    const mockApiCall = jest.fn().mockResolvedValue(mockData)
    
    await act(async () => {
      const response = await result.current.request(mockApiCall, 'Success!')
      expect(response).toEqual(mockData)
    })
    
    expect(result.current.data).toEqual(mockData)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe(null)
  })
  
  it('should set loading state during API call', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    const mockApiCall = jest.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ data: 'test' }), 100))
    )
    
    let loadingDuringCall = false
    
    act(() => {
      result.current.request(mockApiCall).then(() => {
        // API call completed
      })
    })
    
    // Check loading state immediately after calling
    await waitFor(() => {
      if (result.current.loading) {
        loadingDuringCall = true
      }
    })
    
    expect(loadingDuringCall).toBe(true)
    
    // Wait for completion
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
  })
  
  it('should handle API error', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    const mockError = new Error('API Error')
    const mockApiCall = jest.fn().mockRejectedValue(mockError)
    
    await act(async () => {
      const response = await result.current.request(
        mockApiCall, 
        undefined, 
        'Custom error message'
      )
      expect(response).toBe(null)
    })
    
    expect(result.current.data).toBe(null)
    expect(result.current.loading).toBe(false)
    expect(result.current.error).toBe('Custom error message')
  })
  
  it('should use error message from exception if custom message not provided', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    const mockError = { message: 'Network error' }
    const mockApiCall = jest.fn().mockRejectedValue(mockError)
    
    await act(async () => {
      await result.current.request(mockApiCall)
    })
    
    expect(result.current.error).toBe('Network error')
  })
  
  it('should clear previous error on new successful request', async () => {
    const { result } = renderHook(() => useApiRequest())
    
    // First call - error
    const mockErrorCall = jest.fn().mockRejectedValue(new Error('Error'))
    await act(async () => {
      await result.current.request(mockErrorCall, undefined, 'Error occurred')
    })
    
    expect(result.current.error).toBe('Error occurred')
    
    // Second call - success
    const mockSuccessCall = jest.fn().mockResolvedValue({ data: 'success' })
    await act(async () => {
      await result.current.request(mockSuccessCall)
    })
    
    expect(result.current.error).toBe(null)
    expect(result.current.data).toEqual({ data: 'success' })
  })
  
  it('should handle API call that returns nested data', async () => {
    const { result } = renderHook(() => useApiRequest<{ user: { name: string } }>())
    
    const mockData = { data: { user: { name: 'John' } } }
    const mockApiCall = jest.fn().mockResolvedValue(mockData)
    
    await act(async () => {
      await result.current.request(mockApiCall)
    })
    
    // Hook extracts .data field if present
    expect(result.current.data).toEqual({ user: { name: 'John' } })
  })
})

