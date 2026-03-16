/**
 * Mock视频采集模块
 * 用于测试流程，不需要真实摄像头硬件权限
 * 模拟摄像头启动、录制，最后生成一个假的视频Blob用于测试整个流程
 */

export interface VideoCaptureOptions {
  width?: number;
  height?: number;
  frameRate?: number;
  facingMode?: 'user' | 'environment';
  stabilization?: boolean;
}

/**
 * Mock视频采集器类
 * 模拟真实摄像头行为，但使用Canvas生成模拟视频流
 */
export class VideoCapture {
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private animationFrameId: number | null = null;
  private isRecording: boolean = false;
  private recordingStartTime: number = 0;
  private recordedChunks: Blob[] = [];
  private mediaRecorder: MediaRecorder | null = null;
  private mockStream: MediaStream | null = null;

  /**
   * 初始化模拟摄像头
   * 返回一个带有模拟流的视频元素
   */
  async initialize(options: VideoCaptureOptions = {}): Promise<HTMLVideoElement> {
    const {
      width = 1280,
      height = 720,
    } = options;

    // 创建canvas来生成模拟视频流
    this.canvasElement = document.createElement('canvas');
    this.canvasElement.width = width;
    this.canvasElement.height = height;

    // 从canvas获取媒体流
    this.mockStream = this.canvasElement.captureStream(30);

    // 创建视频元素并设置模拟流
    this.videoElement = document.createElement('video');
    this.videoElement.srcObject = this.mockStream;
    this.videoElement.setAttribute('playsinline', 'true');
    this.videoElement.setAttribute('autoplay', 'true');
    this.videoElement.setAttribute('muted', 'true');
    this.videoElement.muted = true;

    // 开始绘制模拟画面
    this.startMockDrawing();

    // 等待一小段时间让流初始化
    await new Promise(resolve => setTimeout(resolve, 500));

    return this.videoElement;
  }

