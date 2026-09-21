import {useState} from 'react';
import type {AnkiCard} from '../api/client';
import {Button} from '../design-system/Button';
import {Icon} from '../design-system/Icon';
export function Flashcards({cards}: {cards:AnkiCard[]}) {
  const [index,setIndex]=useState(0);const [flipped,setFlipped]=useState(false);
  if(!cards.length)return <div className="empty-projects"><h2>这份资料尚未生成卡片</h2><p>可以补充资料，选择知识卡片模式后重新生成。</p></div>;
  const card=cards[index];
  function move(next:number){setIndex(next);setFlipped(false);}
  return <><div className="document-label">ACTIVE RECALL<span>{index+1} / {cards.length}</span></div><h2>想一想，再看答案。</h2><button type="button" className={`flashcard ${flipped?'flipped':''}`} aria-label={flipped?'查看问题':'查看答案'} aria-pressed={flipped} onClick={()=>setFlipped(!flipped)}><span>{flipped?'ANSWER / 答案':'QUESTION / 问题'}</span><Icon name="cards" size={30}/><strong>{flipped?card.back:card.front}</strong><small>点击卡片{flipped?'返回问题':'查看答案'}</small></button>{card.source_hint&&<p className="source-label">来源：{card.source_hint}</p>}<div className="card-navigation"><Button variant="secondary" disabled={index===0} onClick={()=>move(index-1)}>上一张</Button><span>{index+1} / {cards.length}</span><Button variant="secondary" disabled={index===cards.length-1} onClick={()=>move(index+1)}>下一张</Button></div></>;
}
