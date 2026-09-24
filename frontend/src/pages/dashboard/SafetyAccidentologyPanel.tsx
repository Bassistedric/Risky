import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import './SafetyAccidentologyPanel.css'

const API='http://127.0.0.1:8000'
type Row={code:string;label:string;count:number;percent:number}
type Accidentology={coverage:{events:number;normal_events:number;advanced_events:number;heepo:number;classification:number;just_culture:number;actions:number};heepo:{families:Row[];factors:Row[]};classification:{deviation:Row[];material_agent:Row[];injury_nature:Row[];injury_location:Row[]};just_culture:{conclusions:Row[]};actions:{total:number;done:number;completion_percent:number|null;local_count:number;global_9001_count:number;overdue:number;statuses:{status:string;count:number}[]}}

const PIE_COLORS=['#3f7f93','#e59b45','#6d9d63','#9b72b0','#cf6c68','#6d86b3']

function Bars({rows,limit}:{rows:Row[];limit?:number}){
 const shown=limit?rows.slice(0,limit):rows,max=Math.max(1,...shown.map(r=>r.count))
 return <div className="acc-bars">{shown.map((r,i)=><div className="acc-bar" key={r.code}>
  <div className="acc-bar__head"><span title={r.label}><b>{r.code}</b> {r.label}</span><strong>{r.count}</strong></div>
  <div className="acc-bar__track"><i style={{width:`${r.count/max*100}%`,background:PIE_COLORS[i%PIE_COLORS.length]}}/></div>
 </div>)}</div>
}

function topWithOther(rows:Row[],limit=5,otherLabel='Autres'):Row[]{
 if(rows.length<=limit)return rows
 const top=rows.slice(0,limit),rest=rows.slice(limit)
 const count=rest.reduce((s,r)=>s+r.count,0),total=rows.reduce((s,r)=>s+r.count,0)
 return [...top,{code:'OTHER',label:otherLabel,count,percent:total?count*100/total:0}]
}

function Pie({rows}:{rows:Row[]}){
 const total=rows.reduce((s,r)=>s+r.count,0)
 let cursor=0
 const stops=rows.map((r,i)=>{const start=cursor;cursor+=total?r.count/total*100:0;return `${PIE_COLORS[i%PIE_COLORS.length]} ${start}% ${cursor}%`})
 return <div className="acc-pie-wrap">
  <div className="acc-pie" style={{background:total?`conic-gradient(${stops.join(',')})`:'#edf0f2'}}><span>{total}</span></div>
  <div className="acc-pie-legend">{rows.map((r,i)=><div key={r.code}><i style={{background:PIE_COLORS[i%PIE_COLORS.length]}}/><span title={r.label}>{r.label}</span><b>{r.count}</b></div>)}</div>
 </div>
}

