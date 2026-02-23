/**
 * 报告生成模块
 * 自动生成结构化检查报告
 */

import {
  InspectionReport,
  HouseProblem,
  SeverityLevel,
  ProblemCategory,
  PropertyType,
  PROBLEM_CATEGORIES
} from '@/types';

/**
 * 报告生成器类
 */
export class ReportGenerator {
  /**
   * 创建新报告
   */
  static createReport(
    propertyType: PropertyType,
    address?: string,
    problems: HouseProblem[] = []
  ): InspectionReport {
    const report: InspectionReport = {
      id: Date.now().toString(),
      createdAt: new Date(),
      propertyType,
      address,
      problems,
      summary: this.calculateSummary(problems)
    };
    return report;
  }

  /**
   * 计算报告摘要
   */
  static calculateSummary(problems: HouseProblem[]): InspectionReport['summary'] {
    let criticalCount = 0;
    let highCount = 0;
    let moderateCount = 0;
    let lowCount = 0;
    let totalEstimatedCost = 0;

    problems.forEach(problem => {
      totalEstimatedCost += problem.estimatedCost;
      switch (problem.severity) {
        case SeverityLevel.CRITICAL:
          criticalCount++;
          break;
        case SeverityLevel.HIGH:
          highCount++;
          break;
        case SeverityLevel.MODERATE:
          moderateCount++;
          break;
        case SeverityLevel.LOW:
        case SeverityLevel.MINOR:
          lowCount++;
          break;
      }
    });

    const totalProblems = problems.length;
    const severityPoints = criticalCount * 20 + highCount * 10 + moderateCount * 5 + lowCount * 2;
    const overallScore = Math.max(0, Math.min(100, 100 - severityPoints));

    return {
      totalProblems,
      criticalCount,
      highCount,
      moderateCount,
      lowCount,
      totalEstimatedCost,
      overallScore
    };
  }

