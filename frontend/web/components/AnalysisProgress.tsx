'use client';

import { Brain, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

interface AnalysisProgressProps {
  isAnalyzing: boolean;
  progress: number;
  currentFrame: number;
  totalFrames: number;
  problemsFound: number;
}

/**
 * AI分析进度组件
 * 显示分析进度、当前状态和发现的问题数量
 */
export function AnalysisProgress({
  isAnalyzing,
  progress,
  currentFrame,
  totalFrames,
  problemsFound
}: AnalysisProgressProps) {
  return (
    <div className="w-full bg-white rounded-xl shadow-lg p-6">
      {/* 标题 */}
      <div className="flex items-center gap-3 mb-6">
        <div className={clsx(
          'w-12 h-12 rounded-xl flex items-center justify-center',
          isAnalyzing ? 'bg-blue-100 animate-pulse' : 'bg-green-100'
        )}>
          {isAnalyzing ? (
            <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
          ) : (
            <Brain className="w-6 h-6 text-green-600" />
          )}
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            {isAnalyzing ? 'AI分析中...' : '分析完成'}
          </h3>
          <p className="text-sm text-gray-500">
            {isAnalyzing
              ? '正在使用深度学习模型分析视频内容'
              : '已完成所有帧的分析'}
          </p>
        </div>
      </div>

      {/* 进度条 */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">分析进度</span>
          <span className="text-sm font-bold text-blue-600">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
          <div
            className={clsx(
              'h-full transition-all duration-300 ease-out',
              isAnalyzing ? 'bg-blue-600' : 'bg-green-600'
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-3 gap-4">
        <div className="text-center p-4 bg-gray-50 rounded-xl">
          <div className="text-2xl font-bold text-gray-900">
            {currentFrame}/{totalFrames}
          </div>
          <div className="text-xs text-gray-500 mt-1">已处理帧</div>
        </div>
        <div className="text-center p-4 bg-red-50 rounded-xl">
          <div className="text-2xl font-bold text-red-600">{problemsFound}</div>
          <div className="text-xs text-gray-500 mt-1">发现问题</div>
        </div>
        <div className="text-center p-4 bg-blue-50 rounded-xl">
          <div className="text-2xl font-bold text-blue-600">
            {totalFrames > 0 ? Math.round((currentFrame / totalFrames) * 100) : 0}%
          </div>
          <div className="text-xs text-gray-500 mt-1">完成度</div>
        </div>
      </div>

      {/* 状态提示 */}
      {isAnalyzing && (
        <div className="mt-6 flex items-center gap-2 text-sm text-blue-600 bg-blue-50 p-3 rounded-lg">
          <AlertCircle className="w-4 h-4" />
          <span>正在识别房屋问题，请稍候...</span>
        </div>
      )}

      {!isAnalyzing && totalFrames > 0 && (
        <div className="mt-6 flex items-center gap-2 text-sm text-green-600 bg-green-50 p-3 rounded-lg">
          <CheckCircle className="w-4 h-4" />
          <span>分析已完成，共发现 {problemsFound} 个问题</span>
        </div>
      )}
    </div>
  );
}
