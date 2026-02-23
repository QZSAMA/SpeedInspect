/**
 * 数据安全与加密存储模块
 * 用户视频及检查报告加密存储，符合数据隐私保护法规
 */

import CryptoJS from 'crypto-js';

const ENCRYPTION_KEY = process.env.NEXT_PUBLIC_ENCRYPTION_KEY || 'speed-inspect-secret-key-2024';
const STORAGE_PREFIX = 'speed_inspect_';

/**
 * 加密服务类
 */
export class EncryptionService {
  private key: string;

  constructor(key?: string) {
    this.key = key || ENCRYPTION_KEY;
  }

  /**
   * 加密数据
   */
  encrypt(data: string): string {
    return CryptoJS.AES.encrypt(data, this.key).toString();
  }

  /**
   * 解密数据
   */
  decrypt(encryptedData: string): string {
    const bytes = CryptoJS.AES.decrypt(encryptedData, this.key);
    return bytes.toString(CryptoJS.enc.Utf8);
  }

  /**
   * 生成数据哈希
   */
  hash(data: string): string {
    return CryptoJS.SHA256(data).toString();
  }

  /**
   * 验证数据完整性
   */
  verifyHash(data: string, hash: string): boolean {
    return this.hash(data) === hash;
  }
}

/**
 * 安全存储服务类
 */
export class SecureStorage {
  private encryptionService: EncryptionService;

  constructor(encryptionKey?: string) {
    this.encryptionService = new EncryptionService(encryptionKey);
  }

  /**
   * 存储加密数据
   */
  setItem(key: string, value: any): void {
    try {
      const stringValue = JSON.stringify(value);
      const encryptedValue = this.encryptionService.encrypt(stringValue);
      localStorage.setItem(STORAGE_PREFIX + key, encryptedValue);
    } catch (error) {
      console.error('存储数据失败:', error);
      throw new Error('数据存储失败');
    }
  }

  /**
   * 获取解密数据
   */
  getItem<T>(key: string): T | null {
    try {
      const encryptedValue = localStorage.getItem(STORAGE_PREFIX + key);
      if (!encryptedValue) return null;

      const decryptedValue = this.encryptionService.decrypt(encryptedValue);
      return JSON.parse(decryptedValue) as T;
    } catch (error) {
      console.error('获取数据失败:', error);
      return null;
    }
  }

  /**
   * 删除数据
   */
  removeItem(key: string): void {
    localStorage.removeItem(STORAGE_PREFIX + key);
  }

  /**
   * 清空所有数据
   */
  clear(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(STORAGE_PREFIX)) {
        localStorage.removeItem(key);
      }
    });
  }

  /**
   * 存储大文件（如视频）
   */
  async storeBlob(key: string, blob: Blob): Promise<void> {
    try {
      const arrayBuffer = await blob.arrayBuffer();
      const base64 = this.arrayBufferToBase64(arrayBuffer);
      const encrypted = this.encryptionService.encrypt(base64);
      localStorage.setItem(STORAGE_PREFIX + key, encrypted);
    } catch (error) {
      console.error('存储文件失败:', error);
      throw new Error('文件存储失败');
    }
  }

  /**
   * 获取大文件
   */
  async getBlob(key: string): Promise<Blob | null> {
    try {
      const encrypted = localStorage.getItem(STORAGE_PREFIX + key);
      if (!encrypted) return null;

      const base64 = this.encryptionService.decrypt(encrypted);
      const arrayBuffer = this.base64ToArrayBuffer(base64);
      return new Blob([arrayBuffer]);
    } catch (error) {
      console.error('获取文件失败:', error);
      return null;
    }
  }

  /**
   * ArrayBuffer转Base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Base64转ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
}

// 导出单例实例
export const encryptionService = new EncryptionService();
export const secureStorage = new SecureStorage();
