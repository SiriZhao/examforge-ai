import {useState} from 'react';
import type {ReviewWorkspace} from '../hooks/useReviewWorkspace';
import type {Project} from '../api/workspace';
import {ProjectList} from '../components/ProjectList';
import {Button} from '../design-system/Button';
import {Modal} from '../design-system/Modal';
export function ProjectsPage({workspace:w}: {workspace:ReviewWorkspace}) {
  const [pendingDelete,setPendingDelete]=useState<Project|null>(null);const recent=w.projects.slice(0,3);const history=w.projects.slice(3);
  async function confirmDelete(){if(!pendingDelete)return;const deleted=await w.deleteProject(pendingDelete);if(deleted)setPendingDelete(null);}
  return <section className="content-page"><div className="result-heading"><div><div className="eyebrow">YOUR LEARNING LIBRARY</div><h1>每一份知识，都在这里。</h1></div><Button onClick={w.newProject} disabled={!!w.busy}>新建学习项目</Button></div><p className="muted">重新打开项目继续整理；不再需要的项目可以安全删除。</p>
    <section className="project-library"><div className="library-heading"><h2>最近项目</h2><span>{recent.length} 个</span></div><ProjectList projects={recent} jobs={w.jobs} onOpen={p=>void w.openProject(p)} onDelete={setPendingDelete} disabled={!!w.busy}/>
      <div className="library-heading history-heading"><h2>历史记录</h2><span>{history.length} 个</span></div>{history.length?<ProjectList projects={history} jobs={w.jobs} onOpen={p=>void w.openProject(p)} onDelete={setPendingDelete} disabled={!!w.busy}/>:<div className="history-empty"><p>更早的项目会保存在这里。</p></div>}
    </section><Modal open={!!pendingDelete} title="删除这个项目？" onClose={()=>!w.busy&&setPendingDelete(null)}><div className="delete-confirmation"><p>项目「{pendingDelete?.course_name}」及其中的上传资料会被永久删除。</p><p className="muted">这个操作无法撤销。已经下载到电脑的复习资料不会受到影响。</p><div className="button-row"><Button variant="danger" loading={w.busy==='正在删除项目'} onClick={()=>void confirmDelete()}>确认删除</Button><Button variant="secondary" disabled={!!w.busy} onClick={()=>setPendingDelete(null)}>保留项目</Button></div></div></Modal>
  </section>;
}
