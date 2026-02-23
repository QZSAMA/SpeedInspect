'use client';

import { useRef } from 'react';
import { Provider } from 'react-redux';
import { makeStore, AppStore } from './index';

/**
 * Redux Provider 组件
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const storeRef = useRef<AppStore>();
  if (!storeRef.current) {
    storeRef.current = makeStore();
  }

  return <Provider store={storeRef.current}>{children}</Provider>;
}
