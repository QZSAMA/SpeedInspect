import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 不需要登录的路径
const publicPaths = ['/login', '/register', '/api/public'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // 检查是否是公开路径
  if (publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.next();
  }
  
  // 检查是否有访问令牌
  const accessToken = request.cookies.get('access_token')?.value || 
                      request.headers.get('Authorization')?.split(' ')[1];
  
  // 没有令牌则跳转到登录页
  if (!accessToken) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 匹配所有路径除了:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
