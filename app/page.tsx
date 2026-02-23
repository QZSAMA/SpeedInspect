'use client';

import { useState, useCallback, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  createNewReport,
  addProblems,
  saveReport,
  setVideoState,
  setAIState,
  setPropertyType
} from '@/store/slices/inspectionSlice';
import { RootState, AppDispatch } from '@/store';
import { VideoCapture } from '@/components/VideoCapture';
import { AnalysisProgress } from '@/components/AnalysisProgress';
import { ProblemList } from '@/components/ProblemList';
import { VideoCapture as VideoCaptureClass } from '@/lib/videoCapture';
import { AIAnalyzer } from '@/lib/aiAnalyzer';
import { ReportGenerator } from '@/lib/reportGenerator';
import { PropertyType, HouseProblem } from '@/types';
import {
  Home,
  Building2,
  Factory,
  Briefcase,
  Upload,
  Download,
  RefreshCcw,
  CheckCircle,
  FileText
} from 'lucide-react';
import { clsx } from 'clsx';

/**
 * 主页面组件
 * 房屋状况智能检查系统的核心界面
 */
export default function HomePage() {
  const dispatch = useDispatch<AppDispatch>();
  const { currentReport, videoState, aiState, selectedPropertyType } = useSelector(
    (state: RootState) => state.inspection
  );

  const [step, setStep] = useState<'welcome' | 'capture' | 'analyze' | 'results'>('welcome');
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const videoCaptureRef = useRef<VideoCaptureClass | null>(null);
  const aiAnalyzerRef = useRef<AIAnalyzer | null>(null);

  /**
   * 选择房屋类型
   */
  const handleSelectPropertyType = (type: PropertyType) => {
    dispatch(setPropertyType(type));
    dispatch(createNewReport());
    setStep('capture');
  };

  /**
   * 视频采集完成
   */
  const handleVideoCaptured = useCallback((blob: Blob) => {
    setVideoBlob(blob);
    dispatch(setVideoState({ isRecording: false, isProcessing: true }));
    setStep('analyze');
    startAnalysis(blob);
  }, [dispatch]);

  /**
   * 开始AI分析
   */
  const startAnalysis = async (blob: Blob) => {
    try {
      dispatch(setAIState({ isAnalyzing: true, modelLoaded: false }));

      if (!aiAnalyzerRef.current) {
        aiAnalyzerRef.current = new AIAnalyzer();
        await aiAnalyzerRef.current.initialize();
      }

      dispatch(setAIState({ modelLoaded: true }));

      const videoCapture = new VideoCaptureClass();
      const frames = await videoCapture.extractFrames(blob, 500);

      dispatch(setAIState({ totalFrames: frames.length, currentFrame: 0 }));

      const problems = await aiAnalyzerRef.current.analyzeVideoFrames(
        frames,
        (current, total) => {
          dispatch(setAIState({ currentFrame: current }));
          setAnalysisProgress((current / total) * 100);
        }
      );

      dispatch(addProblems(problems));
      dispatch(setAIState({ isAnalyzing: false }));

      if (currentReport) {
        const updatedReport = {
          ...currentReport,
          problems,
          summary: ReportGenerator.calculateSummary(problems)
        };
        dispatch(saveReport(updatedReport));
      }

      setStep('results');
    } catch (error) {
      console.error('分析失败:', error);
      dispatch(setAIState({ isAnalyzing: false }));
    }
  };

  /**
   * 下载报告
   */
  const handleDownloadReport = () => {
    if (currentReport) {
      ReportGenerator.downloadReport(currentReport, 'html');
    }
  };

  /**
   * 重新开始
   */
  const handleRestart = () => {
    setStep('welcome');
    setVideoBlob(null);
    setAnalysisProgress(0);
    dispatch(createNewReport());
  };

  /**
   * 房屋类型选项
   */
  const propertyTypeOptions = [
    { type: PropertyType.APARTMENT, label: '公寓', icon: Home, description: '适合普通住宅检查' },
    { type: PropertyType.HOUSE, label: '独栋房屋', icon: Building2, description: '适合别墅和独栋住宅' },
    { type: PropertyType.OFFICE, label: '办公室', icon: Briefcase, description: '适合商业办公空间' },
    { type: PropertyType.COMMERCIAL, label: '商业用房', icon: Factory, description: '适合商铺和商业场所' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* 头部 */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">SpeedInspect</h1>
                <p className="text-sm text-gray-500">房屋状况智能检查系统</p>
              </div>
            </div>
            {step !== 'welcome' && (
              <button
                onClick={handleRestart}
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <RefreshCcw className="w-4 h-4" />
                重新开始
              </button>
            )}
          </div>
        </div>
      </header>

      {/* 主要内容 */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* 欢迎页面 */}
        {step === 'welcome' && (
          <div className="space-y-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                欢迎使用房屋智能检查
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                基于AI技术，快速、客观、全面地检查房屋状况，为您的租赁交易和房屋维护提供数据支持
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {propertyTypeOptions.map((option) => (
                <button
                  key={option.type}
                  onClick={() => handleSelectPropertyType(option.type)}
                  className="flex items-start gap-4 p-6 bg-white rounded-xl shadow-sm border-2 border-transparent hover:border-blue-500 transition-all group"
                >
                  <div className="p-3 bg-blue-50 rounded-xl group-hover:bg-blue-100 transition-colors">
                    <option.icon className="w-8 h-8 text-blue-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="text-lg font-semibold text-gray-900">{option.label}</h3>
                    <p className="text-sm text-gray-500 mt-1">{option.description}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 视频采集页面 */}
        {step === 'capture' && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">录制房屋视频</h2>
              <p className="text-gray-600">请缓慢移动摄像头，全面拍摄房屋的每个角落</p>
            </div>
            <VideoCapture onVideoCaptured={handleVideoCaptured} />
          </div>
        )}

        {/* 分析页面 */}
        {step === 'analyze' && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">AI分析中</h2>
              <p className="text-gray-600">正在使用深度学习模型分析视频内容...</p>
            </div>
            <AnalysisProgress
              isAnalyzing={aiState.isAnalyzing}
              progress={analysisProgress}
              currentFrame={aiState.currentFrame}
              totalFrames={aiState.totalFrames}
              problemsFound={currentReport?.problems.length || 0}
            />
          </div>
        )}

        {/* 结果页面 */}
        {step === 'results' && currentReport && (
          <div className="space-y-6">
            {/* 报告摘要 */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">检查完成</h2>
                  <p className="text-gray-600">以下是房屋状况检查报告</p>
                </div>
                <div className="text-right">
                  <div className="text-4xl font-bold text-blue-600">
                    {currentReport.summary.overallScore}
                  </div>
                  <div className="text-sm text-gray-500">综合评分</div>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center p-4 bg-red-50 rounded-xl">
                  <div className="text-2xl font-bold text-red-600">
                    {currentReport.summary.criticalCount}
                  </div>
                  <div className="text-xs text-gray-500">严重</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-xl">
                  <div className="text-2xl font-bold text-orange-600">
                    {currentReport.summary.highCount}
                  </div>
                  <div className="text-xs text-gray-500">高级</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-xl">
                  <div className="text-2xl font-bold text-yellow-600">
                    {currentReport.summary.moderateCount}
                  </div>
                  <div className="text-xs text-gray-500">中等</div>
                </div>
                <div className="text-center p-4 bg-blue-50 rounded-xl">
                  <div className="text-2xl font-bold text-blue-600">
                    {currentReport.summary.lowCount}
                  </div>
                  <div className="text-xs text-gray-500">轻微</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-xl">
                  <div className="text-2xl font-bold text-green-600">
                    ¥{currentReport.summary.totalEstimatedCost.toLocaleString()}
                  </div>
                  <div className="text-xs text-gray-500">预估费用</div>
                </div>
              </div>
            </div>

            {/* 问题列表 */}
            <ProblemList problems={currentReport.problems} />

            {/* 操作按钮 */}
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleDownloadReport}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
              >
                <Download className="w-5 h-5" />
                下载报告
              </button>
              <button
                onClick={handleRestart}
                className="flex items-center gap-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors"
              >
                <RefreshCcw className="w-5 h-5" />
                新的检查
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
