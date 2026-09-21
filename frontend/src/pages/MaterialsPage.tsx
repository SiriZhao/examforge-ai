import type {ReviewWorkspace} from '../hooks/useReviewWorkspace';
import {MATERIAL_ROLES,type MaterialRole} from '../api/workspace';
import {Button} from '../design-system/Button';
import {Card} from '../design-system/Card';
import {Upload} from '../design-system/Upload';
import {Icon} from '../design-system/Icon';
export function MaterialsPage({workspace:w}: {workspace:ReviewWorkspace}) {
  return <section className="content-page"><div className="eyebrow">BUILD YOUR LEARNING FOUNDATION</div><h1>{w.project?.course_name || '学习资料'}</h1><p className="muted">确认资料用途，让 AI 更准确地理解课程与考试范围。</p>
    {w.materials.length>0 && <Card><h2>已上传资料</h2>{w.materials.map(file=><div className="material-row" key={file.id}><Icon name="file"/><div><strong title={file.original_filename}>{file.original_filename}</strong><small>{file.pages} 页 · 已解析</small></div><label className="visually-hidden" htmlFor={file.id}>资料用途：{file.original_filename}</label><select id={file.id} value={file.role} disabled={!!w.busy} onChange={e=>w.setMaterials(current=>current.map(item=>item.id===file.id?{...item,role:e.target.value as MaterialRole}:item))}>{MATERIAL_ROLES.map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></div>)}<div className="button-row"><Button loading={w.busy==='正在生成资料诊断'} disabled={!!w.busy || w.files.length>0} onClick={()=>void w.diagnose()}>生成资料诊断<Icon name="arrow" size={16}/></Button></div></Card>}
    <details className="add-materials" open={!w.materials.length || w.files.length>0}><summary>添加学习资料</summary><Upload files={w.files} onChange={w.setFiles} disabled={!!w.busy}/>{w.files.length>0&&<Button loading={w.busy==='正在上传并解析资料'} disabled={!!w.busy} onClick={()=>void w.upload()}>上传 {w.files.length} 份资料</Button>}</details>
  </section>;
}
