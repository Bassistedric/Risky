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
 { key:'primary', checks:['primary_material_factors','primary_collective_protection','primary_personal_protection','primary_environmental_factors','primary_other'], details:'primary_details' },
 { key:'secondary', checks:['secondary_organization','secondary_communication','secondary_human_factors','secondary_other'], details:'secondary_details' },
 { key:'tertiary', checks:['tertiary_third_party_material','tertiary_incorrect_advice','tertiary_third_party_organization','tertiary_other'], details:'tertiary_details' },
]

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
  </div>:<div className="accident-circumstantial__cause-grid">
   {causeGroups.map(group=><div className="accident-circumstantial__cause-card" key={group.key}>
    <h3>{at('circumstantial.'+group.key+'.title')}</h3>
    {group.checks.map(key=><label className="accident-circumstantial__check" key={key}>
     <input type="checkbox" checked={Boolean(data[key])} disabled={!editing} onChange={e=>set(key,e.target.checked)}/>
     <span>{at('circumstantial.fields.'+key)}</span>
    </label>)}
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