  /**
   * 生成HTML报告
   */
  static generateHTML(report: InspectionReport): string {
    const severityColors: Record<SeverityLevel, string> = {
      [SeverityLevel.MINOR]: '#10b981',
      [SeverityLevel.LOW]: '#f59e0b',
      [SeverityLevel.MODERATE]: '#f97316',
      [SeverityLevel.HIGH]: '#ef4444',
      [SeverityLevel.CRITICAL]: '#dc2626'
    };

    const severityLabels: Record<SeverityLevel, string> = {
      [SeverityLevel.MINOR]: '轻微',
      [SeverityLevel.LOW]: '低级',
      [SeverityLevel.MODERATE]: '中等',
      [SeverityLevel.HIGH]: '高级',
      [SeverityLevel.CRITICAL]: '严重'
    };

    const propertyTypeLabels: Record<PropertyType, string> = {
      [PropertyType.APARTMENT]: '公寓',
      [PropertyType.HOUSE]: '独栋房屋',
      [PropertyType.VILLA]: '别墅',
      [PropertyType.OFFICE]: '办公室',
      [PropertyType.COMMERCIAL]: '商业用房'
    };

    const problemsByCategory = this.groupProblemsByCategory(report.problems);

    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>房屋检查报告 - ${report.id}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; background: #f8fafc; padding: 20px; }
    .container { max-width: 900px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); overflow: hidden; }
    .header { background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 40px; text-align: center; }
    .header h1 { font-size: 28px; margin-bottom: 10px; }
    .header p { opacity: 0.9; font-size: 16px; }
    .content { padding: 40px; }
    .section { margin-bottom: 30px; }
    .section-title { font-size: 20px; font-weight: 600; color: #1e293b; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0; }
    .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }
    .info-item { background: #f8fafc; padding: 15px; border-radius: 8px; }
    .info-label { font-size: 12px; color: #64748b; text-transform: uppercase; margin-bottom: 5px; }
    .info-value { font-size: 16px; font-weight: 600; color: #1e293b; }
    .score-card { text-align: center; padding: 30px; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-radius: 12px; margin-bottom: 20px; }
    .score-number { font-size: 64px; font-weight: 700; color: #3b82f6; }
    .score-label { font-size: 16px; color: #64748b; margin-top: 10px; }
    .stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 20px; }
    .stat-item { text-align: center; padding: 15px 10px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
    .stat-number { font-size: 24px; font-weight: 700; }
    .stat-label { font-size: 12px; color: #64748b; margin-top: 5px; }
    .problem-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin-bottom: 15px; }
    .problem-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
    .problem-category { display: flex; align-items: center; gap: 10px; }
    .category-icon { width: 40px; height: 40px; background: #eff6ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .category-name { font-weight: 600; font-size: 16px; }
    .severity-badge { padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; color: white; }
    .problem-description { color: #475569; margin-bottom: 15px; }
    .problem-meta { display: flex; gap: 20px; flex-wrap: wrap; }
    .meta-item { display: flex; align-items: center; gap: 5px; font-size: 14px; color: #64748b; }
    .suggestion { background: #f0fdf4; border-left: 4px solid #10b981; padding: 15px; border-radius: 0 8px 8px 0; margin-top: 15px; }
    .suggestion-title { font-weight: 600; color: #166534; margin-bottom: 8px; }
    .cost { background: #fff7ed; border-left: 4px solid #f97316; padding: 15px; border-radius: 0 8px 8px 0; margin-top: 10px; }
    .cost-title { font-weight: 600; color: #9a3412; margin-bottom: 8px; }
    .footer { text-align: center; padding: 30px; color: #64748b; font-size: 14px; border-top: 1px solid #e2e8f0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🏠 房屋状况智能检查报告</h1>
      <p>SpeedInspect AI 检测系统</p>
    </div>
    <div class="content">
      <div class="section">
        <h2 class="section-title">基本信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <div class="info-label">报告编号</div>
            <div class="info-value">${report.id}</div>
          </div>
          <div class="info-item">
            <div class="info-label">检查日期</div>
            <div class="info-value">${report.createdAt.toLocaleDateString('zh-CN')}</div>
          </div>
          <div class="info-item">
            <div class="info-label">房屋类型</div>
            <div class="info-value">${propertyTypeLabels[report.propertyType]}</div>
          </div>
          <div class="info-item">
            <div class="info-label">检查时间</div>
            <div class="info-value">${report.createdAt.toLocaleTimeString('zh-CN')}</div>
          </div>
        </div>
        ${report.address ? `
        <div class="info-item" style="margin-top: 15px;">
          <div class="info-label">房屋地址</div>
          <div class="info-value">${report.address}</div>
        </div>
        ` : ''}
      </div>
      <div class="section">
        <h2 class="section-title">综合评分</h2>
        <div class="score-card">
          <div class="score-number">${report.summary.overallScore}</div>
          <div class="score-label">房屋状况评分（满分100）</div>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-number" style="color: #dc2626;">${report.summary.criticalCount}</div>
              <div class="stat-label">严重</div>
            </div>
            <div class="stat-item">
              <div class="stat-number" style="color: #ef4444;">${report.summary.highCount}</div>
              <div class="stat-label">高级</div>
            </div>
            <div class="stat-item">
              <div class="stat-number" style="color: #f97316;">${report.summary.moderateCount}</div>
              <div class="stat-label">中等</div>
            </div>
            <div class="stat-item">
              <div class="stat-number" style="color: #f59e0b;">${report.summary.lowCount}</div>
              <div class="stat-label">轻微</div>
            </div>
            <div class="stat-item">
              <div class="stat-number" style="color: #3b82f6;">${report.summary.totalProblems}</div>
              <div class="stat-label">总计</div>
            </div>
          </div>
        </div>
      </div>
      <div class="section">
        <h2 class="section-title">问题详情</h2>
        ${Object.entries(problemsByCategory).map(([category, problems]) => `
          <div style="margin-bottom: 25px;">
            <h3 style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 15px;">
              ${PROBLEM_CATEGORIES[category as ProblemCategory].label}
              <span style="font-size: 14px; font-weight: 400; color: #64748b; margin-left: 10px;">(${problems.length}个问题)</span>
            </h3>
            ${problems.map(problem => `
              <div class="problem-card">
                <div class="problem-header">
                  <div class="problem-category">
                    <div class="category-icon">🔍</div>
                    <div>
                      <div class="category-name">${problem.description}</div>
                      <div style="font-size: 12px; color: #64748b;">置信度: ${(problem.confidence * 100).toFixed(0)}%</div>
                    </div>
                  </div>
                  <span class="severity-badge" style="background: ${severityColors[problem.severity]};">
                    ${severityLabels[problem.severity]}
                  </span>
                </div>
                <div class="problem-meta">
                  <div class="meta-item">📍 位置: ${problem.location}</div>
                </div>
                <div class="suggestion">
                  <div class="suggestion-title">修复建议</div>
                  <div>${problem.repairSuggestion}</div>
                </div>
                <div class="cost">
                  <div class="cost-title">预估费用</div>
                  <div>¥${problem.estimatedCost.toLocaleString()}</div>
                </div>
              </div>
            `).join('')}
          </div>
        `).join('')}
      </div>
      <div class="section">
        <h2 class="section-title">费用汇总</h2>
        <div class="score-card">
          <div class="score-number" style="color: #f97316;">¥${report.summary.totalEstimatedCost.toLocaleString()}</div>
          <div class="score-label">修复总费用预估</div>
        </div>
      </div>
    </div>
    <div class="footer">
      <p>本报告由 SpeedInspect AI 智能检测系统自动生成</p>
      <p>如有疑问，请联系专业人员进行现场核查</p>
      <p style="margin-top: 10px; font-size: 12px;">报告生成时间: ${new Date().toLocaleString('zh-CN')}</p>
    </div>
  </div>
</body>
</html>
    `;
  }

  /**
   * 下载报告
   */
  static downloadReport(report: InspectionReport, format: 'html' | 'json' = 'html'): void {
    let content: string;
    let filename: string;
    let mimeType: string;

    if (format === 'html') {
      content = this.generateHTML(report);
      filename = `inspection-report-${report.id}.html`;
      mimeType = 'text/html';
    } else {
      content = JSON.stringify(report, null, 2);
      filename = `inspection-report-${report.id}.json`;
      mimeType = 'application/json';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * 按类别分组问题
   */
  private static groupProblemsByCategory(
    problems: HouseProblem[]
  ): Record<ProblemCategory, HouseProblem[]> {
    const grouped: Record<ProblemCategory, HouseProblem[]> = {} as any;

    problems.forEach(problem => {
      if (!grouped[problem.category]) {
        grouped[problem.category] = [];
      }
      grouped[problem.category].push(problem);
    });

    return grouped;
  }
}
