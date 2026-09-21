import {useState} from 'react';
import type {GeneratedExamQuestion} from '../api/client';
import {Button} from '../design-system/Button';
export function Questions({questions,mock}: {questions:GeneratedExamQuestion[];mock:boolean}) {
  const [revealed,setRevealed]=useState<Record<number,boolean>>({});
  if(!questions.length)return <div className="empty-projects"><h2>暂无生成题目</h2><p>补充课程资料或往年试卷后重新生成。</p></div>;
  return <><div className="document-label">{mock?'MOCK EXAM':'PRACTICE'}<span>{questions.length} 道题 · 自评练习</span></div><h2>{mock?'给知识一次实战机会。':'用练习，检验理解。'}</h2><p className="muted">题目来自本次生成。完成作答后可查看参考答案与解析。</p>{questions.map((question,i)=><section className="exam-question" key={i}><h3>{String(i+1).padStart(2,'0')} / {question.type||question.question_type}</h3><p className="question-stem">{question.question}</p>{!!question.options?.length&&<ul>{question.options.map((option,j)=><li key={j}>{option}</li>)}</ul>}<textarea aria-label={`第 ${i+1} 题答案`} placeholder="写下你的答案与思路…"/><Button variant="text" aria-expanded={!!revealed[i]} onClick={()=>setRevealed(old=>({...old,[i]:!old[i]}))}>{revealed[i]?'收起解析':'查看参考答案'}</Button>{revealed[i]&&<div className="concept-callout"><div><strong>参考答案</strong><p>{question.answer||'本题未返回答案'}</p><strong>解析</strong><p>{question.explanation||'本题未返回详细解析'}</p></div></div>}<p className="source-label">{question.source_basis||question.source_hint||'基于上传材料生成'}{question.concept&&` · ${question.concept}`}</p></section>)}</>;
}
