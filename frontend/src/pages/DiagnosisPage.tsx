import type {ReviewWorkspace} from '../hooks/useReviewWorkspace';
import {Button} from '../design-system/Button';
import {Card} from '../design-system/Card';
import {ModeSelector} from '../components/ModeSelector';
export function DiagnosisPage({workspace:w}: {workspace:ReviewWorkspace}) {
  const diagnosis=w.diagnosis;if(!diagnosis)return null;
  return <section className="content-page"><div className="eyebrow">UNDERSTAND BEFORE GENERATING</div><h1>先理清资料，再开始学习。</h1><p className="muted">{w.project?.course_name} · 已解析 {diagnosis.files_processed} 份资料</p><div className="diagnosis-layout"><Card><span className="muted">资料完整度</span><div className="diagnosis-value">{diagnosis.material_completeness}<small>/ 100</small></div><p className="muted">根据资料类型与数量评估，不代表知识掌握程度。</p></Card><Card><h2>推荐生成策略</h2><ul>{diagnosis.recommended_strategy.map((item,i)=><li key={i}>{item}</li>)}</ul></Card></div>
    {diagnosis.missing.length>0 && <Card><h2>还可以补充</h2><p>{diagnosis.missing.join('、')}</p>{diagnosis.risks.map((risk,i)=><p className="muted" key={i}>{risk}</p>)}</Card>}
    <ModeSelector value={w.mode} onChange={w.setMode} disabled={!!w.busy}/><div className="button-row"><Button loading={!!w.busy} onClick={()=>void w.generate()}>确认并开始生成</Button><Button variant="secondary" disabled={!!w.busy} onClick={()=>w.setPage('materials')}>返回资料</Button></div>
  </section>;
}
