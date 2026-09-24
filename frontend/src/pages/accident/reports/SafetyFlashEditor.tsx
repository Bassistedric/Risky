import { useEffect, useState } from 'react'
import './SafetyFlashEditor.css'
import { API_BASE_URL, downloadSafetyFlashPdf, getSafetyFlashPreview } from './reportApi'
import { getReportLanguage, rt } from './i18n/reportI18n'
import vmaLogo from '../../../assets/images/vma_logo.jpg'
import zeroLogo from '../../../assets/images/Go_for_zero.jpg'

type Props = { eventId: number; onBack: () => void }
type Photo = { id:number; original_filename:string; caption:string|null; sort_order:number; filename?:string }
type Draft = { event_type:string; subject:string; facts:string; explanations:string; recommendations:string; photos:Photo[] }

export default function SafetyFlashEditor({ eventId, onBack }: Props) {
    const [draft,setDraft]=useState<Draft|null>(null)
    const [error,setError]=useState<string|null>(null)
    const [busy,setBusy]=useState(false)

    useEffect(()=>{ getSafetyFlashPreview(eventId).then(setDraft).catch(e=>setError(e instanceof Error?e.message:String(e))) },[eventId])
    if(error) return <div className="sf-editor__state">{error}<button onClick={onBack}>{rt('preview.back')}</button></div>
    if(!draft) return <div className="sf-editor__state">{rt('preview.loading')}</div>
    const set=(key:keyof Draft,value:any)=>setDraft({...draft,[key]:value})

    const Header=()=> <header className="sf-editor__header">
        <img className="sf-editor__vma" src={vmaLogo} alt="VMA"/>
        <h1>CFE Safety Flash</h1>
        <img className="sf-editor__zero" src={zeroLogo} alt="Go for Zero"/>
    </header>

    return <div className="sf-editor">
        <div className="sf-editor__toolbar">
            <button onClick={onBack}>← {rt('preview.back')}</button>
            <strong>CFE Safety Flash</strong>
            <button className="sf-editor__generate" disabled={busy} onClick={async()=>{try{setBusy(true);await downloadSafetyFlashPdf(eventId,getReportLanguage(),draft)}finally{setBusy(false)}}}>{rt('preview.generatePdf')}</button>
        </div>

        <div className="sf-editor__sheet">
            <Header/>
            <div className="sf-editor__toprow">
                <div className="sf-editor__type">
                    <strong>{rt('safetyFlash.editor.what')}</strong>
                    {['INCIDENT','ACCIDENT','NEAR_MISS'].map(v=><label key={v} className={draft.event_type===v?'selected':''}>
                        <input type="radio" checked={draft.event_type===v} onChange={()=>set('event_type',v)}/>
                        {rt('values.eventType.'+v)}
                    </label>)}
                </div>
                <label className="sf-editor__field sf-editor__subject">
                    <span>{rt('safetyFlash.editor.subject')}</span>
                    <input value={draft.subject} onChange={e=>set('subject',e.target.value)}/>
                </label>
            </div>
            <label className="sf-editor__field sf-editor__boxed"><span>{rt('safetyFlash.editor.facts')}</span><textarea rows={5} value={draft.facts} onChange={e=>set('facts',e.target.value)}/></label>
            <label className="sf-editor__field sf-editor__boxed sf-editor__explanations"><span>{rt('safetyFlash.editor.explanations')}</span><textarea rows={9} value={draft.explanations} onChange={e=>set('explanations',e.target.value)}/></label>
            <small className="sf-editor__internal">Internal use only.</small>
        </div>

        <div className="sf-editor__sheet">
            <Header/>
            <label className="sf-editor__field sf-editor__boxed sf-editor__actions"><span>{rt('safetyFlash.editor.actions')}</span><textarea rows={6} value={draft.recommendations} onChange={e=>set('recommendations',e.target.value)}/></label>
            <div className="sf-editor__support">
                <h2>{rt('safetyFlash.editor.support')}</h2>
                <div className="sf-editor__photos">
                    {draft.photos.length ? draft.photos.map(p=><div key={p.id}>
                        <img src={`${API_BASE_URL}/events/${eventId}/photos/${p.id}/file`} alt={p.caption||p.original_filename}/>
                        <small>{p.caption||p.original_filename}</small>
                    </div>) : <div>{rt('safetyFlash.editor.noPhoto')}</div>}
                </div>
            </div>
            <small className="sf-editor__internal">Internal use only.</small>
        </div>
    </div>
}
