'use client';

import { HouseProblem, SeverityLevel, PROBLEM_CATEGORIES, ProblemCategory } from '@/types';
import { AlertTriangle, CheckCircle, XCircle, Info, Wrench, DollarSign } from 'lucide-react';
import { clsx } from 'clsx';

interface ProblemListProps {
  problems: HouseProblem[];
  onRemoveProblem?: (problemId: string) => void;
  showDetails?: boolean;
}

/**
 * 问题列表组件
 * 显示检测到的房屋问题，支持按严重程度和类别筛选
 */
export function ProblemList({ problems, onRemoveProblem, showDetails = true }: ProblemListProps) {
  /**
   * 获取严重程度颜色
   */
  const getSeverityColor = (severity: SeverityLevel) => {
    switch (severity) {
      case SeverityLevel.CRITICAL:
        return 'bg-red-100 text-red-700 border-red-200';
      case SeverityLevel.HIGH:
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case SeverityLevel.MODERATE:
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case SeverityLevel.LOW:
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case SeverityLevel.MINOR:
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  /**
   * 获取严重程度图标
   */
  const getSeverityIcon = (severity: SeverityLevel) => {
    switch (severity) {
      case SeverityLevel.CRITICAL:
        return <XCircle className="w-5 h-5" />;
      case SeverityLevel.HIGH:
        return <AlertTriangle className="w-5 h-5" />;
      case SeverityLevel.MODERATE:
        return <AlertTriangle className="w-5 h-5" />;
      case SeverityLevel.LOW:
        return <Info className="w-5 h-5" />;
      case SeverityLevel.MINOR:
        return <CheckCircle className="w-5 h-5" />;
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  /**
   * 获取严重程度标签
   */
  const getSeverityLabel = (severity: SeverityLevel) => {
    switch (severity) {
      case SeverityLevel.CRITICAL:
        return '严重';
      case SeverityLevel.HIGH:
        return '高级';
      case SeverityLevel.MODERATE:
        return '中等';
      case SeverityLevel.LOW:
        return '低级';
      case SeverityLevel.MINOR:
        return '轻微';
      default:
        return '未知';
    }
  };

  /**
   * 按严重程度排序问题
   */
  const sortedProblems = [...problems].sort((a, b) => b.severity - a.severity);

  if (problems.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl shadow-lg p-12 text-center">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-gray-900 mb-2">没有发现问题</h3>
        <p className="text-gray-500">房屋状况良好，继续保持！</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* 问题统计 */}
      <div className="bg-white rounded-xl shadow-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">
              发现 {problems.length} 个问题
            </h3>
            <p className="text-sm text-gray-500">按严重程度排序显示</p>
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
            <span className="text-sm text-gray-600">请及时处理</span>
          </div>
        </div>
      </div>

      {/* 问题列表 */}
      {sortedProblems.map((problem) => (
        <div
          key={problem.id}
          className="bg-white rounded-xl shadow-lg overflow-hidden"
        >
          {/* 问题头部 */}
          <div className="p-4 border-b border-gray-100">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                <div className={clsx('p-2 rounded-lg', getSeverityColor(problem.severity))}>
                  {getSeverityIcon(problem.severity)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-bold text-gray-900">{problem.description}</h4>
                    <span className={clsx(
                      'px-2 py-0.5 text-xs font-medium rounded-full border',
                      getSeverityColor(problem.severity)
                    )}>
                      {getSeverityLabel(problem.severity)}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Info className="w-4 h-4" />
                      {PROBLEM_CATEGORIES[problem.category].label}
                    </span>
                    <span className="flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      {problem.location}
                    </span>
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      置信度 {(problem.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
              {onRemoveProblem && (
                <button
                  onClick={() => onRemoveProblem(problem.id)}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <XCircle className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>

          {/* 问题详情 */}
          {showDetails && (
            <div className="p-4 space-y-4 bg-gray-50">
              {/* 修复建议 */}
              <div className="flex items-start gap-3">
                <div className="p-2 bg-green-100 text-green-600 rounded-lg">
                  <Wrench className="w-4 h-4" />
                </div>
                <div>
                  <h5 className="font-semibold text-gray-900 text-sm mb-1">修复建议</h5>
                  <p className="text-sm text-gray-600">{problem.repairSuggestion}</p>
                </div>
              </div>

              {/* 预估费用 */}
              <div className="flex items-start gap-3">
                <div className="p-2 bg-orange-100 text-orange-600 rounded-lg">
                  <DollarSign className="w-4 h-4" />
                </div>
                <div>
                  <h5 className="font-semibold text-gray-900 text-sm mb-1">预估费用</h5>
                  <p className="text-lg font-bold text-orange-600">
                    ¥{problem.estimatedCost.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