export default function SafetyAccidentologyPanel({organizationId,year,month,tradeCode,temporaryWorkers=0,subcontractors=0}:{organizationId:number;year:number;month:number;tradeCode:string;temporaryWorkers?:number;subcontractors?:number}){
 const {t}=useTranslation()
 const other=t('safetyStatistics.accidentology.other')
 const [data,setData]=useState<Accidentology|null>(null),[error,setError]=useState('')
 useEffect(()=>{const q=new URLSearchParams({organization_id:String(organizationId),year:String(year),month_to:String(month)});if(tradeCode)q.set('trade_code',tradeCode);setError('');fetch(`${API}/safety-statistics/accidentology?${q}`).then(r=>{if(!r.ok)throw Error(t('safetyStatistics.accidentology.loadError'));return r.json()}).then(setData).catch(e=>{setData(null);setError(e.message)})},[organizationId,year,month,tradeCode,t])
 if(error)return <section className="safety-dashboard__panel"><div className="acc-error">{error}</div></section>
 if(!data)return null
 const a=data.actions, progress=a.completion_percent??0
 const statusLabel=(s:string)=>t(`safetyStatistics.accidentology.actionStatus.${s}`,{defaultValue:s})
 return <section className="accidentology">
  <div className="accidentology__title"><h3>{t('safetyStatistics.accidentology.title')}</h3><p>{t('safetyStatistics.accidentology.subtitle')}</p></div>
  <div className="acc-coverage"><article><span>{t('safetyStatistics.accidentology.coverage.classification')}</span><strong>{data.coverage.classification}/{data.coverage.events}</strong><small>{data.coverage.events?Math.round(data.coverage.classification*100/data.coverage.events):0}%</small></article><article><span>{t('safetyStatistics.accidentology.coverage.heepo')}</span><strong>{data.coverage.heepo}/{data.coverage.events}</strong><small>{data.coverage.events?Math.round(data.coverage.heepo*100/data.coverage.events):0}%</small></article><article><span>{t('safetyStatistics.accidentology.coverage.just_culture')}</span><strong>{data.coverage.just_culture}/{data.coverage.normal_events}</strong><small>{data.coverage.normal_events?Math.round(data.coverage.just_culture*100/data.coverage.normal_events):0}%</small></article><article><span>{t('safetyStatistics.accidentology.coverage.actions')}</span><strong>{a.total}</strong><small>{t('safetyStatistics.accidentology.encoded')}</small></article></div>

  <section className="acc-group acc-group--fedris"><h3>{t('safetyStatistics.accidentology.classification')}</h3><div className="acc-grid acc-grid--four">
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.deviation')}</h4><Pie rows={topWithOther(data.classification.deviation,5,other)}/></article>
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.material_agent')}</h4><Pie rows={topWithOther(data.classification.material_agent,5,other)}/></article>
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.injury_nature')}</h4><Pie rows={topWithOther(data.classification.injury_nature,5,other)}/></article>
   <article className="acc-card"><h4>{t('safetyStatistics.accidentology.injury_location')}</h4><Pie rows={topWithOther(data.classification.injury_location,5,other)}/></article>
  </div></section>

  <section className="acc-group acc-group--heepo"><h3>HEEPO</h3><div className="acc-grid"><article className="acc-card"><h4>{t('safetyStatistics.accidentology.heepoFamilies')}</h4><Pie rows={data.heepo.families}/></article><article className="acc-card"><h4>{t('safetyStatistics.accidentology.heepoFactors')}</h4><Bars rows={['H','E','En','P','O'].flatMap(prefix=>data.heepo.factors.filter(r=>r.code.startsWith(prefix)).slice(0,1))}/></article></div></section>

  <section className="acc-group acc-group--culture"><h3>{t('safetyStatistics.accidentology.justCulture')}</h3><article className="acc-card"><Pie rows={data.just_culture.conclusions}/></article></section>

  <section className="acc-group acc-group--actions"><h3>{t('safetyStatistics.accidentology.actions')}</h3><article className="acc-card acc-actions"><div className="acc-actions__head"><div><span>{a.local_count} {t('safetyStatistics.accidentology.localActions')} · {a.global_9001_count} {t('safetyStatistics.accidentology.global9001')}</span></div><strong>{Math.round(progress)}%</strong></div><div className="acc-actions__progress"><i style={{width:`${Math.min(100,progress)}%`}}/></div><small>{t('safetyStatistics.accidentology.localProgress')}</small><div className="acc-actions__statuses">{a.statuses.map(s=><span key={s.status}><b>{s.count}</b> {statusLabel(s.status)}</span>)}</div>{a.overdue>0&&<div className="acc-actions__overdue">{a.overdue} {t('safetyStatistics.accidentology.overdue')}</div>}</article></section>
  <section className="acc-external"><span>{t('safetyStatistics.accidentology.externalWorkers')}</span><div><b>{temporaryWorkers}</b> {t('safetyStatistics.accidentology.temporaryWorkers')}<i/> <b>{subcontractors}</b> {t('safetyStatistics.accidentology.subcontractors')}</div></section>
 </section>
}
