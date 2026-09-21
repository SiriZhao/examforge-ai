import type {ReviewReport} from '../api/client';
export function KnowledgeMap({report}: {report:ReviewReport}) {
  const branches=report.study_units?.length?report.study_units.map(unit=>({name:unit.name,points:[...unit.must_know,...unit.key_points],description:unit.how_to_review})):report.chapters.map(chapter=>({name:chapter.chapter,points:chapter.keywords,description:chapter.review_advice}));
  return <><div className="document-label">KNOWLEDGE MAP</div><h2>让知识，连接起来。</h2><p className="muted">根据本次报告的章节与复习单元呈现知识结构。</p>{branches.length?<div className="mindmap"><div className="map-root">{report.title}</div><div className="map-branches">{branches.map((branch,i)=><section key={i}><h3>{branch.name}</h3><ul>{branch.points.map((point,j)=><li key={j}>{point}</li>)}</ul><p>{branch.description}</p></section>)}</div></div>:<p className="muted">本次报告没有结构化章节，请查看知识总结。</p>}</>;
}
