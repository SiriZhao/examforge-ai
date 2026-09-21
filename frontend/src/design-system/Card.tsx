import type { HTMLAttributes } from 'react';
export function Card({className = '', ...props}: HTMLAttributes<HTMLElement>) { return <section {...props} className={`ui-card ${className}`}/>; }
