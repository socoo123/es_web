import { useState } from 'react';
import { getHealth } from './api';
import type { Health } from './api';

type State =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'success'; data: Health }
  | { kind: 'error' };

export function HealthPanel() {
  const [state, setState] = useState<State>({ kind: 'idle' });
  if (import.meta.env.VITE_LESSON_PREVIEW) {
    return <aside className="health" aria-label="运行状态">
      <strong>在线静态预览</strong>
      <p>表单与路由可操作。健康 API 请按 F01 在本机启动 Java 后验证。</p>
    </aside>;
  }
  async function check() {
    setState({ kind: 'loading' });
    try { setState({ kind: 'success', data: await getHealth() }); }
    catch { setState({ kind: 'error' }); }
  }
  return <aside className="health" aria-label="运行状态">
    <div role="status" aria-live="polite">
      {state.kind === 'idle' && '先检查 React → Java 是否连通。'}
      {state.kind === 'loading' && '正在连接 Java…'}
      {state.kind === 'success' && `Java 已连接 · ${state.data.service} · ${state.data.stage}`}
      {state.kind === 'error' && '连接失败：确认 Java 运行在 8080，再点击重试。'}
    </div>
    <button type="button" onClick={check} disabled={state.kind === 'loading'}>
      {state.kind === 'error' ? '重试连接' : '检查 Java 连接'}
    </button>
  </aside>;
}
