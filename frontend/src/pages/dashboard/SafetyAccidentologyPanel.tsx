import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import './SafetyAccidentologyPanel.css'

const API='http://127.0.0.1:8000'

type Row={code:string;label:string;count:number;percent:number}
type Accidentology={
 coverage:{events:number;heepo:number;classification:number;just_culture:number;actions:number}
 heepo:{families:Row[];factors:Row[]}
 classification:{deviation:Row[];material_agent:Row[];injury_nature:Row[];injury_location:Row[]}
 just_culture:{conclusions:Row[]}
 actions:{total:number;done:number;completion_percent:number;overdue:number;statuses:{status:string;count:number}[]}
}

function Bars({rows,limit}:{rows:Row[];limit?:number}){
 const shown=limit?rows.slice(0,limit):rows
 const max=Math.max(1,...shown.map(r=>r.count))
 return <div className="acc-bars">{shown.map(r=><div className="acc-bar" key={r.code}>
  <div className="acc-bar__head"><span title={r.label}><b>{r.code}</b> {r.label}</span><strong>{r.count}</strong></div>
  <div className="acc-bar__track"><i style={{width:`${r.count/max*100}%`}}/></div>
 </div>)}</div>
}

export default function SafetyAccidentologyPanel({organizationId,year,month,tradeCode}:{organizationId:number;year:number;month:number;tradeCode:string}){
 const {t}=useTranslation()
 const [data,setData]=useState<Accidentology|null>(null),[error,setError]=useState('')

 useEffect(()=>{
  const q=new URLSearchParams({organization_id:String(organizationId),year:String(year),month_to:String(month)})
  if(tradeCode)q.set('trade_code',tradeCode)
  setError('')
  fetch(`${API}/safety-statistics/accidentology?${q}`).then(r=>{if(!r.ok)throw Error(t('safetyStatistics.accidentology.loadError'));return r.json()}).then(setData).catch(e=>{setData(null);setError(e.message)})
 },[organizationId,year,month,tradeCode,t])

 if(error)return <section className="safety-dashboard__panel"><div className="acc-error">{error}</div></section>
 if(!data)return null
 const a=data.actions
 const statusLabel=(s:string)=>t(`safetyStatistics.accidentology.actionStatus.${s}`,{defaultValue:s})

 return <section className="accidentology">
  <div className="accidentology__title"><div><h3>{t('safetyStatistics.accidentology.title')}</h3><p>{t('safetyStatistics.accidentology.subtitle')}</p></div></div>

  <div className="acc-coverage">
   {(['heepo','classification','just_culture'] as const).map(k=><article key={k}><span>{t(`safetyStatistics.accidentology.coverage.${k}`)}</span><strong>{data.coverage[k]}/{data.coverage.events}</strong><small>{data.coverage.events?Math.round(data.coverage[k]*100/data.coverage.events):0}%</small></article>)}
   <article><span>{t('safetyStatistics.accidentology.coverage.actions')}</span><strong>{a.total}</strong><small>{t('safetyStatistics.accidentology.encoded')}</small></article>
  </div>

  <div className="acc-grid">
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.heepoFamilies')}</h4><Bars rows={data.heepo.families}/></article>
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.heepoFactors')}</h4><Bars rows={data.heepo.factors} limit={8}/></article>
  </div>

  <h3 className="acc-section-title">{t('safetyStatistics.accidentology.classification')}</h3>
  <div className="acc-grid acc-grid--four">
   {(['deviation','material_agent','injury_nature','injury_location'] as const).map(k=><article className="acc-card" key={k}><h4>{t(`safetyStatistics.accidentology.${k}`)}</h4><Bars rows={data.classification[k]} limit={6}/></article>)}
  </div>

  <div className="acc-grid">
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.justCulture')}</h4><Bars rows={data.just_culture.conclusions}/></article>
   <article className="acc-card acc-actions"><div className="acc-actions__head"><div><h4>{t('safetyStatistics.accidentology.actions')}</h4><span>{a.total} {t('safetyStatistics.accidentology.actionsEncoded')}</span></div><strong>{Math.round(a.completion_percent)}%</strong></div>
    <div className="acc-actions__progress"><i style={{width:`${Math.min(100,a.completion_percent)}%`}}/></div>
    <div className="acc-actions__statuses">{a.statuses.map(s=><span key={s.status}><b>{s.count}</b> {statusLabel(s.status)}</span>)}</div>
    {a.overdue>0&&<div className="acc-actions__overdue">{a.overdue} {t('safetyStatistics.accidentology.overdue')}</div>}
   </article>
  </div>
 </section>
}
