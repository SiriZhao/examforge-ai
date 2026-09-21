import {MODES,type Mode} from '../api/workspace';
import {Icon} from '../design-system/Icon';
export function ModeSelector({value,onChange,disabled}: {value:Mode;onChange:(mode:Mode)=>void;disabled?:boolean}) {
  return <><div className="section-heading modes-heading"><h3>按照你的节奏学习</h3><span>选择一种模式，开始就好</span></div><div className="mode-grid">{MODES.map(mode=><button type="button" disabled={disabled} key={mode.id} className={`mode-card ${value===mode.id?'selected':''}`} aria-pressed={value===mode.id} onClick={()=>onChange(mode.id)}><span className="mode-icon"><Icon name={mode.icon}/></span>{value===mode.id && <span className="selected-check"><Icon name="check" size={12}/></span>}<strong>{mode.title}</strong><small>{mode.description}</small></button>)}</div><p className="mode-description"><Icon name="spark" size={14}/>{MODES.find(mode=>mode.id===value)?.detail}</p></>;
}
