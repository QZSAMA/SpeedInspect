/**
 * 房屋问题类型定义
 */

// 房屋问题类别
export enum ProblemCategory {
  WALL_DAMAGE = 'wall_damage',
  FURNITURE_WEAR = 'furniture_wear',
  PLUMBING_ELECTRIC = 'plumbing_electric',
  FLOORING = 'flooring',
  CEILING = 'ceiling',
  WINDOW_DOOR = 'window_door',
  BATHROOM = 'bathroom',
  KITCHEN = 'kitchen',
  LIGHTING = 'lighting',
  PAINTING = 'painting',
  MOLD = 'mold',
  WATER_DAMAGE = 'water_damage',
  PEST_INFESTATION = 'pest_infestation',
  SAFETY_HAZARD = 'safety_hazard',
  OTHER = 'other'
}

// 问题严重程度 1-5级
export enum SeverityLevel {
  MINOR = 1,
  LOW = 2,
  MODERATE = 3,
  HIGH = 4,
  CRITICAL = 5
}

// 房屋问题
export interface HouseProblem {
  id: string;
  category: ProblemCategory;
  description: string;
  severity: SeverityLevel;
  confidence: number;
  location: string;
  frameTimestamp?: number;
  imageData?: string;
  boundingBox?: BoundingBox;
  repairSuggestion: string;
  estimatedCost: number;
}

// 边界框
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

// 检查报告
export interface InspectionReport {
  id: string;
  createdAt: Date;
  propertyType: PropertyType;
  address?: string;
  problems: HouseProblem[];
  summary: ReportSummary;
  videoUrl?: string;
  thumbnailUrl?: string;
}

// 报告摘要
export interface ReportSummary {
  totalProblems: number;
  criticalCount: number;
  highCount: number;
  moderateCount: number;
  lowCount: number;
  totalEstimatedCost: number;
  overallScore: number;
}

// 房屋类型
export enum PropertyType {
  APARTMENT = 'apartment',
  HOUSE = 'house',
  VILLA = 'villa',
  OFFICE = 'office',
  COMMERCIAL = 'commercial'
}

// 视频采集状态
export interface VideoCaptureState {
  isRecording: boolean;
  duration: number;
  isProcessing: boolean;
  progress: number;
}

// AI分析状态
export interface AIAnalysisState {
  isAnalyzing: boolean;
  currentFrame: number;
  totalFrames: number;
  modelLoaded: boolean;
}

/**
 * 登录凭证
 */
export interface LoginCredentials {
  account: string;
  password: string;
}

/**
 * 注册数据
 */
export interface RegisterData {
  username: string;
  email: string;
  password: string;
  phone?: string;
}

/**
 * 用户信息
 */
export interface User {
  id: string;
  username: string;
  email: string;
  phone?: string;
  role: 'user' | 'admin' | 'superadmin';
  status: 'active' | 'inactive' | 'banned';
  created_at: string;
  updated_at: string;
}

/**
 * 令牌响应
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  expires_at: number;
  user: User;
}

/**
 * 上传文件信息
 */
export interface UploadedFile {
  id: string;
  filename: string;
  original_name: string;
  size: number;
  mime_type: string;
  url: string;
  created_at: string;
}

// 问题类别配置
export const PROBLEM_CATEGORIES: Record<ProblemCategory, { label: string; icon: string }> = {
  [ProblemCategory.WALL_DAMAGE]: { label: '墙面损坏', icon: 'wall' },
  [ProblemCategory.FURNITURE_WEAR]: { label: '家具磨损', icon: 'sofa' },
  [ProblemCategory.PLUMBING_ELECTRIC]: { label: '水电设施', icon: 'zap' },
  [ProblemCategory.FLOORING]: { label: '地板问题', icon: 'floor' },
  [ProblemCategory.CEILING]: { label: '天花板问题', icon: 'ceiling' },
  [ProblemCategory.WINDOW_DOOR]: { label: '门窗问题', icon: 'door' },
  [ProblemCategory.BATHROOM]: { label: '卫生间问题', icon: 'bath' },
  [ProblemCategory.KITCHEN]: { label: '厨房问题', icon: 'kitchen' },
  [ProblemCategory.LIGHTING]: { label: '照明问题', icon: 'lightbulb' },
  [ProblemCategory.PAINTING]: { label: '油漆问题', icon: 'paint' },
  [ProblemCategory.MOLD]: { label: '霉斑问题', icon: 'mold' },
  [ProblemCategory.WATER_DAMAGE]: { label: '水渍问题', icon: 'water' },
  [ProblemCategory.PEST_INFESTATION]: { label: '虫害问题', icon: 'bug' },
  [ProblemCategory.SAFETY_HAZARD]: { label: '安全隐患', icon: 'alert' },
  [ProblemCategory.OTHER]: { label: '其他问题', icon: 'other' }
};
