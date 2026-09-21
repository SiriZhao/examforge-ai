import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './recallforge.css';

type Page = 'home' | 'processing' | 'results' | 'system';
type IconName = 'spark' | 'home' | 'folder' | 'cards' | 'arrow' | 'upload' | 'file' | 'settings' | 'check' | 'book' | 'bolt' | 'target' | 'download' | 'close' | 'plus' | 'map';
function Icon({name, size = 20}: {name: IconName; size?: number}) {
  const paths: Record<IconName, React.ReactNode> = {
    spark: <><path d="m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3Z"/><path d="m20 2 .5 1.5L22 4l-1.5.5L20 6l-.5-1.5L18 4l1.5-.5Z"/></>,
    home: <><path d="m3 10 9-7 9 7v10H3Z"/><path d="M9 20v-7h6v7"/></>, folder: <path d="M3 6h7l2 3h9v11H3Zm0 0V4h7l2 2h9v3"/>,
    cards: <><rect x="7" y="6" width="13" height="15" rx="2"/><path d="M16 3H4v14M11 11h5m-5 4h3"/></>,
    arrow: <path d="M4 12h15m-6-6 6 6-6 6"/>, upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5"/></>,
    file: <><path d="M5 3h9l5 5v13H5Zm9 0v6h5M9 13h6m-6 4h6"/></>,
    settings: <><path d="m9 3-1 3-3 1 1 3-2 2 2 2-1 3 3 1 1 3h6l1-3 3-1-1-3 2-2-2-2 1-3-3-1-1-3Z"/><circle cx="12" cy="12" r="3"/></>,
    check: <path d="m5 12 4 4L19 6"/>, book: <><path d="M12 6C8 3 4 4 3 4v15c4-1 7 0 9 2 2-2 5-3 9-2V4c-4-1-7 0-9 2Zm0 0v15"/></>,
    bolt: <path d="m13 2-9 12h7l-1 8 10-13h-7Z"/>, target: <><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></>,
    download: <><path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/></>, close: <path d="m6 6 12 12M6 18 18 6"/>, plus: <path d="M12 5v14M5 12h14"/>,
    map: <><rect x="3" y="9" width="6" height="6" rx="1"/><path d="M9 12h5M14 5v14m0-14h4m-4 7h4m-4 7h4"/><path d="M18 3h3v4h-3Zm0 7h3v4h-3Zm0 7h3v4h-3Z"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
const modes: {title: string; desc: string; icon: IconName; detail: string}[] = [
  {title: '考试突击', desc: '抓住重点，高效备考', icon: 'bolt', detail: '优先整理高频考点、核心公式与易错题'},
  {title: '理解学习', desc: '循序渐进，真正学懂', icon: 'book', detail: '用概念解释、关联知识和例题建立理解'},
  {title: '知识卡片', desc: '主动回忆，记得更牢', icon: 'cards', detail: '把知识拆成简短问答，支持主动回忆'},
  {title: '模拟考试', desc: '以练代学，查漏补缺', icon: 'target', detail: '按资料范围生成试卷与参考解析'},
];
const projects = [
  {name: '高等数学 · 第五章积分.pdf', type: 'PDF', date: '今天 10:24', status: '已完成', sub: '知识总结 · 24 张卡片'},
  {name: '管理学原理 · 期末重点.pptx', type: 'PPT', date: '昨天 19:36', status: '已完成', sub: '知识总结 · 模拟考试'},
  {name: '英语长难句学习笔记.docx', type: 'DOC', date: '09 月 07 日', status: '待生成', sub: '已添加 1 份资料'},
];
const stages = ['上传', 'OCR', '章节理解', 'AI 生成', '完成'];
const tabs = ['知识总结', '思维导图', '问答卡片', '练习题', '模拟考试'];
const summary = '# 定积分与应用\n\n示例内容，仅用于 RecallForge v3.0 设计演示，未解析所选文件。\n\n## 1. 定积分的概念\n定积分表示函数在给定区间内的累积量。几何上，曲线在 x 轴上方的面积取正，下方取负。\n\n## 2. 微积分基本定理\n若 f 在 [a,b] 连续，且 F 是 f 的一个原函数，则 ∫ₐᵇ f(x)dx = F(b) − F(a)。\n\n## 3. 易错提醒\n计算几何面积时，先找零点，再分段取绝对值。\n';

function App() {
  const [page, setPage] = useState<Page>('home');
  const [mode, setMode] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const [drag, setDrag] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [running, setRunning] = useState(false);
  const [tab, setTab] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [answer, setAnswer] = useState<number | null>(null);
  const [exam, setExam] = useState(false);
  const [title, setTitle] = useState(projects[0].name);
  const [settings, setSettings] = useState(false);
  const [toast, setToast] = useState('');
  const input = useRef<HTMLInputElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => { if (settings) dialog.current?.showModal(); else dialog.current?.close(); }, [settings]);
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => setProgress(p => Math.min(100, p + 2)), 220);
    return () => window.clearInterval(timer);
  }, [running]);
  useEffect(() => { if (progress === 100) setRunning(false); }, [progress]);
  useEffect(() => { if (!toast) return; const timer = window.setTimeout(() => setToast(''), 3500); return () => window.clearTimeout(timer); }, [toast]);
  const currentStage = progress === 100 ? 4 : Math.min(3, Math.floor(progress / 25));
  function addFiles(incoming: File[]) {
    const valid = incoming.filter(f => /\.(pdf|ppt|pptx|png|jpe?g|webp|doc|docx)$/i.test(f.name) && f.size <= 50 * 1024 * 1024);
    setError(valid.length !== incoming.length ? '部分文件未添加：请选择支持的格式，且每份文件不超过 50 MB。' : '');
    setFiles(old => [...old, ...valid.filter(f => !old.some(o => o.name === f.name && o.size === f.size))]);
  }
  function start() { setTitle(files[0]?.name || projects[0].name); setProgress(0); setRunning(true); setPage('processing'); }
  function exportContent() {
    const content = [summary, '# 思维导图\n定积分 → 概念与性质 / 计算方法 / 几何应用', '# 问答卡片\n问：定积分与几何面积相同吗？\n答：不一定。定积分是有向面积；几何面积须对各段取绝对值。', '# 练习题\n∫₀¹ 2x dx = ?\n答案：1。原函数为 x²。', '# 模拟考试（样例节选）\n1. 解释定积分的几何意义。\n2. 计算 ∫₀² x dx。\n参考答案：有向面积；2。'][tab];
    const blob = new Blob([content], {type: 'text/markdown;charset=utf-8'}); const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `RecallForge-${tabs[tab]}-示例.md`; a.click(); window.setTimeout(() => URL.revokeObjectURL(url), 1000); setToast('已导出当前内容 · Markdown');
  }
  function openResults(name: string) {setTitle(name); setTab(0); setPage('results');}
  return <div className="rf-app">
    <aside className="sidebar">
      <a className="brand" href="#" onClick={e => {e.preventDefault();setPage('home');}}><span className="brand-mark"><Icon name="spark" size={23}/></span><span>RecallForge<span className="version">3.0</span></span></a>
      <div className="workspace"><span className="avatar">L</span><div>我的学习空间<small>PERSONAL WORKSPACE</small></div><span className="chevron">⌄</span></div>
      <button className="new-project" onClick={() => {setFiles([]); setPage('home');}}><Icon name="plus" size={18}/>新建学习项目<span>＋</span></button>
      <nav aria-label="主导航"><button className={page === 'home' ? 'active' : ''} onClick={() => setPage('home')}><Icon name="home"/>学习首页</button><button className={page === 'results' ? 'active' : ''} onClick={() => openResults(projects[0].name)}><Icon name="folder"/>我的项目<span className="count">3</span></button><button onClick={() => {setPage('results');setTab(2);}}><Icon name="cards"/>知识卡片</button></nav>
      <div className="nav-label">最近打开</div><div className="mini-projects">{projects.slice(0,2).map(p => <button key={p.name} onClick={() => openResults(p.name)}><span className="tiny-dot"/>{p.name.split(' · ')[0]}</button>)}</div>
      <div className="sidebar-bottom"><div className="learning-note"><Icon name="spark"/><h4>让资料，变成你的知识。</h4><p>从整理到理解，<br/>把时间留给真正的学习。</p><div className="note-line"/></div><button className={page === 'system' ? 'active' : ''} onClick={() => setPage('system')}><Icon name="map" size={18}/>组件与设计规范<span>↗</span></button><div className="profile"><span className="avatar">L</span><div>学习者<small>个人空间</small></div><span className="profile-dot"/></div></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="breadcrumb">我的学习空间<span>/</span><strong>{{home:'学习首页', processing:'AI 处理', results:'学习内容', system:'设计规范'}[page]}</strong></div><div className="header-actions"><span className="model-status"><i/>演示模型<span className="status-detail">· 就绪</span></span><button className="icon-button" aria-label="打开设置" onClick={() => setSettings(true)}><Icon name="settings" size={19}/></button></div></header>
      <main>
      {page === 'home' && <div className="dashboard">
        <section className="home-primary"><div className="intro"><div className="eyebrow"><span/>LESS ORGANIZING. MORE UNDERSTANDING.</div><h1>学习，从理解开始<span>。</span></h1><p>把繁杂的资料交给 AI，把清晰的知识留给自己。</p></div>
          <section className={`upload-box ${drag ? 'dragging' : ''}`} aria-label="上传学习资料" onDragOver={e => {e.preventDefault();setDrag(true);}} onDragLeave={() => setDrag(false)} onDrop={e => {e.preventDefault();setDrag(false);addFiles(Array.from(e.dataTransfer.files));}}>
            <div className="upload-art" aria-hidden="true"><div className="paper back-paper">Aa<div/><div/></div><div className="paper front-paper"><Icon name="file" size={24}/><div/><div/><div/></div><span className="art-spark"><Icon name="spark" size={20}/></span></div>
            <h2>{drag ? '松开鼠标，添加资料' : '上传你的学习资料'}</h2><p>拖拽文件到这里，或点击下方按钮选择</p><button className="button primary" onClick={() => input.current?.click()}><Icon name="plus" size={18}/>选择文件</button><input ref={input} className="visually-hidden" type="file" multiple accept=".pdf,.ppt,.pptx,.png,.jpg,.jpeg,.webp,.doc,.docx" onChange={e => {addFiles(Array.from(e.target.files || []));e.target.value='';}}/><div className="file-types"><span>PDF</span><span>PPT</span><span>图片</span><span>Word</span><b>·</b>每份最大 50 MB</div>
          </section>
          {error && <p role="alert" className="error">{error}</p>}
          {files.length > 0 && <section className="selected-files" aria-label="已选择文件">{files.map((f,i) => <div key={`${f.name}-${f.size}`}><Icon name="file"/><span>{f.name}</span><small>{(f.size/1024/1024).toFixed(1)} MB</small><button aria-label={`移除 ${f.name}`} className="icon-button" onClick={() => setFiles(prev => prev.filter((_,idx) => idx !== i))}><Icon name="close" size={16}/></button></div>)}<button className="button primary" onClick={start}>开始生成 · {modes[mode].title}<Icon name="arrow" size={16}/></button><small>交互演示：文件仅在当前页面选择，不会上传或解析。</small></section>}
          <div className="section-heading"><h3>按照你的节奏学习</h3><span>选择一种模式，开始就好</span></div><div className="mode-grid">{modes.map((m,i) => <button key={m.title} className={`mode-card ${mode === i ? 'selected' : ''}`} aria-pressed={mode === i} onClick={() => setMode(i)}><span className="mode-icon"><Icon name={m.icon} size={21}/></span>{mode === i && <span className="selected-check"><Icon name="check" size={12}/></span>}<strong>{m.title}</strong><small>{m.desc}</small></button>)}</div><p className="mode-description"><Icon name="spark" size={14}/>{modes[mode].detail}</p>
          <div className="journey"><span>一份资料，无限可能</span><div>上传资料<i>→</i>AI 理解<i>→</i>生成内容<i>→</i>导出复习</div><button onClick={start}>体验示例<Icon name="arrow" size={15}/></button></div>
        </section>
        <aside className="recent-panel"><div className="section-heading"><h3>最近项目</h3><span className="sample-label">示例</span></div><p className="recent-subtitle">每一次学习，都有迹可循。</p><div className="project-list">{projects.map((p,i) => <button className="project-item" key={p.name} onClick={() => i === 2 ? (setTitle(p.name), setProgress(0), setRunning(true), setPage('processing')) : openResults(p.name)}><span className={`file-badge type-${i}`}><Icon name="file" size={21}/><small>{p.type}</small></span><strong>{p.name}</strong><p>{p.sub}</p><div><time>{p.date}</time><span className={`badge ${i === 2 ? 'pending' : ''}`}>{i !== 2 && <Icon name="check" size={11}/>} {p.status}</span></div></button>)}</div><button className="all-projects" onClick={() => {setToast('右侧展示了全部 3 个示例项目');}}>已显示全部 3 个项目</button><div className="tip"><span>LEARNING TIP / 01</span><h4>读过，不等于记住。</h4><p>试着合上资料，回答一个问题。<br/>主动回忆，让知识真正留下来。</p><button onClick={() => {setPage('results');setTab(2);}}>试试知识卡片<Icon name="arrow" size={15}/></button></div></aside>
      </div>}
      {page === 'processing' && <section className="processing-page"><div className="eyebrow">FROM INFORMATION TO UNDERSTANDING</div><h1>{progress === 100 ? '你的学习内容，准备好了。' : '正在把资料，变成知识。'}</h1><p className="muted">{title} · {modes[mode].title}</p><div className={`processing-orb ${running ? 'animating' : ''}`}><Icon name={progress === 100 ? 'check' : 'spark'} size={42}/></div><div className="progress-heading"><strong>{progress === 100 ? '全部完成' : `${stages[currentStage]}${running ? '进行中' : '已暂停'}`}</strong><span>{progress}%</span></div><div className="progress-track" role="progressbar" aria-label="资料处理进度" aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}><div style={{width: `${progress}%`}}/></div><ol className="stage-list">{stages.map((s,i) => <li key={s} className={i < currentStage || progress === 100 ? 'done' : i === currentStage ? 'current' : ''}><span className="stage-number">{i < currentStage || progress === 100 ? <Icon name="check" size={17}/> : i+1}</span><div><strong>{s}</strong><p>{['检查格式并准备学习资料','识别文字、公式与图片内容','建立章节结构，连接相关概念','整理总结、卡片与练习题','学习内容已就绪，可以查看与导出'][i]}</p></div><small>{i < currentStage || progress === 100 ? '已完成' : i === currentStage ? running ? '处理中' : '已暂停' : '等待中'}</small></li>)}</ol><div className="processing-actions">{progress === 100 ? <button className="button primary" onClick={() => openResults(title)}>查看学习内容<Icon name="arrow" size={17}/></button> : <button className="button secondary" onClick={() => setRunning(!running)}>{running ? '暂停演示' : '继续演示'}</button>}<button className="text-button" onClick={() => {setRunning(false);setPage('home');}}>返回首页</button></div><p className="demo-note">演示流程 · 进度由动画模拟，结果为高等数学示例内容</p></section>}
      {page === 'results' && <section className="results-page"><div className="result-heading"><div><div className="eyebrow">YOUR KNOWLEDGE, CONNECTED</div><h1>把知识，变成自己的。</h1><p className="muted">{title} <span className="sample-label">示例内容</span></p></div><button className="button primary" onClick={exportContent}><Icon name="download" size={17}/>导出当前内容</button></div><div className="result-tabs" role="tablist" aria-label="生成内容">{tabs.map((t,i) => <button key={t} id={`tab-${i}`} role="tab" aria-selected={tab === i} aria-controls="result-panel" onClick={() => {setTab(i);setAnswer(null);}}>{t}</button>)}</div><div className="result-layout"><article id="result-panel" role="tabpanel" aria-labelledby={`tab-${tab}`} className="result-content">
        {tab === 0 && <><div className="document-label">CHAPTER 05 <span>知识总结</span></div><h2>定积分与应用</h2><p className="document-lead">从「无限细分」到「整体累积」，理解微积分的另一半。</p><div className="concept-callout"><Icon name="spark"/><div><strong>先抓住这一个核心</strong><p>定积分，是把连续变化的微小量加起来，得到整体的累积结果。</p></div></div><h3><span>01</span>定积分的概念</h3><p>在区间 [a, b] 内对函数进行分割、近似求和，再取极限。几何上，定积分表示曲线与 x 轴之间的有向面积。</p><h3><span>02</span>微积分基本定理</h3><p>若 f 在 [a, b] 上连续，F 是 f 的一个原函数，那么：</p><div className="formula">∫<sub>a</sub><sup>b</sup> f(x) dx = F(b) − F(a)</div><h3><span>03</span>最容易忽略的地方</h3><p>定积分不一定等于几何面积。曲线在 x 轴下方时贡献为负；求面积时，先找零点，再分段取绝对值。</p><div className="source-label">示例知识 · 来源页码需在接入解析服务后提供</div></>}
        {tab === 1 && <><div className="document-label">KNOWLEDGE MAP</div><h2>让知识，连接起来。</h2><div className="mindmap"><div className="map-root">定积分与应用</div><div className="map-branches">{[['概念与性质','分割 · 求和 · 极限','有向面积与区间可加性'],['计算方法','微积分基本定理','换元积分 · 分部积分'],['几何应用','平面图形面积','旋转体体积']].map(branch => <div key={branch[0]}><strong>{branch[0]}</strong><p>{branch[1]}</p><p>{branch[2]}</p></div>)}</div></div></>}
        {tab === 2 && <><div className="document-label">ACTIVE RECALL <span>示例卡片 01 / 01</span></div><h2>想一想，再看答案。</h2><button className={`flashcard ${flipped ? 'flipped' : ''}`} onClick={() => setFlipped(!flipped)}><span>{flipped ? 'ANSWER / 答案' : 'QUESTION / 问题'}</span><Icon name="cards" size={30}/><strong>{flipped ? '不一定。定积分是有向面积。' : '定积分与曲线下的几何面积，总是相同的吗？'}</strong>{flipped && <p>曲线在 x 轴下方时，积分为负；求几何面积需要分段取绝对值。</p>}<small>点击卡片{flipped ? '返回问题' : '查看答案'} ↻</small></button><p className="muted center">先独立回忆，再核对理解。</p></>}
        {tab === 3 && <><div className="document-label">PRACTICE <span>基础巩固</span></div><h2>用一道题，检验理解。</h2><p>计算 ∫₀¹ 2x dx 的值。</p><div className="answer-options">{['0','1','2','4'].map((a,i) => <button key={a} aria-pressed={answer === i} className={answer === i ? 'chosen' : ''} onClick={() => setAnswer(i)}><span>{'ABCD'[i]}</span>{a}</button>)}</div>{answer !== null && <div className="concept-callout" role="status"><Icon name={answer === 1 ? 'check' : 'book'}/><p>{answer === 1 ? '回答正确。' : '再检查一下积分上下限。'} 2x 的原函数为 x²，代入后得到 1² − 0² = 1。</p></div>}</>}
        {tab === 4 && <><div className="document-label">MOCK EXAM <span>样例节选 · 2 道题</span></div><h2>给知识一次实战机会。</h2><p className="muted">定积分基础 · 建议用时 5 分钟 · 自评练习</p><div className="exam-question"><h3>01 / 概念简答</h3><p>请解释定积分的几何意义。</p><textarea aria-label="第一题答案" placeholder="写下你的理解…"/></div><div className="exam-question"><h3>02 / 计算题</h3><p>计算 ∫₀² x dx，并写出过程。</p><textarea aria-label="第二题答案" placeholder="写下计算过程…"/></div><button className="button primary" onClick={() => setExam(!exam)}>{exam ? '收起参考解析' : '完成作答，查看解析'}</button>{exam && <div className="concept-callout"><p>1. 定积分表示有向面积，x 轴下方部分为负。<br/>2. 原函数为 x²/2，代入上下限得到 2。<br/>本原型提供参考解析，不进行 AI 评分。</p></div>}</>}
      </article><aside className="result-aside"><Icon name="book" size={24}/><h3>本章学习路径</h3><p>理解概念，连接知识，<br/>再通过回忆和练习巩固。</p>{tabs.map((t,i) => <button className={tab === i ? 'active' : ''} key={t} onClick={() => setTab(i)}><span>0{i+1}</span>{t}<Icon name="arrow" size={14}/></button>)}<small>所有页面均为设计演示。<br/>导出格式：Markdown。</small></aside></div></section>}
      {page === 'system' && <section className="system-page"><div className="eyebrow">RECALLFORGE / DESIGN SYSTEM 3.0</div><h1>安静的界面，清晰的思考。</h1><p className="muted">以内容为中心，用克制的颜色与明确的状态支持学习。</p><h2>01 / 颜色与语义</h2><div className="swatches">{[['#245C49','主色 · 深墨绿'],['#EEF4EF','辅助 · 浅鼠尾草'],['#F8F9F6','画布 · 暖白'],['#FFFFFF','内容表面'],['#232D29','主要文字'],['#69736D','次要文字']].map(([color,label]) => <div key={color}><div style={{background:color}}/><strong>{label}</strong><code>{color}</code></div>)}</div><h2>02 / 基础组件</h2><div className="component-grid"><section><h3>Button</h3><div className="button-samples"><button className="button primary" onClick={() => setToast('主按钮：执行页面核心操作')}>主要操作<Icon name="arrow" size={16}/></button><button className="button secondary" onClick={() => setToast('次按钮：辅助操作')}>次要操作</button><button className="button primary" disabled>不可用</button></div><p>高度 40 px · 圆角 8 px · 焦点环 3 px</p></section><section><h3>Card / 模式选择</h3><button className="mode-card selected" onClick={() => setToast('模式卡片：单选，使用 aria-pressed')}><Icon name="bolt"/><strong>考试突击</strong><small>抓住重点，高效备考</small></button><p>圆角 12 px · 内边距 20 px · 选中描边</p></section><section><h3>Progress / 处理状态</h3><div className="progress-track"><div style={{width:'62%'}}/></div><p>上传 → OCR → 章节理解 → AI 生成 → 完成</p><span className="badge">已完成</span> <span className="badge pending">等待中</span><p>动效 220 ms · 支持减少动态效果</p></section><section><h3>布局与排版</h3><p>Sidebar 224 px / Header 72 px</p><p>桌面主栏自适应 / 最近项目 288 px</p><p>标题 36 px / 正文 14 px / 辅助 12 px</p><p>间距使用 4 / 8 / 12 / 16 / 24 / 32 / 48</p></section></div><h2>03 / 交互状态</h2><p className="system-copy">Upload Box：默认、拖入、已选择、格式错误。File Item：文件类型、名称、创建时间、状态文字。Sidebar：默认、悬停、当前页。处理任务：等待、运行、暂停、完成；生产版本应额外实现失败、重试和取消。所有操作均可用键盘聚焦，状态不只依靠颜色区分。</p></section>}
      </main><footer className="app-footer"><span><Icon name="spark" size={13}/>RecallForge · AI-powered Learning Assistant</span><span>DESIGN PREVIEW <b>v3.0</b></span></footer>
    </div>
    <dialog ref={dialog} onCancel={() => setSettings(false)} onClose={() => setSettings(false)} className="settings-dialog"><div className="section-heading"><h2>工作空间设置</h2><button className="icon-button" onClick={() => setSettings(false)} aria-label="关闭设置"><Icon name="close"/></button></div><p>当前为 v3.0 交互设计预览。</p><label>模型状态<input readOnly value="演示模型 · 未连接真实 AI 服务"/></label><label>外观<input readOnly value="浅色 · Forest & Paper"/></label><p className="muted">上传仅用于选择文件演示。生成进度及内容使用样例数据，不读取文件内容。</p><button className="button primary" onClick={() => setSettings(false)}>完成</button></dialog>
    {toast && <div className="toast" role="status"><Icon name="check" size={16}/>{toast}</div>}
  </div>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
