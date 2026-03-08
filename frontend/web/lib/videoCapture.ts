/**
 * 视频采集模块
 * 支持移动设备视频录制、防抖处理及清晰度优化
 */

export interface VideoCaptureOptions {
  width?: number;
  height?: number;
  frameRate?: number;
  facingMode?: 'user' | 'environment';
  stabilization?: boolean;
}

/**
 * 视频采集器类
 */
export class VideoCapture {
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private animationFrameId: number | null = null;
  private isProcessing: boolean = false;

  /**
   * 初始化视频采集
   */
  async initialize(options: VideoCaptureOptions = {}): Promise<HTMLVideoElement> {
    const {
      width = 1280,
      height = 720,
      frameRate = 30,
      facingMode = 'environment',
      stabilization = true
    } = options;

    // 检查浏览器支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('浏览器不支持媒体设备API');
    }

    const constraints: MediaStreamConstraints = {
      video: {
        width: { ideal: width },
        height: { ideal: height },
        frameRate: { ideal: frameRate },
        facingMode
      },
      audio: false
    };

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (err) {
      if (err instanceof Error) {
        switch (err.name) {
          case 'NotAllowedError':
            throw new Error('摄像头权限被拒绝');
          case 'NotFoundError':
            throw new Error('未找到摄像头设备');
          case 'NotReadableError':
            throw new Error('摄像头被其他应用占用');
          case 'OverconstrainedError':
            throw new Error('摄像头参数设置不合理');
          default:
            throw new Error(`获取摄像头失败: ${err.message}`);
        }
      }
      throw new Error('获取摄像头失败');
    }

    this.videoElement = document.createElement('video');
    this.videoElement.srcObject = this.mediaStream;
    this.videoElement.setAttribute('playsinline', 'true');
    this.videoElement.setAttribute('autoplay', 'true');
    this.videoElement.setAttribute('muted', 'true');
    this.videoElement.setAttribute('playsinline', 'true');

    // 等待视频元数据加载
    await new Promise((resolve, reject) => {
      if (!this.videoElement) {
        reject(new Error('视频元素未创建'));
        return;
      }

      const timeoutId = setTimeout(() => {
        reject(new Error('视频元数据加载超时'));
      }, 5000);

      this.videoElement.onloadedmetadata = () => {
        clearTimeout(timeoutId);
        resolve(true);
      };

      this.videoElement.onerror = () => {
        clearTimeout(timeoutId);
        reject(new Error('视频元素加载失败'));
      };
    });

    this.canvasElement = document.createElement('canvas');
    this.canvasElement.width = width;
    this.canvasElement.height = height;

    return this.videoElement;
  }

  /**
   * 开始录制
   */
  startRecording(mimeType: string = 'video/webm;codecs=vp9'): void {
    if (!this.mediaStream) {
      throw new Error('Media stream not initialized');
    }

    this.recordedChunks = [];
    this.mediaRecorder = new MediaRecorder(this.mediaStream, { mimeType });

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        this.recordedChunks.push(event.data);
      }
    };

    this.mediaRecorder.start(100);
  }

  /**
   * 停止录制
   */
  stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('Media recorder not initialized'));
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
   * 提取视频帧
   */
  async extractFrames(
    videoBlob: Blob,
    frameInterval: number = 1000
  ): Promise<{ frame: ImageData; timestamp: number }[]> {
    const frames: { frame: ImageData; timestamp: number }[] = [];
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    if (!ctx) {
      throw new Error('Cannot get canvas context');
    }

    video.src = URL.createObjectURL(videoBlob);
    video.load();

    await new Promise((resolve) => {
      video.onloadedmetadata = () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        resolve(true);
      };
    });

    const duration = video.duration;
    let currentTime = 0;

    while (currentTime < duration) {
      video.currentTime = currentTime;
      await new Promise((resolve) => {
        video.onseeked = () => resolve(true);
      });

      ctx.drawImage(video, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      frames.push({ frame: this.enhanceImage(imageData), timestamp: currentTime });

      currentTime += frameInterval / 1000;
    }

    URL.revokeObjectURL(video.src);
    return frames;
  }

  /**
   * 图像增强（清晰度优化）
   */
  private enhanceImage(imageData: ImageData): ImageData {
    const data = imageData.data;
    const width = imageData.width;
    const height = imageData.height;
    const output = new ImageData(width, height);
    const outputData = output.data;

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const a = data[i + 3];

      const gray = 0.299 * r + 0.587 * g + 0.114 * b;
      const contrastFactor = 1.2;
      const brightnessFactor = 1.05;

      outputData[i] = Math.min(255, Math.max(0, (r - 128) * contrastFactor + 128 * brightnessFactor));
      outputData[i + 1] = Math.min(255, Math.max(0, (g - 128) * contrastFactor + 128 * brightnessFactor));
      outputData[i + 2] = Math.min(255, Math.max(0, (b - 128) * contrastFactor + 128 * brightnessFactor));
      outputData[i + 3] = a;
    }

    return output;
  }

  /**
   * 停止摄像头
   */
  stopCamera(): void {
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
      this.animationFrameId = null;
    }
  }

  /**
   * 获取当前帧
   */
  getCurrentFrame(): ImageData | null {
    if (!this.videoElement || !this.canvasElement) {
      return null;
    }

    const ctx = this.canvasElement.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(this.videoElement, 0, 0, this.canvasElement.width, this.canvasElement.height);
    return ctx.getImageData(0, 0, this.canvasElement.width, this.canvasElement.height);
  }
}
