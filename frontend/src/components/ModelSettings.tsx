import {useEffect,useRef,useState} from 'react';
import type {LLMConfig} from '../api/client';
import {Button} from '../design-system/Button';
import {Modal} from '../design-system/Modal';
import {userFacingError} from '../api/workspace';
export function ModelSettings({open,value,onSave,onClose}: {open:boolean;value:LLMConfig;onSave:(config:LLMConfig)=>void;onClose:()=>void}) {
  const [draft,setDraft]=useState(value);const [status,setStatus]=useState('');const [testing,setTesting]=useState(false);const controller=useRef<AbortController | null>(null);
  useEffect(()=>{if(open){setDraft(value);setStatus('');}return()=>{controller.current?.abort();};},[open,value]);
  useEffect(()=>{if(!open)setTesting(false);},[open]);
  async function test() {
    if(!draft.api_key?.trim() || !draft.base_url?.trim()){setStatus('请先填写 Base URL 和 API Key。');return;}
    let url: URL;
    try {url=new URL(draft.base_url);if(!['http:','https:'].includes(url.protocol))throw new Error();} catch {setStatus('请输入有效的 HTTP 或 HTTPS Base URL。');return;}
    controller.current?.abort();const request=new AbortController();controller.current=request;setTesting(true);setStatus('');
    const timeout=window.setTimeout(()=>request.abort(),15000);
    try {
      const response=await fetch(url.toString().replace(/\/$/,'')+'/models',{headers:{Authorization:`Bearer ${draft.api_key}`},signal:request.signal});
      if(!request.signal.aborted)setStatus(response.ok?'连接测试成功。实际生成仍取决于模型权限与额度。':`连接失败（HTTP ${response.status}），请检查配置。`);
    } catch {if(controller.current===request)setStatus('连接未完成，请检查网络、CORS 或 API 配置。');}
    finally {window.clearTimeout(timeout);if(controller.current===request)setTesting(false);}
  }
  function save() {
    try {localStorage.setItem('examforge-byok',JSON.stringify(draft));onSave(draft);setStatus('已保存到当前浏览器。');}catch(e){setStatus(userFacingError(e,'model').message);}
  }
  return <Modal open={open} title="你的 AI 模型" onClose={onClose}><p className="muted">配置模型后默认使用「AI 深度整理」；未配置时才使用「基础离线整理」。你的资料始终保留在本地工作区。</p><div className="form-grid">
    <label>供应商<select value={draft.provider||'deepseek'} onChange={e=>setDraft({...draft,provider:e.target.value})}><option value="deepseek">DeepSeek</option><option value="openai">OpenAI</option><option value="openai_compatible">OpenAI-compatible</option></select></label>
    <label>模型名称<input value={draft.model||''} onChange={e=>setDraft({...draft,model:e.target.value})} placeholder="填写可用模型名称"/></label>
    <label className="full-width">Base URL<input type="url" value={draft.base_url||''} onChange={e=>setDraft({...draft,base_url:e.target.value})}/></label>
    <label className="full-width">API Key<input type="password" autoComplete="off" value={draft.api_key||''} onChange={e=>setDraft({...draft,api_key:e.target.value})}/></label>
  </div><p className="muted">配置保存在当前浏览器。生成时会将 Key 临时发送给后端并调用所选模型服务；请在自己的设备上使用。</p>{status&&<p role="status">{status}</p>}<div className="button-row"><Button onClick={save} disabled={testing}>保存配置</Button><Button variant="secondary" loading={testing} onClick={()=>void test()}>测试连接</Button></div></Modal>;
}
