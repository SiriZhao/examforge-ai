import type {JobReference, Project} from '../api/workspace';
import {Icon} from '../design-system/Icon';
export function ProjectList({projects,jobs,onOpen,onDelete,disabled}: {projects:Project[];jobs:Record<string,JobReference>;onOpen:(project:Project)=>void;onDelete?:(project:Project)=>void;disabled?:boolean}) {
  if (!projects.length) return <div className="empty-projects"><Icon name="folder" size={28}/><h4>第一份知识，等你开启</h4><p>上传课程资料后，项目会出现在这里。</p></div>;
  return <div className="project-list">{projects.map(project=>{
    const job=jobs[project.id];
    const status=job?.status==='completed'?'已完成':job?.status==='partial'?'部分完成':job?.status==='failed'||job?.status==='retryable_failed'?'生成失败':job?.status==='retrying'?'正在重试':job?'处理中':'待生成';
    const filename=project.files?.[0]?.original_filename;
    const type=filename?.split('.').pop()?.toUpperCase() || '资料';
    const time=project.created_at ? new Date(project.created_at) : null;
    const running=!!job&&!['completed','partial','failed','retryable_failed'].includes(job.status);
    return <article className="project-item" key={project.id}><button className="project-open" onClick={()=>onOpen(project)} disabled={disabled} aria-label={`重新打开 ${project.course_name}`}>
      <span className="file-badge"><Icon name="file" size={21}/><small>{type}</small></span><span className="project-copy"><strong title={filename || project.course_name}>{filename || project.course_name}</strong>
      <span>{project.course_name} · {project.files?.length || 0} 份资料</span><span className="project-meta"><time dateTime={project.created_at}>{time && !Number.isNaN(time.getTime()) ? time.toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'}) : '创建时间待同步'}</time><span className={`badge ${job?.status==='completed'?'':'pending'}`}>{status}</span></span></span>
    </button>{onDelete&&<button className="project-delete" aria-label={`删除 ${project.course_name}`} title={running?'生成进行中，完成后才能删除':'删除项目'} disabled={disabled||running} onClick={()=>onDelete(project)}><Icon name="trash" size={17}/></button>}</article>;
  })}</div>;
}
