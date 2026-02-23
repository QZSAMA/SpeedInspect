import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import {
  InspectionReport,
  HouseProblem,
  VideoCaptureState,
  AIAnalysisState,
  PropertyType
} from '@/types';

/**
 * 检查状态类型
 */
export interface InspectionState {
  currentReport: InspectionReport | null;
  reports: InspectionReport[];
  videoState: VideoCaptureState;
  aiState: AIAnalysisState;
  selectedPropertyType: PropertyType;
  isOfflineMode: boolean;
}

/**
 * 初始状态
 */
const initialState: InspectionState = {
  currentReport: null,
  reports: [],
  videoState: {
    isRecording: false,
    duration: 0,
    isProcessing: false,
    progress: 0
  },
  aiState: {
    isAnalyzing: false,
    currentFrame: 0,
    totalFrames: 0,
    modelLoaded: false
  },
  selectedPropertyType: PropertyType.APARTMENT,
  isOfflineMode: false
};

/**
 * 检查状态切片
 */
const inspectionSlice = createSlice({
  name: 'inspection',
  initialState,
  reducers: {
    /**
     * 设置当前报告
     */
    setCurrentReport: (state, action: PayloadAction<InspectionReport | null>) => {
      state.currentReport = action.payload;
    },

    /**
     * 添加问题到当前报告
     */
    addProblem: (state, action: PayloadAction<HouseProblem>) => {
      if (state.currentReport) {
        state.currentReport.problems.push(action.payload);
        updateReportSummary(state.currentReport);
      }
    },

    /**
     * 批量添加问题
     */
    addProblems: (state, action: PayloadAction<HouseProblem[]>) => {
      if (state.currentReport) {
        state.currentReport.problems.push(...action.payload);
        updateReportSummary(state.currentReport);
      }
    },

    /**
     * 移除问题
     */
    removeProblem: (state, action: PayloadAction<string>) => {
      if (state.currentReport) {
        state.currentReport.problems = state.currentReport.problems.filter(
          p => p.id !== action.payload
        );
        updateReportSummary(state.currentReport);
      }
    },

    /**
     * 保存报告
     */
    saveReport: (state, action: PayloadAction<InspectionReport>) => {
      const existingIndex = state.reports.findIndex(r => r.id === action.payload.id);
      if (existingIndex >= 0) {
        state.reports[existingIndex] = action.payload;
      } else {
        state.reports.push(action.payload);
      }
    },

    /**
     * 删除报告
     */
    deleteReport: (state, action: PayloadAction<string>) => {
      state.reports = state.reports.filter(r => r.id !== action.payload);
    },

    /**
     * 设置视频采集状态
     */
    setVideoState: (state, action: PayloadAction<Partial<VideoCaptureState>>) => {
      state.videoState = { ...state.videoState, ...action.payload };
    },

    /**
     * 设置AI分析状态
     */
    setAIState: (state, action: PayloadAction<Partial<AIAnalysisState>>) => {
      state.aiState = { ...state.aiState, ...action.payload };
    },

    /**
     * 选择房屋类型
     */
    setPropertyType: (state, action: PayloadAction<PropertyType>) => {
      state.selectedPropertyType = action.payload;
    },

    /**
     * 设置离线模式
     */
    setOfflineMode: (state, action: PayloadAction<boolean>) => {
      state.isOfflineMode = action.payload;
    },

    /**
     * 创建新报告
     */
    createNewReport: (state) => {
      const newReport: InspectionReport = {
        id: Date.now().toString(),
        createdAt: new Date(),
        propertyType: state.selectedPropertyType,
        problems: [],
        summary: {
          totalProblems: 0,
          criticalCount: 0,
          highCount: 0,
          moderateCount: 0,
          lowCount: 0,
          totalEstimatedCost: 0,
          overallScore: 100
        }
      };
      state.currentReport = newReport;
    },

    /**
     * 重置检查状态
     */
    resetInspection: () => initialState
  }
});

/**
 * 更新报告摘要
 */
function updateReportSummary(report: InspectionReport) {
  const problems = report.problems;
  let criticalCount = 0;
  let highCount = 0;
  let moderateCount = 0;
  let lowCount = 0;
  let totalEstimatedCost = 0;

  problems.forEach(problem => {
    totalEstimatedCost += problem.estimatedCost;
    switch (problem.severity) {
      case 5:
        criticalCount++;
        break;
      case 4:
        highCount++;
        break;
      case 3:
        moderateCount++;
        break;
      case 1:
      case 2:
        lowCount++;
        break;
    }
  });

  const totalProblems = problems.length;
  const severityPoints = criticalCount * 20 + highCount * 10 + moderateCount * 5 + lowCount * 2;
  const overallScore = Math.max(0, Math.min(100, 100 - severityPoints));

  report.summary = {
    totalProblems,
    criticalCount,
    highCount,
    moderateCount,
    lowCount,
    totalEstimatedCost,
    overallScore
  };
}

export const {
  setCurrentReport,
  addProblem,
  addProblems,
  removeProblem,
  saveReport,
  deleteReport,
  setVideoState,
  setAIState,
  setPropertyType,
  setOfflineMode,
  createNewReport,
  resetInspection
} = inspectionSlice.actions;

export default inspectionSlice.reducer;