  /**
   * 在canvas上绘制动态模拟画面
   */
  private startMockDrawing() {
    if (!this.canvasElement) return;

    const ctx = this.canvasElement.getContext('2d');
    if (!ctx) return;

    const width = this.canvasElement.width;
    const height = this.canvasElement.height;
    let startTime = Date.now();

    const drawFrame = () => {
      const elapsed = (Date.now() - startTime) / 1000;

      // 绘制渐变背景
      const gradient = ctx.createLinearGradient(0, 0, width, height);
      gradient.addColorStop(0, `hsl(${elapsed * 30}, 70%, 80%)`);
      gradient.addColorStop(1, `hsl(${elapsed * 30 + 60}, 70%, 90%)`);
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      // 绘制移动的网格（模拟房屋结构的动态效果）
      ctx.strokeStyle = 'rgba(100, 100, 100, 0.3)';
      ctx.lineWidth = 2;
      const gridSize = 80;
      const offset = (elapsed * 20) % gridSize;

      for (let x = -offset; x < width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      for (let y = -offset; y < height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // 绘制模拟"扫描线"效果
      ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
      const scanY = (elapsed * 150) % height;
      ctx.fillRect(0, scanY - 2, width, 4);

      // 绘制录制指示器
      if (this.isRecording) {
        ctx.fillStyle = 'rgba(255, 0, 0, 0.8)';
        ctx.beginPath();
        ctx.arc(40, 40, 15, 0, Math.PI * 2);
        ctx.fill();

        // 脉冲效果
        const pulse = (Math.sin(elapsed * 6) + 1) / 2;
        ctx.strokeStyle = `rgba(255, 0, 0, ${0.5 - pulse * 0.3})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(40, 40, 15 + pulse * 10, 0, Math.PI * 2);
        ctx.stroke();

        // 录制时间文字
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px sans-serif';
        const recordingTime = Math.floor(elapsed - this.recordingStartTime);
        const mins = Math.floor(recordingTime / 60);
        const secs = recordingTime % 60;
        ctx.fillText(`${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`, 70, 47);
      } else {
        // 摄像头就绪提示
        ctx.fillStyle = 'rgba(0, 120, 255, 0.8)';
        ctx.font = 'bold 24px sans-serif';
        ctx.fillText('🎥 摄像头已就绪 (Mock模式)', 40, 50);
      }

      // 绘制"房屋角落"模拟框
      ctx.strokeStyle = `rgba(50, 50, 50, ${0.5 + Math.sin(elapsed) * 0.2})`;
      ctx.lineWidth = 3;
      ctx.strokeRect(width * 0.1, height * 0.15, width * 0.3, height * 0.35);
      ctx.strokeRect(width * 0.55, height * 0.2, width * 0.3, height * 0.3);

      this.animationFrameId = requestAnimationFrame(drawFrame);
    };

    drawFrame();
  }

  /**
   * 开始录制
   */
  startRecording(mimeType: string = 'video/webm;codecs=vp9'): void {
    if (!this.mockStream) {
      throw new Error('Mock stream not initialized');
    }

    this.isRecording = true;
    this.recordingStartTime = Date.now() / 1000;
    this.recordedChunks = [];

    this.mediaRecorder = new MediaRecorder(this.mockStream, { mimeType });

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.recordedChunks.push(event.data);
      }
    };

    this.mediaRecorder.start(100);
  }

  /**
   * 停止录制
   * 如果没有实际数据（录制时间太短），生成一个假的Blob
   */
  stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      this.isRecording = false;

      if (!this.mediaRecorder || this.recordedChunks.length === 0) {
        // 如果没有录制到数据，生成一个最小的WebM文件Blob
        // 这样可以保证上传流程正常进行
        console.warn('No recorded chunks, generating mock video blob');
        const mockBlob = this.generateMockVideoBlob();
        resolve(mockBlob);
        return;
      }

      this.mediaRecorder.onstop = () => {
        const videoBlob = new Blob(this.recordedChunks, { type: 'video/webm' });
        resolve(videoBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * 生成一个最小的可被浏览器识别为视频的Mock Blob
   * 后端会忽略真实内容使用模拟分析，所以这里只需要占位
   */
  private generateMockVideoBlob(): Blob {
    // 最小的WebM文件头（EBML header）
    // 这足够让浏览器识别为video/webm格式
    const minimalWebM = new Uint8Array([
      0x1A, 0x45, 0xDF, 0xA3,  // EBML signature
      0x01, 0x00, 0x00, 0x00,  // EBML size
      0x42, 0xF0, 0x81, 0x01,  // EBML version
      0x42, 0xF1, 0x81, 0x01,  // EBML read version
      0x42, 0xF2, 0x81, 0x40,  // EBML max ID length
      0x42, 0xF3, 0x81, 0x08,  // EBML max size length
      0x42, 0x82, 0x84, 0x42, 0xF8, 0x1F, 0x66, // DocType = "webm"
      0x42, 0x83, 0x81, 0x02,  // DocType version
      0x42, 0x84, 0x81, 0x00,  // DocType read version
      0x1F, 0x43, 0xB6, 0x75,  // Segment
      0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 // Segment size
    ]);

    return new Blob([minimalWebM], { type: 'video/webm' });
  }

  /**
   * 提取视频帧 - mock版本也返回空数组
   */
  async extractFrames(
    videoBlob: Blob,
    frameInterval: number = 1000
  ): Promise<{ frame: ImageData; timestamp: number }[]> {
    // 返回一个空数组，实际AI分析会使用模拟数据
    return [];
  }

  /**
   * 停止摄像头
   */
  stopCamera(): void {
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }

    if (this.mockStream) {
      this.mockStream.getTracks().forEach(track => track.stop());
      this.mockStream = null;
    }

    if (this.videoElement && this.videoElement.srcObject) {
      this.videoElement.srcObject = null;
    }
  }

  /**
   * 获取当前帧
   */
  getCurrentFrame(): ImageData | null {
    if (!this.canvasElement) {
      return null;
    }

    const ctx = this.canvasElement.getContext('2d');
    if (!ctx) return null;

    return ctx.getImageData(0, 0, this.canvasElement.width, this.canvasElement.height);
  }
}
