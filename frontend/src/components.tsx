import type {ReactNode} from 'react'
import {ArrowUpRight,Info} from 'lucide-react'
import type {Point} from './types'

export function Card({children,className=''}:{children:ReactNode;className?:string}){return <section className={`card ${className}`}>{children}</section>}
export function Tag({children,tone='neutral'}:{children:ReactNode;tone?:'neutral'|'green'|'amber'|'blue'}){return <span className={`tag ${tone}`}>{children}</span>}
export function Metric({label,value,detail}:{label:string;value:string;detail:string}){return <div className="metric"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>}
export function Sparkline({points,color='#c6f36b'}:{points:Point[];color?:string}){
 if(points.length<2)return <div className="empty-chart">Collecting observations</div>
 const values=points.map(p=>p.value),min=Math.min(...values),max=Math.max(...values),range=max-min||1;
 const path=values.map((v,i)=>`${i?'L':'M'} ${(i/(values.length-1))*100} ${42-((v-min)/range)*34}`).join(' ')
 return <svg className="spark" viewBox="0 0 100 48" preserveAspectRatio="none"><path d="M 0 46 L 100 46" className="gridline"/><path d={path} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke"/></svg>
}
export function SectionTitle({eyebrow,title,action}:{eyebrow?:string;title:string;action?:string}){return <div className="section-title"><div>{eyebrow&&<span>{eyebrow}</span>}<h2>{title}</h2></div>{action&&<button className="text-button">{action}<ArrowUpRight size={15}/></button>}</div>}
export function ScopeNote({children}:{children:ReactNode}){return <div className="scope"><Info size={16}/><span>{children}</span></div>}

