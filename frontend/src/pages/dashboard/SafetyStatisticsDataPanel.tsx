import { ChangeEvent, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import './SafetyStatisticsDataPanel.css'

const API='http://127.0.0.1:8000'
type Props={organizationId:number;year:number;onChanged:()=>void}
type Preview={filename:string;year:number;month_to:number;record_count:number;entities:Array<{organization_code:string;source_label:string;total_hours_ytd:number}>}
type Disability={id:number;disability_percent:number;conventional_days:number;source?:string|null}

export default function SafetyStatisticsDataPanel({organizationId,year,onChanged}:Props){
 const {t}=useTranslation()
 const [open,setOpen]=useState(false),[file,setFile]=useState<File|null>(null),[preview,setPreview]=useState<Preview|null>(null)
 const [tf,setTf]=useState(''),[tg,setTg]=useState(''),[disability,setDisability]=useState(''),[rows,setRows]=useState<Disability[]>([])
 const [busy,setBusy]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('')
 const token=()=>sessionStorage.getItem('risky_session_token')??''
 const auth={'X-Session-Token':token()}

 const load=async()=>{
  const [a,b]=await Promise.all([
   fetch(`${API}/safety-statistics/targets?organization_id=${organizationId}&year=${year}`),
   fetch(`${API}/safety-statistics/permanent-disabilities?organization_id=${organizationId}&year=${year}`)
  ])
  if(a.ok){const x=await a.json();setTf(x.tf_target??'');setTg(x.tg_target??'')}
  if(b.ok)setRows(await b.json())
 }
 useEffect(()=>{if(open)void load()},[open,organizationId,year])

 const upload=async(mode:'preview'|'apply')=>{
  if(!file)return
  setBusy(true);setError('');setMessage('')
  try{
   const body=new FormData();body.append('file',file)
   const r=await fetch(`${API}/safety-statistics/work-hours/import/${mode}`,{method:'POST',headers:auth,body})
   const x=await r.json();if(!r.ok)throw Error(x.detail??t('safetyStatistics.data.error'))
   if(mode==='preview')setPreview(x)
   else{setPreview(null);setMessage(t('safetyStatistics.data.importDone',{count:x.records_written}));onChanged()}
  }catch(e){setError(e instanceof Error?e.message:t('safetyStatistics.data.error'))}finally{setBusy(false)}
 }
 const saveTargets=async()=>{
  setBusy(true);setError('');setMessage('')
  try{
   const r=await fetch(`${API}/safety-statistics/targets`,{method:'PUT',headers:{...auth,'Content-Type':'application/json'},body:JSON.stringify({organization_id:organizationId,year,tf_target:tf===''?null:Number(tf.replace(',','.')),tg_target:tg===''?null:Number(tg.replace(',','.')),source:'CFE'})})
   const x=await r.json();if(!r.ok)throw Error(x.detail??t('safetyStatistics.data.error'))
   setMessage(t('safetyStatistics.data.targetsSaved'));onChanged()
  }catch(e){setError(e instanceof Error?e.message:t('safetyStatistics.data.error'))}finally{setBusy(false)}
 }
 const addDisability=async()=>{
  if(!disability)return
  setBusy(true);setError('');setMessage('')
  try{
   const r=await fetch(`${API}/safety-statistics/permanent-disabilities`,{method:'POST',headers:{...auth,'Content-Type':'application/json'},body:JSON.stringify({organization_id:organizationId,year,disability_percent:Number(disability.replace(',','.')),source:'AXA'})})
   const x=await r.json();if(!r.ok)throw Error(x.detail??t('safetyStatistics.data.error'))
   setDisability('');await load();setMessage(t('safetyStatistics.data.disabilitySaved'));onChanged()
  }catch(e){setError(e instanceof Error?e.message:t('safetyStatistics.data.error'))}finally{setBusy(false)}
 }
 const remove=async(id:number)=>{
  setBusy(true);setError('');setMessage('')
  try{const r=await fetch(`${API}/safety-statistics/permanent-disabilities/${id}`,{method:'DELETE',headers:auth});if(!r.ok){const x=await r.json();throw Error(x.detail??t('safetyStatistics.data.error'))}await load();onChanged()}
  catch(e){setError(e instanceof Error?e.message:t('safetyStatistics.data.error'))}finally{setBusy(false)}
 }
 const choose=(e:ChangeEvent<HTMLInputElement>)=>{setFile(e.target.files?.[0]??null);setPreview(null);setMessage('');setError('')}

 return <section className="safety-data">
  <button type="button" className="safety-data__toggle" onClick={()=>setOpen(v=>!v)}><span>⚙ {t('safetyStatistics.data.title')}</span><span>{open?'⌃':'⌄'}</span></button>
  {open&&<div className="safety-data__body">
   <div className="safety-data__grid">
    <article><h3>{t('safetyStatistics.data.rhTitle')}</h3><p>{t('safetyStatistics.data.rhHelp')}</p><input type="file" accept=".xlsx" onChange={choose}/><div className="safety-data__actions"><button disabled={!file||busy} onClick={()=>void upload('preview')}>{t('safetyStatistics.data.preview')}</button>{preview&&<button className="primary" disabled={busy} onClick={()=>void upload('apply')}>{t('safetyStatistics.data.apply')}</button>}</div>
     {preview&&<div className="safety-data__preview"><strong>{preview.filename}</strong><span>{preview.year} · {t('safetyStatistics.data.throughMonth',{month:preview.month_to})} · {preview.record_count} {t('safetyStatistics.data.records')}</span>{preview.entities.map(e=><span key={e.organization_code}>{e.source_label}: {Math.round(e.total_hours_ytd).toLocaleString()}</span>)}</div>}
    </article>
    <article><h3>{t('safetyStatistics.data.targetsTitle')}</h3><p>{t('safetyStatistics.data.targetsHelp')}</p><div className="safety-data__fields"><label>TF<input value={tf} onChange={e=>setTf(e.target.value)} inputMode="decimal"/></label><label>TG<input value={tg} onChange={e=>setTg(e.target.value)} inputMode="decimal"/></label></div><button className="primary" disabled={busy} onClick={()=>void saveTargets()}>{t('safetyStatistics.data.save')}</button></article>
    <article><h3>{t('safetyStatistics.data.disabilityTitle')}</h3><p>{t('safetyStatistics.data.disabilityHelp')}</p><div className="safety-data__inline"><input value={disability} onChange={e=>setDisability(e.target.value)} placeholder="% AXA" inputMode="decimal"/><button className="primary" disabled={!disability||busy} onClick={()=>void addDisability()}>{t('safetyStatistics.data.add')}</button></div><div className="safety-data__rows">{rows.length===0?<span>{t('safetyStatistics.data.none')}</span>:rows.map(r=><div key={r.id}><span>{r.disability_percent}% · JGC {r.conventional_days}</span><button onClick={()=>void remove(r.id)} disabled={busy}>×</button></div>)}</div></article>
   </div>
   {message&&<div className="safety-data__message">{message}</div>}{error&&<div className="safety-data__message error">{error}</div>}
  </div>}
 </section>
}
