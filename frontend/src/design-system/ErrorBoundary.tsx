import {Component,type ErrorInfo,type ReactNode} from 'react';
import {Icon} from './Icon';

export class ErrorBoundary extends Component<{children:ReactNode},{failed:boolean}> {
  state={failed:false};
  static getDerivedStateFromError(){return {failed:true};}
  componentDidCatch(_error:Error,_info:ErrorInfo){/* The product fallback intentionally hides technical details. */}
  render(){
    if(this.state.failed)return <main className="fatal-state" role="alert"><span><Icon name="book" size={34}/></span><h1>页面暂时没有加载完成</h1><p>你的项目和学习资料仍然保留。重新加载后可以继续。</p><button className="button primary" type="button" onClick={()=>window.location.reload()}>重新加载 RecallForge</button></main>;
    return this.props.children;
  }
}
