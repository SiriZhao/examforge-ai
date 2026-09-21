import type {ReviewWorkspace} from '../hooks/useReviewWorkspace';
import {Progress,type ProgressStage} from '../design-system/Progress';
import {Button} from '../design-system/Button';
import {Icon} from '../design-system/Icon';
import {userFacingError} from '../api/workspace';

export function ProcessingPage({workspace:w}: {workspace:ReviewWorkspace}) {
  const status=w.job?.status;
  const failed=status==='failed'||status==='retryable_failed';
  const partial=status==='partial'&&!!w.result;
  const complete=status==='completed'&&!!w.result;
  const retrying=status==='retrying';
  const failure=failed?userFacingError(new Error(w.job?.error_code||w.job?.error||''),'generation'):null;
  const index=complete||partial?4:failed?3:status==='ocr'?1:status==='building_evidence'?2:['llm','validating','running','retrying'].includes(status||'')?3:0;
  const labels=['上传与解析','OCR','章节理解','AI 分章生成','保存学习内容'];
  const descriptions=['检查格式并解析资料','识别文字、公式与图片内容','建立章节结构，连接相关概念','按章节与语义块生成并保存 checkpoint','canonical 学习内容已就绪，可随时导出'];
  const stages:ProgressStage[]=labels.map((label,i)=>({
    label,
    description:descriptions[i],
    state:complete?'done':partial?(i===3?'error':'done'):failed?(i<index?'done':i===index?'error':'waiting'):i<index?'done':i===index?'active':'waiting',
  }));
  const title=complete?'你的学习内容，准备好了。':partial?'部分内容已生成并保存。':failed?'这次生成已停止。':retrying?'正在从 checkpoint 继续。':'正在把资料，变成知识。';
  const progressLabel=complete?'生成完成':partial?'部分生成完成':failed?'生成失败 · 已停止':retrying?'正在重试':w.job?.message||'正在获取任务进度';

  return <section className="processing-page"><div className="eyebrow">FROM INFORMATION TO UNDERSTANDING</div><h1>{title}</h1><p className="muted">{w.project?.course_name}</p><div className={`processing-orb ${!complete&&!partial&&!failed&&!w.pollError?'animating':''}`}><Icon name={complete?'check':'spark'} size={42}/></div><Progress value={w.job?.progress} stages={stages} label={progressLabel}/>
    {failure&&<div className="error recovery-panel" role="alert"><strong>{failure.title}</strong><p>{failure.message}</p></div>}
    {partial&&<div className="notice warning" role="status"><strong>已保存可用的部分结果</strong><p>{userFacingError(new Error(w.job?.error_code||''),'generation').message} 重新生成会从未完成章节继续。</p></div>}
    {w.pollError&&<div className="error recovery-panel" role="alert"><strong>{w.pollError.title}</strong><p>{w.pollError.message}</p><p>任务可能仍在服务器运行，重新查询不会重复生成。</p><Button variant="secondary" onClick={w.retryPoll}>重新查询进度</Button></div>}
    <div className="processing-actions">{(complete||partial)&&<Button onClick={()=>w.setPage('results')}>查看学习内容<Icon name="arrow" size={16}/></Button>}{partial&&w.job?.retryable&&<Button variant="secondary" disabled={!!w.busy} onClick={()=>void w.generate()}>从 checkpoint 继续</Button>}{failed&&<Button disabled={!!w.busy} onClick={()=>{if(w.diagnosis)void w.generate();else w.setPage('materials');}}>{w.job?.retryable?'从 checkpoint 继续':'返回资料后重试'}</Button>}<Button variant="text" onClick={()=>w.setPage('home')}>返回首页</Button></div>
    {!complete&&!partial&&!failed&&<p className="demo-note">处理进度由服务器实时返回，等待期间可以返回首页。</p>}
  </section>;
}
