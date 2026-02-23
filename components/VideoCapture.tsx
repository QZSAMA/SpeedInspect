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
      const videoCapture = new VideoCaptureClass();
      videoCaptureRef.current = videoCapture;
      const videoElement = await videoCapture.initialize({
        width: 1280,
        height: 720,
        facingMode: 'environment'
      });

      if (videoRef.current && containerRef.current) {
        videoElement.style.width = '100%';
        videoElement.style.height = '100%';
        videoElement.style.objectFit = 'cover';
        videoElement.style.borderRadius = '12px';
        containerRef.current.appendChild(videoElement);
        videoRef.current = videoElement;
      }

      setIsCameraActive(true);
    } catch (err) {
      console.error('启动摄像头失败:', err);
      setError('无法访问摄像头，请确保已授予相机权限');
    }
  };

  /**
   * 停止摄像头
   */
  const stopCamera = () => {
    if (videoCaptureRef.current) {
      videoCaptureRef.current.stopCamera();
    }
    if (containerRef.current && videoRef.current) {
      containerRef.current.removeChild(videoRef.current);
    }
    setIsCameraActive(false);
    setIsRecording(false);
    setRecordingTime(0);
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
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
          {error}
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
