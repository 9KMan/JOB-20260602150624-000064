import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse,
} from 'axios';
import { getToken, refreshToken } from 'next-auth/react';
import type { ApiError } from '@/types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    const token = await getToken();

    if (token?.accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${token.accessToken}`;
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError<ApiError>) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && originalRequest) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      isRefreshing = true;

      try {
        const newToken = await refreshToken();

        if (newToken && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }

        processQueue(null, newToken as string);
        return api(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as Error, null);
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    const apiError: ApiError = {
      message:
        error.response?.data?.message ||
        error.message ||
        'An unexpected error occurred',
      code: error.response?.data?.code,
      statusCode: error.response?.status || 500,
      errors: error.response?.data?.errors,
    };

    return Promise.reject(apiError);
  }
);

export default api;

export const apiGet = async <T>(url: string, params?: Record<string, unknown>) =>
  api.get<T>(url, { params }).then((res) => res.data);

export const apiPost = async <T>(url: string, data?: unknown) =>
  api.post<T>(url, data).then((res) => res.data);

export const apiPut = async <T>(url: string, data?: unknown) =>
  api.put<T>(url, data).then((res) => res.data);

export const apiPatch = async <T>(url: string, data?: unknown) =>
  api.patch<T>(url, data).then((res) => res.data);

export const apiDelete = async <T>(url: string) =>
  api.delete<T>(url).then((res) => res.data);