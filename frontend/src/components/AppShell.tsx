import type {ReactNode} from 'react';
import type {Page} from '../api/workspace';
import {Icon} from '../design-system/Icon';
import {Button} from '../design-system/Button';
export function AppShell({page, onNavigate, onNew, onSettings, modelConfigured, busy, children}: {
  page: Page; onNavigate:(page:Page)=>void;onNew:()=>void;onSettings:()=>void;modelConfigured:boolean;busy:boolean;children:ReactNode;
}) {
  return <div className="rf-app"><a className="skip-link" href="#main-content">跳至主要内容</a><aside className="sidebar">
    <a className="brand" href="#" onClick={e=>{e.preventDefault();if (!busy) onNavigate('home');}} aria-label="RecallForge 学习首页"><span className="brand-mark"><Icon name="spark" size={23}/></span><span>RecallForge<span className="version">3.1</span></span></a>
    <Button className="new-project" style={{marginTop:32}} variant="secondary" disabled={busy} onClick={onNew}><Icon name="plus" size={18}/>新建学习项目</Button>
    <nav aria-label="主导航">{([{id:'home',label:'学习首页',icon:'home'},{id:'projects',label:'我的项目',icon:'folder'}] as const).map(item=><button key={item.id} title={item.label} aria-label={item.label} disabled={busy} className={page===item.id?'active':''} aria-current={page===item.id?'page':undefined} onClick={()=>onNavigate(item.id)}><Icon name={item.icon}/>{item.label}</button>)}</nav>
    <div className="sidebar-bottom"><div className="learning-note"><Icon name="spark"/><h4>让资料，变成你的知识。</h4><p>从整理到理解，<br/>把时间留给真正的学习。</p><div className="note-line"/></div><button onClick={onSettings}><Icon name="settings" size={18}/>模型与设置</button></div>
    </aside><div className="main-shell"><header className="topbar"><div className="breadcrumb">RecallForge<span>/</span><strong>{{home:'学习首页',projects:'我的项目',materials:'学习资料',diagnosis:'资料诊断',processing:'AI 处理',results:'学习内容'}[page]}</strong></div><div className="header-actions"><span className="model-status"><i className={modelConfigured?'':'offline'}/>{modelConfigured?'AI 深度整理':'基础离线整理'}</span><button className="icon-button" aria-label="打开设置" onClick={onSettings}><Icon name="settings" size={19}/></button></div></header>
    <main id="main-content" tabIndex={-1}>{children}</main><footer className="app-footer"><span><Icon name="spark" size={13}/>RecallForge · AI-powered Learning Assistant</span><span>v3.1</span></footer></div></div>;
}
