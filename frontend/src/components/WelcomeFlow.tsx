import {useState} from 'react';
import {Button} from '../design-system/Button';
import {Icon,type IconName} from '../design-system/Icon';
import {Modal} from '../design-system/Modal';

const STEPS: {title:string;description:string;icon:IconName}[]=[
  {title:'上传文件',description:'选择课程 PDF、PPTX、Word、图片或笔记。文件会保存在你的学习空间。',icon:'upload'},
  {title:'AI 理解内容',description:'RecallForge 自动识别文字、章节、重点和知识之间的联系。',icon:'spark'},
  {title:'生成复习资料',description:'获得知识总结、思维导图、问答卡片、练习题和模拟考试。',icon:'book'},
];

export function WelcomeFlow({open,onComplete}: {open:boolean;onComplete:()=>void}) {
  const [step,setStep]=useState(0);const current=STEPS[step];
  return <Modal open={open} title="欢迎使用 RecallForge" onClose={onComplete}>
    <div className="welcome-flow">
      <p className="welcome-intro">不用学习复杂操作，三步就能把课程文件变成可以直接复习的内容。</p>
      <div className="welcome-progress" aria-label={`新手引导第 ${step+1} 步，共 3 步`}><span>{step+1} / 3</span><div>{STEPS.map((item,index)=><i key={item.title} className={index<=step?'active':''}/>)}</div></div>
      <section className="welcome-step"><span className="welcome-icon"><Icon name={current.icon} size={32}/></span><small>第 {step+1} 步</small><h3>{current.title}</h3><p>{current.description}</p></section>
      <div className="welcome-actions"><Button variant="text" onClick={onComplete}>稍后再说</Button><div>{step>0&&<Button variant="secondary" onClick={()=>setStep(value=>value-1)}>上一步</Button>}<Button onClick={()=>step===STEPS.length-1?onComplete():setStep(value=>value+1)}>{step===STEPS.length-1?'开始使用':'下一步'}<Icon name="arrow" size={16}/></Button></div></div>
    </div>
  </Modal>;
}
