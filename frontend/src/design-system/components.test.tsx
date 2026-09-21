import {cleanup,fireEvent,render,screen} from '@testing-library/react';
import {afterEach,describe,expect,it} from 'vitest';
import {validateFiles,Upload} from './Upload';
import {ResultTabs} from '../components/ResultTabs';
import {userFacingError} from '../api/workspace';
import {ErrorBoundary} from './ErrorBoundary';
afterEach(cleanup);
describe('Upload validation',()=>{
  it('rejects unsupported, empty and oversized files, and caps batches at 10',()=>{
    const oversized=new File(['a'],'huge.pdf');Object.defineProperty(oversized,'size',{value:51*1024*1024});
    const checked=validateFiles([new File(['a'],'legacy.ppt'),new File([],'empty.pdf'),oversized,...Array.from({length:11},(_,i)=>new File(['data'],i+'.pdf'))]);
    expect(checked.files).toHaveLength(10);expect(checked.errors).toHaveLength(4);
  });
  it('deduplicates selected files and supports dropping',()=>{
    const file=new File(['data'],'chapter.pdf');
    expect(validateFiles([file],[file]).files).toHaveLength(1);
    let selected:File[]=[];render(<Upload files={[]} onChange={files=>{selected=files;}}/>);
    fireEvent.drop(screen.getByRole('region',{name:'上传学习资料'}),{dataTransfer:{files:[file]}});
    expect(selected).toEqual([file]);
  });
  it('ignores drops while disabled',()=>{
    let called=false;render(<Upload files={[]} onChange={()=>{called=true;}} disabled/>);
    fireEvent.drop(screen.getByRole('region',{name:'上传学习资料'}),{dataTransfer:{files:[new File(['a'],'a.pdf')]}});
    expect(called).toBe(false);
  });
});
describe('Keyboard navigation',()=>{
  it('moves result tab focus with arrow keys',()=>{
    let selected=0;render(<ResultTabs value={0} onChange={next=>{selected=next;}}/>);
    fireEvent.keyDown(screen.getByRole('tab',{name:'知识总结'}),{key:'ArrowRight'});
    expect(selected).toBe(1);expect(screen.getByRole('tab',{name:'思维导图'})).toHaveFocus();
  });
});
describe('Student-facing errors',()=>{
  it('translates technical failures into actionable language',()=>{
    expect(userFacingError(new Error('ECONNREFUSED'),'workspace')).toEqual(expect.objectContaining({title:'暂时连接不上服务'}));
    expect(userFacingError(new Error('OCR engine failed'),'generation')).toEqual(expect.objectContaining({title:'图片文字没有识别完成'}));
    expect(userFacingError(new Error('model quota exceeded'),'generation')).toEqual(expect.objectContaining({title:'AI 模型暂时不可用'}));
    expect(userFacingError(new Error('something unexpected'),'general').message).not.toMatch(/未知错误/);
  });
  it('shows a recovery screen instead of a blank page after a render failure',()=>{
    const original=console.error;console.error=()=>undefined;
    function Broken(): never {throw new Error('render failed');}
    render(<ErrorBoundary><Broken/></ErrorBoundary>);
    expect(screen.getByRole('heading',{name:'页面暂时没有加载完成'})).toBeInTheDocument();
    expect(screen.getByRole('button',{name:'重新加载 RecallForge'})).toBeEnabled();
    console.error=original;
  });
});
