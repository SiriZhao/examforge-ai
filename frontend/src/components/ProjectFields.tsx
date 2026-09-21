import type {ProjectForm} from '../api/workspace';
export function ProjectFields({value,onChange,disabled}: {value:ProjectForm;onChange:(value:ProjectForm)=>void;disabled?:boolean}) {
  function update<K extends keyof ProjectForm>(key: K, next: ProjectForm[K]) {onChange({...value,[key]:next});}
  return <fieldset disabled={disabled} className="project-fields"><legend>复习设置</legend><div className="form-grid">
    <label>课程名称<input maxLength={160} value={value.course_name} placeholder="例如：概率论（留空使用文件名）" onChange={e=>update('course_name',e.target.value)}/></label>
    <label>考试日期<input type="date" value={value.exam_date} onChange={e=>update('exam_date',e.target.value)}/></label>
    <label>考试形式<select value={value.exam_type} onChange={e=>update('exam_type',e.target.value as ProjectForm['exam_type'])}><option value="unknown">暂不确定</option><option value="closed_book">闭卷笔试</option><option value="open_book">开卷笔试</option><option value="programming">编程考试</option><option value="lab_exam">实验考试</option><option value="essay_based">简答论述</option><option value="computer_based">上机考试</option><option value="oral_presentation">口头展示</option><option value="coursework_report">课程报告</option></select></label>
    <label>每日复习时间（分钟）<input type="number" min={15} max={960} required value={value.daily_minutes} onChange={e=>update('daily_minutes',Number(e.target.value))}/></label>
    <label>当前掌握程度<select value={value.mastery_level} onChange={e=>update('mastery_level',e.target.value)}><option value="none">几乎没学</option><option value="weak">基础薄弱</option><option value="forgotten">学过但忘得较多</option><option value="solid">基本掌握</option><option value="sprint">主要需要冲刺</option></select></label>
    <label>目标成绩<input value={value.target_score} maxLength={40} placeholder="例如：85+" onChange={e=>update('target_score',e.target.value)}/></label>
  </div><label>希望重点提升的方面<textarea value={value.focus} onChange={e=>update('focus',e.target.value)} placeholder="例如：计算题、论述题、背诵效率"/></label></fieldset>;
}
