import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Paths that are intentionally available before authentication.
const publicPaths = ['/login', '/register', '/api/public'];

function isPublicPath(pathname: string): boolean {
  return publicPaths.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

/**
 * Protects application pages during the migration to server-side sessions.
 *
 * This is only an early navigation guard. Protected API handlers must verify
 * and authorize the server-side session independently.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  const cookieToken = request.cookies.get('access_token')?.value;
  const authorization = request.headers.get('authorization');
  const bearerToken = authorization?.match(/^Bearer\s+(.+)$/i)?.[1];

  if (!cookieToken && !bearerToken) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
