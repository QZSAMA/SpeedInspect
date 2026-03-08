'use client';

import dynamic from 'next/dynamic';

// 禁用SSR，避免TensorFlow.js在服务端渲染出错
const DynamicHomePage = dynamic(() => import('./page.client'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">加载中...</p>
      </div>
    </div>
  ),
});

export default DynamicHomePage;
