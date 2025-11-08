import { useState } from 'react';
import { useToast } from './use-toast';

interface ApiRequestOptions {
  successMessage?: string;
  errorMessage?: string;
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function useApiRequest<T = any>() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = async (
    apiCall: () => Promise<T>,
    options?: ApiRequestOptions
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiCall();
      
      if (options?.successMessage) {
        toast({
          title: options.successMessage,
        });
      }
      
      if (options?.onSuccess) {
        options.onSuccess();
      }
      
      return result;
    } catch (err: any) {
      const error = err instanceof Error ? err : new Error(err.message || 'Unknown error');
      setError(error);
      
      toast({
        title: options?.errorMessage || "오류 발생",
        description: error.message,
        variant: "destructive",
      });
      
      if (options?.onError) {
        options.onError(error);
      }
      
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { execute, loading, error };
}

