'use client';

import { useEffect, useRef, useState } from 'react';
import { VideoCapture as VideoCaptureClass } from '@/lib/videoCapture';
import { Camera, Video, Square, Play, RotateCcw } from 'lucide-react';
import { clsx } from 'clsx';

interface VideoCaptureProps {
  onVideoCaptured: (videoBlob: Blob) => void;
  disabled?: boolean;
}

/**
 * 视频采集组件
 * 支持移动设备视频录制、预览和上传
 */
export function VideoCapture({ onVideoCaptured, disabled = false }: VideoCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const videoCaptureRef = useRef<VideoCaptureClass | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * 初始化摄像头
   */
  const startCamera = async () => {
    try {
      setError(null);
      
      // 检查是否在安全环境中（HTTPS、localhost或内网IP）
      const isSecureContext = window.isSecureContext;
      const isLocalhost = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1';
      const isPrivateIP = /^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|169\.254\.|fc00:|fe80:)/.test(window.location.hostname);
      
      // 检查浏览器是否支持媒体设备API
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (!isSecureContext && !isLocalhost && !isPrivateIP) {
          throw new Error('摄像头功能需要在HTTPS环境下使用。请确保您通过HTTPS访问，或在本地网络/localhost环境下测试。');
        }
        throw new Error('浏览器不支持摄像头功能，请使用Chrome、Firefox、Safari或Edge等现代浏览器。');
      }
      
      const videoCapture = new VideoCaptureClass();
      videoCaptureRef.current = videoCapture;
      
      // 尝试初始化摄像头
      const videoElement = await videoCapture.initialize({
        width: 1280,
        height: 720,
        facingMode: 'environment'
      });

      if (containerRef.current) {
        videoElement.style.width = '100%';
        videoElement.style.height = '100%';
        videoElement.style.objectFit = 'cover';
        videoElement.style.borderRadius = '12px';
        videoElement.style.display = 'block';
        containerRef.current.appendChild(videoElement);
        (videoRef as React.MutableRefObject<HTMLVideoElement | null>).current = videoElement;
        
        // 确保视频自动播放
        videoElement.play().catch(playErr => {
          console.error('视频播放失败:', playErr);
          setError('视频播放失败，请检查浏览器设置');
        });
      }

      setIsCameraActive(true);
    } catch (err) {
      console.error('启动摄像头失败:', err);
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('摄像头权限被拒绝。请点击浏览器地址栏旁的锁图标，允许摄像头访问权限，然后刷新页面重试。');
        } else if (err.name === 'NotFoundError') {
          setError('未找到摄像头设备。请确保您的设备已连接摄像头，并且未被其他应用占用。');
        } else if (err.name === 'NotReadableError') {
          setError('摄像头被其他应用占用。请关闭其他正在使用摄像头的应用程序，然后重试。');
        } else if (err.name === 'OverconstrainedError') {
          setError('摄像头参数设置不合理。请尝试使用较低的分辨率。');
        } else if (err.message.includes('HTTPS')) {
          // 自定义HTTPS错误提示，带解决方案
          const errorMessage = `🔒 摄像头功能需要安全环境
当前访问协议是HTTP，浏览器安全策略限制摄像头只能在HTTPS或本地环境下使用。

✅ 最简单的解决方案：
1. 本地开发直接用 localhost 访问（自动支持）
2. 局域网测试用 127.0.0.1 代替IP访问
3. 手机测试用 ngrok 工具做HTTPS隧道：
   • 下载ngrok后执行：ngrok http 你的端口号
   • 用ngrok生成的HTTPS地址访问

⚡ 公网部署建议：
- 免费证书：用Let's Encrypt申请免费HTTPS证书
- 云服务商：阿里云/腾讯云都提供免费SSL证书
- 一键部署：Vercel/Netlify等平台自动配置HTTPS`;
          setError(errorMessage);
        } else {
          setError(err.message || '无法访问摄像头，请确保已授予相机权限');
        }
      } else {
        setError('无法访问摄像头，请确保已授予相机权限');
      }
    }
  };

  /**
   * 停止摄像头
   */
  const stopCamera = () => {
    try {
      if (videoCaptureRef.current) {
        videoCaptureRef.current.stopCamera();
      }
      if (containerRef.current && videoRef.current) {
        try {
          containerRef.current.removeChild(videoRef.current);
        } catch (removeErr) {
          console.error('移除视频元素失败:', removeErr);
        }
      }
      setIsCameraActive(false);
      setIsRecording(false);
      setRecordingTime(0);
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
      setError(null);
    } catch (err) {
      console.error('停止摄像头失败:', err);
      setError('停止摄像头时发生错误');
    }
  };

  /**
   * 开始录制
   */
  const startRecording = () => {
    if (!videoCaptureRef.current) return;

    try {
      videoCaptureRef.current.startRecording();
      setIsRecording(true);
      setRecordingTime(0);

      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } catch (err) {
      console.error('开始录制失败:', err);
      setError('录制启动失败');
    }
  };

  /**
   * 停止录制
   */
  const stopRecording = async () => {
    if (!videoCaptureRef.current) return;

    try {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }

      const videoBlob = await videoCaptureRef.current.stopRecording();
      setIsRecording(false);
      setRecordingTime(0);

      onVideoCaptured(videoBlob);
    } catch (err) {
      console.error('停止录制失败:', err);
      setError('录制结束失败');
    }
  };

  /**
   * 格式化时间
   */
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * 组件卸载时清理
   */
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="w-full">
      {/* 视频预览区域 */}
      <div
        ref={containerRef}
        className={clsx(
          'relative w-full aspect-video bg-gray-900 rounded-xl overflow-hidden',
          disabled && 'opacity-50 pointer-events-none'
        )}
      >
        {!isCameraActive && (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400">
            <Camera className="w-16 h-16 mb-4" />
            <p className="text-lg">点击下方按钮启动摄像头</p>
          </div>
        )}

        {/* 录制时间显示 */}
        {isRecording && (
          <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-full flex items-center gap-2 z-10">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
            <span className="font-mono font-bold">{formatTime(recordingTime)}</span>
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <div className="whitespace-pre-line leading-relaxed">
            {error}
          </div>
        </div>
      )}

      {/* 控制按钮 */}
      <div className="mt-6 flex justify-center gap-4">
        {!isCameraActive ? (
          <button
            onClick={startCamera}
            disabled={disabled}
            className="flex items-center gap-2 px-8 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <Camera className="w-5 h-5" />
            启动摄像头
          </button>
        ) : (
          <>
            {!isRecording ? (
              <button
                onClick={startRecording}
                className="flex items-center gap-2 px-8 py-3 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
              >
                <Video className="w-5 h-5" />
                开始录制
              </button>
            ) : (
              <button
                onClick={stopRecording}
                className="flex items-center gap-2 px-8 py-3 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors animate-pulse"
              >
                <Square className="w-5 h-5" />
                停止录制
              </button>
            )}
            <button
              onClick={stopCamera}
              className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 transition-colors"
            >
              <RotateCcw className="w-5 h-5" />
              关闭
            </button>
          </>
        )}
      </div>
    </div>
  );
}
