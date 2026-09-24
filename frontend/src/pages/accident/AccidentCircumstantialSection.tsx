import { useCallback, useEffect, useState } from 'react'
import { at } from './accidentI18n'
import { API_BASE_URL } from './accidentApi'
import './AccidentCircumstantialSection.css'

type Mode = 'details' | 'causes'
type Data = Record<string, string | boolean | null>
type Props = { eventId: number; mode: Mode }

const detailFields = [
 'victim_address','victim_birth_date','victim_company_seniority','victim_job_seniority',
 'employer_name','employer_address','insurer_name','insurance_policy_number',
 'prevention_advisor','sipp_manager','sepp_name','sepp_contact','report_contributors','report_recipients',
]
const causeGroups = [
 { key:'primary', details:'primary_details', categories:[
  {key:'material', options:['product','machine','tool','orderCleanliness','transport','materialOther']},
  {key:'collective', options:['collectiveAbsent','collectiveMissing','collectiveDisabled','collectiveOther']},
  {key:'ppe', options:['ppeMisuse','ppeAbsent','ppeUnsuitable','ppeOther']},
  {key:'environment', options:['lighting','noise','temperature','environmentOther']},
 ]},
 { key:'secondary', details:'secondary_details', categories:[
  {key:'organization', options:['riskAnalysis','instructions','sippOperation','organizationOther']},
  {key:'communication', options:['followupControl','trainingGap','communicationOther']},
  {key:'human', options:['distraction','intentionalNegligence','fatigue','incompetence','haste','humanOther']},
 ]},
 { key:'tertiary', details:'tertiary_details', categories:[
  {key:'thirdMaterial', options:['designManufacturing','noncompliantEquipment']},
  {key:'badAdvice', options:['badAdvice']},
  {key:'thirdOrganization', options:['instructionsNotFollowed','sitePressure','thirdOrganizationOther']},
 ]},
]

function readSelections(data: Data): string[] {
 try { return JSON.parse(String(data.cause_selections_json || '[]')) } catch { return [] }
}

function AccidentCircumstantialSection({ eventId, mode }: Props) {
 const [required,setRequired]=useState(false)
 const [data,setData]=useState<Data>({})
 const [editing,setEditing]=useState(false)
 const [saving,setSaving]=useState(false)
 const [error,setError]=useState<string|null>(null)

 const load=useCallback(async()=>{
  try{
   const ar=await fetch(API_BASE_URL+'/events/'+eventId+'/serious-accident-assessment')
   if(!ar.ok)return
   const assessment=await ar.json()
   const isRequired=Boolean(assessment.circumstantial_report_required)
   setRequired(isRequired)
   if(!isRequired)return
   const response=await fetch(API_BASE_URL+'/events/'+eventId+'/circumstantial-report')
   if(response.ok){const value=await response.json();if(value)setData(value)}
  }catch{setError(at('circumstantial.loadError'))}
 },[eventId])
 useEffect(()=>{void load()},[load])
 if(!required)return null

 const set=(key:string,value:string|boolean)=>setData(current=>({...current,[key]:value}))
 const selections=readSelections(data)
 const toggleSelection=(code:string,checked:boolean)=>{
  const next=checked ? Array.from(new Set([...selections,code])) : selections.filter(item=>item!==code)
  set('cause_selections_json',JSON.stringify(next))
 }
 const save=async()=>{
  const token=sessionStorage.getItem('risky_session_token')
  if(!token){setError(at('circumstantial.sessionRequired'));return}
  try{
   setSaving(true);setError(null)
   const response=await fetch(API_BASE_URL+'/events/'+eventId+'/circumstantial-report',{
    method:'PUT',headers:{'Content-Type':'application/json','X-Session-Token':token},body:JSON.stringify(data),
   })
   if(!response.ok)throw new Error()
   const value=await response.json();setData(value);setEditing(false)
  }catch{setError(at('circumstantial.saveError'))}finally{setSaving(false)}
 }
 const display=(key:string)=>{const value=data[key];return typeof value==='string'&&value.trim()?value:at('common.notProvided')}

 return <section className="accident-circumstantial">
  <div className="accident-circumstantial__head"><div>
   <span className="accident-circumstantial__eyebrow">{at('circumstantial.required')}</span>
   <h2>{at(mode==='details'?'circumstantial.detailsTitle':'circumstantial.causesTitle')}</h2>
  </div>{!editing&&<button className="risky-button" type="button" onClick={()=>setEditing(true)}>{at('common.edit')}</button>}</div>
  {mode==='details'?<div className="accident-circumstantial__grid">
   {detailFields.map(key=><label key={key} className={key==='report_contributors'||key==='report_recipients'?'wide':''}>
    <span>{at('circumstantial.fields.'+key)}</span>
    {editing?(key==='report_contributors'||key==='report_recipients'||key.endsWith('_address')||key==='sepp_contact'
     ?<textarea value={String(data[key]??'')} onChange={e=>set(key,e.target.value)}/>
     :<input type={key==='victim_birth_date'?'date':'text'} value={String(data[key]??'')} onChange={e=>set(key,e.target.value)}/>)
     :<p>{display(key)}</p>}
   </label>)}
  </div>:<div className="accident-circumstantial__cause-wrap">
   {causeGroups.map(group=><div className="accident-circumstantial__cause-card" key={group.key}>
    <h3>{at('circumstantial.'+group.key+'.title')}</h3>
    {editing ? <div className="accident-circumstantial__category-grid">
     {group.categories.map(category=><div className="accident-circumstantial__category" key={category.key}>
      <h4>{at('circumstantial.categories.'+category.key)}</h4>
      {category.options.map(code=><label className="accident-circumstantial__check" key={code}>
       <input type="checkbox" checked={selections.includes(code)} onChange={e=>toggleSelection(code,e.target.checked)}/>
       <span>{at('circumstantial.options.'+code)}</span>
      </label>)}
     </div>)}
    </div> : <div className="accident-circumstantial__selected">
     {group.categories.flatMap(category=>category.options).filter(code=>selections.includes(code)).map(code=>
      <span className="accident-circumstantial__pill" key={code}>✓ {at('circumstantial.options.'+code)}</span>
     )}
     {group.categories.flatMap(category=>category.options).filter(code=>selections.includes(code)).length===0 &&
      <span className="accident-circumstantial__empty">{at('circumstantial.noCauseSelected')}</span>}
    </div>}
    <span className="accident-circumstantial__detail-label">{at('circumstantial.precision')}</span>
    {editing?<textarea value={String(data[group.details]??'')} onChange={e=>set(group.details,e.target.value)}/>:<p>{display(group.details)}</p>}
   </div>)}
  </div>}
  {error&&<p className="accident-circumstantial__error">{error}</p>}
  {editing&&<div className="accident-circumstantial__actions">
   <button className="risky-button risky-button--cancel" type="button" disabled={saving} onClick={()=>{setEditing(false);void load()}}>{at('common.cancel')}</button>
   <button className="risky-button risky-button--confirm" type="button" disabled={saving} onClick={()=>void save()}>{saving?at('circumstantial.saving'):at('circumstantial.save')}</button>
  </div>}
 </section>
}
export default AccidentCircumstantialSection
