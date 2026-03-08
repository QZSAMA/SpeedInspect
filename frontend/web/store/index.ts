import { configureStore } from '@reduxjs/toolkit';
import inspectionReducer from './slices/inspectionSlice';

/**
 * Redux Store 配置
 */
export const makeStore = () => {
  return configureStore({
    reducer: {
      inspection: inspectionReducer
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: {
          ignoredActions: ['inspection/setCurrentReport', 'inspection/saveReport'],
          ignoredPaths: ['inspection.currentReport', 'inspection.reports']
        }
      })
  });
};

// 类型定义
export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore['getState']>;
export type AppDispatch = AppStore['dispatch'];
