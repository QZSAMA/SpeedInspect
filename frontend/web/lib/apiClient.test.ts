import { getApiBaseUrl } from './apiClient';

describe('API base URL selection', () => {
  it('uses the same-origin API when no public URL is configured', () => {
    expect(getApiBaseUrl(undefined)).toBe('/api/v1');
  });

  it('preserves an explicitly configured API URL for local migration use', () => {
    expect(getApiBaseUrl('http://localhost:8000/api/v1')).toBe('http://localhost:8000/api/v1');
  });

  it('treats whitespace-only configuration as unset', () => {
    expect(getApiBaseUrl('   ')).toBe('/api/v1');
  });
});
