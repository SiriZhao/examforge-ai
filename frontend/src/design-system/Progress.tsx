import { Icon } from './Icon';
export type ProgressStage = {label: string; description: string; state: 'waiting' | 'active' | 'done' | 'error'};
export function Progress({value, stages, label}: {value?: number; stages: ProgressStage[]; label: string}) {
  const normalized = value === undefined ? undefined : Math.min(100, Math.max(0, Number.isFinite(value) ? value : 0));
  return <><div className="progress-heading"><strong role="status">{label}</strong><span>{normalized === undefined ? '处理中' : `${normalized}%`}</span></div>
    <div className={`progress-track ${normalized === undefined && !stages.some(stage => stage.state === 'error') ? 'indeterminate' : ''}`} role="progressbar" aria-label="资料处理进度" aria-valuemin={0} aria-valuemax={100} aria-valuenow={normalized}><div style={{width: normalized === undefined ? '35%' : `${normalized}%`}}/></div>
    <ol className="stage-list">{stages.map((stage,i) => <li key={stage.label} className={stage.state === 'active' ? 'current' : stage.state === 'done' ? 'done' : stage.state === 'error' ? 'failed' : ''}><span className="stage-number">{stage.state === 'done' ? <Icon name="check" size={17}/> : stage.state === 'error' ? '!' : i+1}</span><div><strong>{stage.label}</strong><p>{stage.description}</p></div><small>{{waiting:'等待中',active:'处理中',done:'已完成',error:'失败'}[stage.state]}</small></li>)}</ol></>;
}
