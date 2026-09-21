import type {GenerateReviewResponse,GenerateReviewJob} from '../api/client';
import type {Project,Diagnosis} from '../api/workspace';
export const project:Project={id:'p1',course_name:'高等数学',exam_date:'',exam_type:'unknown',daily_minutes:90,mastery_level:'forgotten',created_at:'2026-09-09T02:00:00+00:00',files:[]};
export const material={id:'f1',original_filename:'高等数学.pdf',saved_filename:'saved.pdf',role:'slides' as const,pages:12};
export const diagnosis:Diagnosis={material_completeness:40,files_processed:1,roles:['slides'],missing:['往年试卷'],risks:[],recommended_strategy:['依据课程资料生成']};
export const result:GenerateReviewResponse={
  review_report:{title:'高等数学复习报告',summary:'理解积分',chapters:[],past_exam_analysis:{detected_files:[],high_frequency_topics:[],summary:'课程材料分析'},review_order:[{chapter:'积分',importance:90,reason:'核心考点'}],sprint_plans:[{days:1,title:'一天冲刺',schedule:['复习积分']}],mock_exam:{title:'模拟卷',questions:[{question_type:'计算题',question:'计算积分',answer:'答案为 1',chapter:'积分',concept:'定积分',explanation:'使用基本定理'}]},anki_cards:[{front:'什么是定积分？',back:'连续累积量',tags:'数学'},{front:'基本定理？',back:'原函数的差',tags:'数学'}],high_frequency_points:['积分'],sprint_checklist:[],low_priority:[],insufficient_materials:[],generated_at:'2026-09-09',study_units:[{name:'定积分',reason:'核心',priority:90,must_know:['有向面积'],key_points:['基本定理'],formulas_or_methods:[],common_exam_angles:[],pitfalls:[],how_to_review:'练习'}]},
  markdown:'# 高等数学复习报告\n\n真实接口返回的总结',download_links:{md:'/download/report.md',pdf:'/download/report.pdf'},download_path:'/download/report.md',export_format:'md',anki_csv_download_path:'/download/cards.csv',llm_status:'disabled',
};
export const completedJob:GenerateReviewJob={job_id:'job1',status:'completed',progress:100,message:'Completed',result,error:null,created_at:'2026-09-09',updated_at:'2026-09-09'};
