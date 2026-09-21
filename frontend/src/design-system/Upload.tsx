import { useId, useRef, useState } from 'react';
import { Button } from './Button';
import { Icon } from './Icon';
export const SUPPORTED_EXTENSIONS = ['pdf','pptx','docx','md','txt','png','jpg','jpeg'];
export function validateFiles(incoming: File[], existing: File[] = []): {files: File[]; errors: string[]} {
  const files = [...existing]; const errors: string[] = [];
  for (const file of incoming) {
    if (!SUPPORTED_EXTENSIONS.includes(file.name.split('.').pop()?.toLowerCase() || '')) {errors.push(`${file.name}：格式不支持，请将 PPT / DOC 转为 PPTX / DOCX。`); continue;}
    if (file.size === 0 || file.size > 50 * 1024 * 1024) {errors.push(`${file.name}：文件不能为空且不能超过 50 MB。`); continue;}
    if (files.some(item => item.name === file.name && item.size === file.size && item.lastModified === file.lastModified)) continue;
    if (files.length >= 10) {errors.push('每批最多选择 10 份文件。'); break;}
    files.push(file);
  }
  return {files, errors};
}
export function Upload({files, onChange, disabled}: {files: File[]; onChange: (files: File[]) => void; disabled?: boolean}) {
  const input = useRef<HTMLInputElement>(null); const depth = useRef(0); const id = useId();
  const [dragging, setDragging] = useState(false); const [errors, setErrors] = useState<string[]>([]);
  function add(incoming: File[]) {if (disabled) return; const checked = validateFiles(incoming, files); onChange(checked.files);setErrors(checked.errors);}
  return <>
    <section aria-label="上传学习资料" aria-disabled={disabled} className={`upload-box ${dragging ? 'dragging' : ''}`}
      onDragEnter={e => {e.preventDefault(); if (!disabled) {depth.current++;setDragging(true);}}}
      onDragOver={e => e.preventDefault()} onDragLeave={e => {e.preventDefault();depth.current = Math.max(0,depth.current-1);if (!depth.current) setDragging(false);}}
      onDrop={e => {e.preventDefault();depth.current=0;setDragging(false);add(Array.from(e.dataTransfer.files));}}>
      <div className="upload-art" aria-hidden="true"><div className="paper back-paper">Aa<div/><div/></div><div className="paper front-paper"><Icon name="file" size={24}/><div/><div/><div/></div><span className="art-spark"><Icon name="spark"/></span></div>
      <h2>{dragging ? '松开鼠标，添加资料' : '上传你的学习资料'}</h2><p>拖拽文件到这里，或点击下方按钮选择</p>
      <Button onClick={() => input.current?.click()} disabled={disabled}><Icon name="plus" size={18}/>选择文件</Button>
      <input ref={input} className="visually-hidden" tabIndex={-1} aria-label="选择学习资料" aria-describedby={id} type="file" multiple disabled={disabled} accept={SUPPORTED_EXTENSIONS.map(ext => '.'+ext).join(',')} onChange={e => {add(Array.from(e.target.files || []));e.target.value='';}}/>
      <div className="file-types" id={id}>PDF · PPTX · DOCX · 图片 · TXT / MD<span>每份 ≤ 50 MB · 每批 ≤ 10 份</span></div>
    </section>
    {errors.length > 0 && <div role="alert" className="error">{errors.map((error,i) => <p key={i}>{error}</p>)}</div>}
    {files.length > 0 && <div className="selected-files" aria-label="待上传文件">{files.map((file,index) => <div key={`${file.name}-${index}`}><Icon name="file"/><span title={file.name}>{file.name}</span><small>{Math.max(.1,file.size/1024/1024).toFixed(1)} MB</small><button type="button" className="icon-button" disabled={disabled} aria-label={`移除 ${file.name}`} onClick={() => onChange(files.filter((_,i) => i !== index))}><Icon name="close" size={16}/></button></div>)}</div>}
  </>;
}
