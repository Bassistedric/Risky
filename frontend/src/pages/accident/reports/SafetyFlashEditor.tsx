import { useEffect, useState } from 'react'
import './SafetyFlashEditor.css'
import { downloadSafetyFlashPdf, getSafetyFlashPreview } from './reportApi'
import { getReportLanguage, rt } from './i18n/reportI18n'

type Props={eventId:number;onBack:()=>void}
type Draft={event_type:string;subject:string;facts:string;explanations:string;recommendations:string;photos:Array<{id:number;original_filename:string;caption:string|null;sort_order:number}>}

export default function SafetyFlashEditor({eventId,onBack}:Props){
 const [draft,setDraft]=useState<Draft|null>(null); const [error,setError]=useState<string|null>(null); const [busy,setBusy]=useState(false)
 useEffect(()=>{getSafetyFlashPreview(eventId).then(setDraft).catch(e=>setError(e instanceof Error?e.message:String(e)))},[eventId])
 if(error)return <div className="sf-editor__state">{error}<button onClick={onBack}>{rt('preview.back')}</button></div>
 if(!draft)return <div className="sf-editor__state">{rt('preview.loading')}</div>
 const set=(key:keyof Draft,value:any)=>setDraft({...draft,[key]:value})
 return <div className="sf-editor">
   <div className="sf-editor__toolbar"><button onClick={onBack}>← {rt('preview.back')}</button><div><span>CFE</span><strong>Safety Flash</strong></div><button disabled={busy} onClick={async()=>{try{setBusy(true);await downloadSafetyFlashPdf(eventId,getReportLanguage(),draft)}finally{setBusy(false)}}}>{rt('preview.generatePdf')}</button></div>
   <div className="sf-editor__sheet">
    <header><div className="sf-editor__brand">VMA</div><h1>CFE Safety Flash</h1></header>
    <div className="sf-editor__type"><strong>{rt('safetyFlash.editor.what')}</strong>{['INCIDENT','ACCIDENT','NEAR_MISS'].map(v=><label key={v}><input type="radio" checked={draft.event_type===v} onChange={()=>set('event_type',v)}/>{rt('values.eventType.'+v)}</label>)}</div>
    <label className="sf-editor__field"><span>{rt('safetyFlash.editor.subject')}</span><input value={draft.subject} onChange={e=>set('subject',e.target.value)}/></label>
    <label className="sf-editor__field"><span>{rt('safetyFlash.editor.facts')}</span><textarea rows={8} value={draft.facts} onChange={e=>set('facts',e.target.value)}/></label>
    <label className="sf-editor__field"><span>{rt('safetyFlash.editor.explanations')}</span><textarea rows={8} value={draft.explanations} onChange={e=>set('explanations',e.target.value)}/></label>
   </div>
   <div className="sf-editor__sheet">
    <header><div className="sf-editor__brand">VMA</div><h1>CFE Safety Flash</h1></header>
    <h2>{rt('safetyFlash.editor.support')}</h2>
    <div className="sf-editor__photos">{draft.photos.length?draft.photos.map(p=><div key={p.id}>Photo {p.sort_order}<small>{p.caption||p.original_filename}</small></div>):<div>{rt('safetyFlash.editor.noPhoto')}</div>}</div>
    <label className="sf-editor__field"><span>{rt('safetyFlash.editor.actions')}</span><textarea rows={10} value={draft.recommendations} onChange={e=>set('recommendations',e.target.value)}/></label>
   </div>
 </div>
}