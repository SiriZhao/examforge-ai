import {useRef} from 'react';
export const RESULT_TABS = ['知识总结','思维导图','问答卡片','练习题','模拟考试'] as const;
export function ResultTabs({value,onChange}: {value:number;onChange:(index:number)=>void}) {
  const refs=useRef<(HTMLButtonElement|null)[]>([]);
  return <div className="result-tabs" role="tablist" aria-label="生成内容">{RESULT_TABS.map((tab,i)=><button key={tab} ref={node=>{refs.current[i]=node;}} id={`result-tab-${i}`} role="tab" type="button" aria-selected={value===i} tabIndex={value===i?0:-1} aria-controls="result-panel" onClick={()=>onChange(i)} onKeyDown={e=>{
    const next=e.key==='ArrowRight'?(i+1)%RESULT_TABS.length:e.key==='ArrowLeft'?(i+RESULT_TABS.length-1)%RESULT_TABS.length:e.key==='Home'?0:e.key==='End'?RESULT_TABS.length-1:null;
    if(next!==null){e.preventDefault();onChange(next);refs.current[next]?.focus();}
  }}>{tab}</button>)}</div>;
}
