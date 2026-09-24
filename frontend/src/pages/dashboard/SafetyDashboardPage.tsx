import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import './SafetyDashboardPage.css'

const API='http://127.0.0.1:8000'
type M={month:number;worked_hours:number;accidents_with_lost_time:number;accidents_without_lost_time:number;lost_days:number;incidents:number;near_misses:number;tf:number|null;tg:number|null;tf_ytd:number|null;tg_ytd:number|null}
type S={scope:{organization_name:string;trade_code:string|null};period:{year:number;month_to:number};totals:{worked_hours:number;accidents_with_lost_time:number;accidents_without_lost_time:number;lost_days:number;conventional_days:number;incidents:number;near_misses:number};indicators:{tf:number|null;tg:number|null;tgg:number|null};targets:{tf_target:number|null;tg_target:number|null};projection:{projected_hours:number|null;projected_tf:number|null;projected_tg:number|null};monthly:M[]}
type Trade={id:number;code:string;name:string}
type Metric='tf'|'tg'|'accidents'

export default function SafetyDashboardPage(){
 const {t,i18n}=useTranslation()
 const now=new Date(), currentYear=now.getFullYear()
 const [year,setYear]=useState(currentYear),[month,setMonth]=useState(now.getMonth()+1)
 const [trade,setTrade]=useState(''),[metric,setMetric]=useState<Metric>('tf')
 const [trades,setTrades]=useState<Trade[]>([]),[data,setData]=useState<S|null>(null)
 const [loading,setLoading]=useState(true),[error,setError]=useState('')
 const org=2 // VMA Sud; sera relié ensuite au sélecteur global RISKY.

 useEffect(()=>{fetch(`${API}/safety-statistics/trades`).then(r=>r.ok?r.json():[]).then(setTrades).catch(()=>{})},[])
 useEffect(()=>{setLoading(true);setError('')
  const q=new URLSearchParams({organization_id:String(org),year:String(year),month_to:String(month)})
  if(trade)q.set('trade_code',trade)
  fetch(`${API}/safety-statistics/summary?${q}`).then(r=>{if(!r.ok)throw Error(t('safetyStatistics.loadError'));return r.json()})
   .then(setData).catch(e=>{setData(null);setError(e.message)}).finally(()=>setLoading(false))
 },[year,month,trade,t])

 const locale=i18n.language==='fr'?'fr-BE':i18n.language==='nl'?'nl-BE':i18n.language==='pl'?'pl-PL':'en-GB'
 const n=(v:number|null|undefined,d=2)=>v==null?'—':new Intl.NumberFormat(locale,{minimumFractionDigits:d,maximumFractionDigits:d}).format(v)
 const ni=(v:number|null|undefined)=>v==null?'—':new Intl.NumberFormat(locale,{maximumFractionDigits:0}).format(v)
 const mn=(m:number)=>new Intl.DateTimeFormat(locale,{month:'short'}).format(new Date(2026,m-1,1))
 const points=useMemo(()=>data?.monthly.map(r=>({m:r.month,v:metric==='tf'?r.tf_ytd:metric==='tg'?r.tg_ytd:r.accidents_with_lost_time+r.accidents_without_lost_time}))??[],[data,metric])
 const max=Math.max(1,...points.flatMap(p=>p.v==null?[]:[p.v]))
 const xy=points.map((p,i)=>p.v==null?null:{...p,x:points.length<2?50:50+i/(points.length-1)*850,y:250-p.v/max*190})
 const line=xy.filter((p):p is NonNullable<typeof p>=>p!==null).map(p=>`${p.x},${p.y}`).join(' ')
 const target=metric==='tf'?data?.targets.tf_target:metric==='tg'?data?.targets.tg_target:null
 const ty=target!=null&&target<=max?250-target/max*190:null

 return <section className="safety-dashboard">
  <header className="safety-dashboard__header"><div><h2>{t('safetyStatistics.title')}</h2><p>{t('safetyStatistics.subtitle')}</p></div>
   <div className="safety-dashboard__filters">
    <label><span>{t('safetyStatistics.year')}</span><select value={year} onChange={e=>setYear(+e.target.value)}>{Array.from({length:5},(_,i)=>currentYear-i).map(y=><option key={y}>{y}</option>)}</select></label>
    <label><span>{t('safetyStatistics.period')}</span><select value={month} onChange={e=>setMonth(+e.target.value)}>{Array.from({length:12},(_,i)=>i+1).map(m=><option key={m} value={m}>{t('safetyStatistics.untilMonth',{month:mn(m)})}</option>)}</select></label>
    <label><span>{t('safetyStatistics.trade')}</span><select value={trade} onChange={e=>setTrade(e.target.value)}><option value="">{t('safetyStatistics.allTrades')}</option>{trades.map(x=><option key={x.id} value={x.code}>{x.name}</option>)}</select></label>
   </div>
  </header>
  {loading&&<div className="safety-dashboard__state">{t('safetyStatistics.loading')}</div>}
  {error&&<div className="safety-dashboard__state error">{error}</div>}
  {!loading&&!error&&data&&<>
   <div className="safety-dashboard__scope"><strong>{data.scope.organization_name}</strong><span>·</span><span>{data.scope.trade_code??t('safetyStatistics.allTrades')}</span><span>·</span><span>{data.period.year}</span></div>
   <div className="safety-dashboard__kpis">
    <article><span>TF</span><strong>{n(data.indicators.tf)}</strong><small>{t('safetyStatistics.cfeTarget')}: {n(data.targets.tf_target)}</small><em>{t('safetyStatistics.projection')}: {n(data.projection.projected_tf)}</em></article>
    <article><span>TG</span><strong>{n(data.indicators.tg)}</strong><small>{t('safetyStatistics.cfeTarget')}: {n(data.targets.tg_target)}</small><em>{t('safetyStatistics.projection')}: {n(data.projection.projected_tg)}</em></article>
    <article><span>TGG</span><strong>{n(data.indicators.tgg)}</strong><small>{t('safetyStatistics.conventionalDays')}: {ni(data.totals.conventional_days)}</small></article>
    <article><span>{t('safetyStatistics.workedHours')}</span><strong>{ni(data.totals.worked_hours)}</strong><small>YTD</small><em>{t('safetyStatistics.projectedHours')}: {ni(data.projection.projected_hours)}</em></article>
   </div>
   <div className="safety-dashboard__secondary">
    {([['lostTimeAccidents',data.totals.accidents_with_lost_time],['noLostTimeAccidents',data.totals.accidents_without_lost_time],['lostDays',data.totals.lost_days],['incidents',data.totals.incidents],['nearMisses',data.totals.near_misses]] as const).map(([k,v])=><article key={k}><span>{t(`safetyStatistics.${k}`)}</span><strong>{v}</strong></article>)}
   </div>
   <section className="safety-dashboard__panel">
    <div className="safety-dashboard__panel-head"><div><h3>{t('safetyStatistics.indicatorEvolution')}</h3><p>{t('safetyStatistics.ytdEvolution')}</p></div><div className="safety-dashboard__tabs">{(['tf','tg','accidents'] as Metric[]).map(k=><button type="button" key={k} className={metric===k?'active':''} onClick={()=>setMetric(k)}>{k==='tf'?'TF':k==='tg'?'TG':t('safetyStatistics.accidents')}</button>)}</div></div>
    <div className="safety-chart"><svg viewBox="0 0 950 300" role="img">{[60,107.5,155,202.5,250].map(y=><line key={y} x1="50" y1={y} x2="900" y2={y} className="grid"/>)}{ty!=null&&<line x1="50" y1={ty} x2="900" y2={ty} className="target"/>}{line&&<polyline points={line} className="line"/>}{xy.map((p,i)=>p&&<g key={p.m}><circle cx={p.x} cy={p.y} r="5"/><text x={p.x} y={p.y-12} textAnchor="middle">{n(p.v,metric==='accidents'?0:2)}</text><text x={p.x} y="280" textAnchor="middle">{mn(p.m)}</text></g>)}</svg></div>
   </section>
   <section className="safety-dashboard__panel"><h3>{t('safetyStatistics.monthlyDetail')}</h3><div className="safety-dashboard__table-wrap"><table><thead><tr><th>{t('safetyStatistics.month')}</th><th>{t('safetyStatistics.hours')}</th><th title={t('safetyStatistics.lostTimeAccidents')}>ATI</th><th title={t('safetyStatistics.noLostTimeAccidents')}>ATSI</th><th>{t('safetyStatistics.lostDays')}</th><th>TF</th><th>TG</th><th>TF YTD</th><th>TG YTD</th></tr></thead><tbody>{data.monthly.map(r=><tr key={r.month}><td>{mn(r.month)}</td><td>{ni(r.worked_hours)}</td><td>{r.accidents_with_lost_time}</td><td>{r.accidents_without_lost_time}</td><td>{r.lost_days}</td><td>{n(r.tf)}</td><td>{n(r.tg)}</td><td>{n(r.tf_ytd)}</td><td>{n(r.tg_ytd)}</td></tr>)}</tbody></table></div></section>
  </>}
 </section>
}
