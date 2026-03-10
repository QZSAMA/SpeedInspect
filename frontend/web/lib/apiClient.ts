/**
 * API 客户端
 * 封装后端API调用
 */

import axios from 'axios';
import { HouseProblem, InspectionReport, User, LoginCredentials, RegisterData, UploadedFile } from '@/types';

// 创建axios实例
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// 请求拦截器：添加JWT令牌
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理令牌刷新和错误
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // 如果是401错误且不是刷新令牌请求，尝试刷新令牌
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await apiClient.post('/auth/refresh-token', { refresh_token: refreshToken });
          const { access_token, refresh_token } = response.data.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // 刷新失败，清除令牌并跳转到登录页
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * 认证相关API
 */
export const authAPI = {
  /**
   * 用户注册
   */
  register: (data: RegisterData) => 
    apiClient.post('/auth/register', data),
  
  /**
   * 用户登录
   */
  login: (credentials: LoginCredentials) => 
    apiClient.post('/auth/login', credentials),
  
  /**
   * 获取当前用户信息
   */
  getProfile: () => 
    apiClient.get('/users/profile'),
  
  /**
   * 更新用户信息
   */
  updateProfile: (data: Partial<User>) => 
    apiClient.put('/users/profile', data),
};

/**
 * 文件上传相关API
 */
export const filesAPI = {
  /**
   * 上传视频文件
   */
  uploadVideo: (file: Blob, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file, 'inspection-video.webm');
    
    return apiClient.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
  },
  
  /**
   * 获取文件信息
   */
  getFile: (fileId: string) => 
    apiClient.get(`/files/${fileId}`),
  
  /**
   * 下载文件
   */
  downloadFile: (fileId: string) => 
    apiClient.get(`/files/${fileId}/download`, {
      responseType: 'blob',
    }),
};

/**
 * AI分析相关API
 */
export const aiAPI = {
  /**
   * 分析视频
   */
  analyzeVideo: (fileId: string, onProgress?: (progress: number) => void) => 
    apiClient.post('/ai/analyze', { file_id: fileId }, {
      onDownloadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    }),
  
  /**
   * 获取分析状态
   */
  getAnalysisStatus: (taskId: string) => 
    apiClient.get(`/ai/analysis/${taskId}/status`),
};

/**
 * 报告相关API
 */
export const reportsAPI = {
  /**
   * 创建报告
   */
  createReport: (data: Partial<InspectionReport>) => 
    apiClient.post('/reports', data),
  
  /**
   * 获取报告列表
   */
  getReports: (page = 1, pageSize = 10) => 
    apiClient.get('/reports', {
      params: { page, page_size: pageSize },
    }),
  
  /**
   * 获取报告详情
   */
  getReport: (reportId: string) => 
    apiClient.get(`/reports/${reportId}`),
  
  /**
   * 更新报告
   */
  updateReport: (reportId: string, data: Partial<InspectionReport>) => 
    apiClient.put(`/reports/${reportId}`, data),
  
  /**
   * 删除报告
   */
  deleteReport: (reportId: string) => 
    apiClient.delete(`/reports/${reportId}`),
  
  /**
   * 下载报告
   */
  downloadReport: (reportId: string, format: 'pdf' | 'html' | 'json' = 'pdf') => 
    apiClient.get(`/reports/${reportId}/download?format=${format}`, {
      responseType: 'blob',
    }),
};

/**
 * 订单相关API
 */
export const ordersAPI = {
  /**
   * 创建订单
   */
  createOrder: (data: any) => 
    apiClient.post('/orders', data),
  
  /**
   * 获取订单列表
   */
  getOrders: (page = 1, pageSize = 10) => 
    apiClient.get('/orders', {
      params: { page, page_size: pageSize },
    }),
  
  /**
   * 获取订单详情
   */
  getOrder: (orderId: string) => 
    apiClient.get(`/orders/${orderId}`),
  
  /**
   * 支付订单
   */
  payOrder: (orderId: string, paymentMethod: string) => 
    apiClient.post(`/orders/${orderId}/pay`, { payment_method: paymentMethod }),
};

export default apiClient;
