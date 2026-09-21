import type {ReviewWorkspace} from '../hooks/useReviewWorkspace';
import {Upload} from '../design-system/Upload';
import {Button} from '../design-system/Button';
import {Icon} from '../design-system/Icon';
import {ModeSelector} from '../components/ModeSelector';
import {ProjectList} from '../components/ProjectList';
import {ProjectFields} from '../components/ProjectFields';
export function Dashboard({workspace:w}: {workspace:ReviewWorkspace}) {
  return <div className="dashboard"><section className="home-primary"><div className="intro"><div className="eyebrow"><span/>LESS ORGANIZING. MORE UNDERSTANDING.</div><h1>学习，从理解开始<span>。</span></h1><p>把繁杂的资料交给 AI，把清晰的知识留给自己。</p></div>
    {w.project && <div className="resume-banner"><span>当前项目：{w.project.course_name}</span><Button variant="text" disabled={!!w.busy} onClick={()=>w.setPage(w.job || w.jobs[w.project!.id] ? 'processing':'materials')}>继续学习<Icon name="arrow" size={16}/></Button></div>}
    <Upload files={w.files} onChange={w.setFiles} disabled={!!w.busy || !w.ready || !!w.project}/>
    {w.project && <p className="muted">添加更多资料请进入当前项目；开启另一门课程请点击「新建学习项目」。</p>}
    <ModeSelector value={w.mode} onChange={w.setMode} disabled={!!w.busy}/>
    {w.files.length>0 && <form onSubmit={e=>{e.preventDefault();void w.upload();}} className="upload-confirmation"><ProjectFields value={w.form} onChange={w.setForm} disabled={!!w.busy}/><Button type="submit" loading={!!w.busy} disabled={!w.ready}>上传 {w.files.length} 份资料<Icon name="arrow" size={16}/></Button><p className="muted">上传后确认资料用途，再生成学习内容。</p></form>}
    <div className="journey"><span>一份资料，无限可能</span><div>上传资料<i>→</i>AI 理解<i>→</i>生成内容<i>→</i>导出复习</div></div>
    </section><aside className="recent-panel"><div className="section-heading"><h3>最近项目</h3><Button variant="text" disabled={!!w.busy} onClick={()=>w.setPage('projects')}>全部</Button></div><p className="recent-subtitle">每一次学习，都有迹可循。</p><ProjectList projects={w.projects.slice(0,3)} jobs={w.jobs} onOpen={p=>void w.openProject(p)} disabled={!!w.busy}/><div className="tip"><span>LEARNING TIP / 01</span><h4>读过，不等于记住。</h4><p>试着合上资料，回答一个问题。<br/>主动回忆，让知识真正留下来。</p></div></aside></div>;
}
