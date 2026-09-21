import {useEffect,useState} from 'react';
import {useReviewWorkspace} from './hooks/useReviewWorkspace';
import {AppShell} from './components/AppShell';
import {ModelSettings} from './components/ModelSettings';
import {Dashboard} from './pages/Dashboard';
import {MaterialsPage} from './pages/MaterialsPage';
import {DiagnosisPage} from './pages/DiagnosisPage';
import {ProcessingPage} from './pages/ProcessingPage';
import {ProjectsPage} from './pages/ProjectsPage';
import {ResultsPage} from './pages/ResultsPage';
import {Button} from './design-system/Button';
import {WelcomeFlow} from './components/WelcomeFlow';

const WELCOME_KEY='recallforge-welcome-complete-v3.1';

export default function App() {
  const workspace=useReviewWorkspace();const [settings,setSettings]=useState(false);
  const [welcome,setWelcome]=useState(()=>localStorage.getItem(WELCOME_KEY)!=='1');
  function completeWelcome(){try{localStorage.setItem(WELCOME_KEY,'1');}catch{/* The flow can still close when storage is unavailable. */}setWelcome(false);}
  useEffect(()=>{document.getElementById('main-content')?.focus({preventScroll:true});window.scrollTo?.(0,0);},[workspace.page]);
  return <AppShell page={workspace.page} onNavigate={workspace.setPage} onNew={workspace.newProject} onSettings={()=>setSettings(true)} modelConfigured={!!workspace.llm.api_key?.trim()} busy={!!workspace.busy}>
    {workspace.error&&<div className="global-notice error" role="alert"><div><strong>{workspace.error.title}</strong><p>{workspace.error.message}</p></div>{!workspace.ready?<Button variant="secondary" disabled={!!workspace.busy} onClick={()=>void workspace.initialize()}>重新连接</Button>:workspace.recovery&&<Button variant="secondary" disabled={!!workspace.busy} onClick={workspace.recovery.run}>{workspace.recovery.label}</Button>}</div>}
    {workspace.busy&&<div className="global-notice operation-status" role="status"><span className="button-spinner"/><div><strong>{workspace.busy}</strong><p>请稍候，完成后页面会自动更新。</p><div className="operation-progress" role="progressbar" aria-label={workspace.busy}><span/></div></div></div>}
    {workspace.page==='home'&&<Dashboard workspace={workspace}/>}
    {workspace.page==='materials'&&<MaterialsPage workspace={workspace}/>}
    {workspace.page==='diagnosis'&&<DiagnosisPage workspace={workspace}/>}
    {workspace.page==='processing'&&<ProcessingPage workspace={workspace}/>}
    {workspace.page==='projects'&&<ProjectsPage workspace={workspace}/>}
    {workspace.page==='results'&&workspace.result&&<ResultsPage key={workspace.job?.job_id} result={workspace.result} jobId={workspace.job?.job_id} onSettings={()=>setSettings(true)}/>}
    <ModelSettings open={settings} value={workspace.llm} onSave={workspace.setLlm} onClose={()=>setSettings(false)}/>
    <WelcomeFlow open={welcome} onComplete={completeWelcome}/>
  </AppShell>;
}
