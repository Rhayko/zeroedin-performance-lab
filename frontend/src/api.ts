import type {Analytics,Athlete,DailyState,PerformanceTest,Session} from './types'
const BASE=import.meta.env.VITE_API_URL||(import.meta.env.DEV?'http://localhost:8000':'')
async function request<T>(path:string,init?:RequestInit):Promise<T>{const res=await fetch(`${BASE}${path}`,{headers:{'Content-Type':'application/json'},...init});if(!res.ok)throw new Error((await res.json()).detail||'Request failed');return res.json()}
async function remove(path:string):Promise<void>{const res=await fetch(`${BASE}${path}`,{method:'DELETE'});if(!res.ok)throw new Error((await res.json()).detail||'Delete failed')}
export const api={
  athletes:()=>request<Athlete[]>('/api/athletes'),
  seed:()=>request<Athlete>('/api/demo/seed',{method:'POST'}),
  athlete:(id:number)=>request<Athlete>(`/api/athletes/${id}`),
  updateAthlete:(id:number,body:unknown)=>request<Athlete>(`/api/athletes/${id}`,{method:'PATCH',body:JSON.stringify(body)}),
  analytics:(id:number)=>request<Analytics>(`/api/athletes/${id}/analytics`),
  dailyStates:(id:number)=>request<DailyState[]>(`/api/athletes/${id}/daily-states`),
  sessions:(id:number)=>request<Session[]>(`/api/athletes/${id}/sessions`),
  tests:(id:number)=>request<PerformanceTest[]>(`/api/athletes/${id}/performance-tests`),
  createAthlete:(body:unknown)=>request<Athlete>('/api/athletes',{method:'POST',body:JSON.stringify(body)}),
  checkIn:(id:number,body:unknown)=>request(`/api/athletes/${id}/daily-states`,{method:'POST',body:JSON.stringify(body)}),
  session:(id:number,body:unknown)=>request(`/api/athletes/${id}/sessions`,{method:'POST',body:JSON.stringify(body)}),
  performanceTest:(id:number,body:unknown)=>request(`/api/athletes/${id}/performance-tests`,{method:'POST',body:JSON.stringify(body)}),
  deleteDailyState:(id:number,stateId:number)=>remove(`/api/athletes/${id}/daily-states/${stateId}`),
  deleteSession:(id:number,sessionId:number)=>remove(`/api/athletes/${id}/sessions/${sessionId}`),
  deleteTest:(id:number,testId:number)=>remove(`/api/athletes/${id}/performance-tests/${testId}`),
  importBackup:(body:unknown)=>request<Athlete>('/api/import',{method:'POST',body:JSON.stringify(body)}),
  exportUrl:(id:number,format:'json'|'csv')=>`${BASE}/api/athletes/${id}/export.${format}`
}
