import { NextRequest } from 'next/server';
import { proxy } from './proxy';

function request(pathname: string, accessToken?: string) {
  const headers = accessToken ? { cookie: `access_token=${accessToken}` } : undefined;
  return new NextRequest(`https://speedinspect.example${pathname}`, { headers });
}

function bearerRequest(pathname: string, token: string) {
  return new NextRequest(`https://speedinspect.example${pathname}`, {
    headers: { authorization: `Bearer ${token}` },
  });
}

describe('proxy authentication boundary', () => {
  it('allows public pages without a session', () => {
    const response = proxy(request('/login'));

    expect(response.status).toBe(200);
    expect(response.headers.get('location')).toBeNull();
  });

  it('redirects protected pages to login without a session', () => {
    const response = proxy(request('/inspection'));

    expect(response.status).toBe(307);
    expect(response.headers.get('location')).toBe('https://speedinspect.example/login');
  });

  it('allows protected pages with an access token cookie', () => {
    const response = proxy(request('/inspection', 'test-token'));

    expect(response.status).toBe(200);
    expect(response.headers.get('location')).toBeNull();
  });

  it('allows protected pages with a bearer token header', () => {
    const response = proxy(bearerRequest('/inspection', 'test-token'));

    expect(response.status).toBe(200);
    expect(response.headers.get('location')).toBeNull();
  });
});
