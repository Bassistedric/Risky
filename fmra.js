// Risky FMRA — based on the existing QHSE weekly FMRA workflow
const fmraDemo=[
 {id:'FMRA-2026-084',date:'20/08/2026',site:'Jumet',metier:'HVAC',responsable:'A. Martin',pm:'P. Lambert',status:'GO'},
 {id:'FMRA-2026-083',date:'18/08/2026',site:'LLN',metier:'Élec (HT-BT)',responsable:'J. Dupont',pm:'M. Leroy',status:'STOP'}
];
const fmraBase=[
 {id:'orga1',q:'Les travaux prévus cette semaine sont-ils clairement définis ?',trigger:'Non',rec:'Clarifier le planning de la semaine avec le responsable/coordination avant de démarrer.'},
 {id:'orga2',q:"L'effectif est-il complet et qualifié pour ces travaux ?",trigger:'Non',rec:'Identifier le renfort ou la qualification manquante et en informer le planning/RH avant démarrage.'},
 {id:'orga3',q:'Le matériel et les EPI nécessaires sont-ils disponibles et en bon état ?',trigger:'Non',rec:'Commander ou remplacer le matériel/EPI manquant ou défectueux avant de démarrer les travaux.'}
];
const fmraRisks={
 Elec:[
  ['tst','Travail sous tension (TST) prévu cette semaine ?','Vérifier que la demande de travail sous tension a été introduite et validée.'],
  ['consignation','Consignation / déconsignation prévue cette semaine ?','Vérifier que la procédure de consignation/déconsignation complète sera appliquée.'],
  ['tremie',"Travail à proximité d'une trémie ou d'une ouverture de sol/plancher prévu cette semaine ?",'Vérifier la mise en place d’une protection collective (garde-corps, plaque, balisage).'],
  ['confine','Travail en espace confiné prévu cette semaine ?',"Vérifier le permis d'entrée, la présence d'un surveillant et le contrôle atmosphérique."],
  ['nouvel','Nouvel intervenant non briefé dans l’équipe ?',"Réaliser l'accueil sécurité et le briefing avant démarrage."],
  ['meteo','Risque de conditions météo dégradées ?','Vérifier les prévisions avant intervention, prévoir un report si nécessaire.'],
  ['autre','Autre tâche à risque (à préciser) ?','Évaluer les mesures de prévention nécessaires avec le SIPP avant de démarrer.',true]
 ],
 HVAC:[
  ['tremie',"Travail à proximité d'une trémie ou d'une ouverture de sol/plancher prévu cette semaine ?",'Vérifier la mise en place d’une protection collective (garde-corps, plaque, balisage).'],
  ['confine','Travail en espace confiné prévu cette semaine ?',"Vérifier le permis d'entrée, la présence d'un surveillant et le contrôle atmosphérique."],
  ['pression','Intervention sur installation sous pression ?','Vérifier la dépressurisation/consignation de l’installation et le contrôle de l’équipement sous pression si applicable.'],
  ['consignation','Consignation / déconsignation prévue cette semaine ?','Vérifier que la procédure de consignation/déconsignation complète sera appliquée.'],
  ['levage','Utilisation d’équipement de levage ?','Vérifier le contrôle/certification de l’équipement et la formation/habilitation du conducteur.'],
  ['legionelle','Intervention sur tour de refroidissement ou circuit d’eau (légionelle) prévue ?','Vérifier le port des EPI respiratoires adaptés et le respect du protocole de désinfection.'],
  ['meteo','Travaux extérieurs ou sensibles aux conditions météo prévus cette semaine ?','Vérifier les prévisions avant intervention, prévoir un report si nécessaire.'],
  ['nouvel','Nouvel intervenant non briefé dans l’équipe ?',"Réaliser l'accueil sécurité et le briefing avant démarrage."],
  ['autre','Autre tâche à risque (permis feu, ...) ?','Identifier précisément le risque et introduire le permis de travail adapté en lien avec le SIPP.',true]
 ],
 Ref:[
  ['fluides','Manipulation de fluides réfrigérants prévue ?','Vérifier la disponibilité des EPI adaptés contre les brûlures cryogéniques et les fuites.'],
  ['nh3',"Intervention sur installation à l'ammoniac (NH3) prévue cette semaine ?",'Vérifier l’habilitation NH3, les détecteurs de fuite et prévenir la coordination si nécessaire.'],
  ['pression','Intervention sur circuit sous pression ?','Vérifier la dépressurisation/consignation du circuit avant intervention.'],
  ['consignation','Consignation / déconsignation prévue cette semaine ?','Vérifier que la procédure de consignation/déconsignation complète sera appliquée.'],
  ['meteo','Travaux extérieurs ou sensibles aux conditions météo prévus cette semaine ?','Vérifier les prévisions avant intervention, prévoir un report si nécessaire.'],
  ['tremie',"Travail à proximité d'une trémie ou d'une ouverture de sol/plancher prévu cette semaine ?",'Vérifier la mise en place d’une protection collective (garde-corps, plaque, balisage).'],
  ['nouvel','Nouvel intervenant non briefé dans l’équipe ?',"Réaliser l'accueil sécurité et le briefing avant démarrage."],
  ['confine','Travail en espace confiné prévu cette semaine ?',"Vérifier le permis d'entrée, la présence d'un surveillant et le contrôle atmosphérique."],
  ['autre','Autre tâche à risque (permis feu, ...) ?','Identifier précisément le risque et introduire le permis de travail adapté en lien avec le SIPP.',true]
 ]
};
let fmraState={answers:{},metier:'Elec'};
function fmraPage(){return `<div class="fmra-page"><div class="module-title"><div><div class="eyebrow fmra-green">FMRA</div><h2>Analyse hebdomadaire des risques</h2><p class="muted">À compléter par le chef d’équipe en début de semaine.</p></div><button class="btn fmra-btn" onclick="newFmra()">+ Nouvelle FMRA</button></div><div class="fmra-kpis"><div class="card"><span>FMRA enregistrées</span><strong>${fmraDemo.length}</strong></div><div class="card"><span>OK GO</span><strong>${fmraDemo.filter(x=>x.status==='GO').length}</strong></div><div class="card"><span>STOP</span><strong class="fmra-red">${fmraDemo.filter(x=>x.status==='STOP').length}</strong></div></div><div class="card fmra-list">${fmraDemo.map(f=>`<div class="row"><span><b>${f.id}</b> · ${f.metier}<br><span class="muted">${f.date} · ${f.site} · Responsable : ${f.responsable} · PM : ${f.pm}</span></span><span class="fmra-status ${f.status==='GO'?'go':'nogo'}">${f.status}</span></div>`).join('')}</div></div>`}
function newFmra(){fmraState={answers:{},metier:'Elec'};renderFmraForm()}
function renderFmraForm(){const m=fmraState.metier;document.querySelector('#content').innerHTML=`<div class="fmra-page"><div class="event-head"><div><div class="eyebrow fmra-green">FMRA</div><h2>Analyse hebdomadaire</h2><p>Organisation de la semaine → risques spécifiques → décision.</p></div><div class="info-banner fmra-info"><span class="info-dot fmra-i">i</span><span>Cette FMRA reprend la logique de l’outil QHSE terrain existant, intégrée dans Risky.</span></div></div><section class="card fmra-block blue"><div class="fmra-block-title">Identification</div><div class="fmra-ident"><label>Date & heure<input id="fdate" type="datetime-local" value="2026-08-20T08:00"></label><label>Métier<select id="fmetier" onchange="fmraChangeMetier(this.value)"><option value="Elec" ${m==='Elec'?'selected':''}>Élec (HT-BT)</option><option value="HVAC" ${m==='HVAC'?'selected':''}>HVAC</option><option value="Ref" ${m==='Ref'?'selected':''}>Réfrigération</option></select></label><label>Chantier<select id="fsite"><option>Jumet</option><option>Louvain-la-Neuve</option><option>Alleur</option></select></label><label>Responsable (Nom & Prénom)<select id="fresp"><option>Chef d’équipe</option><option>Site Supervisor</option><option>Responsable SIPP</option></select></label><label>PM<select id="fpm"><option>PM — Démo</option><option>Non attribué</option></select></label></div></section><div class="fmra-two"><section class="card fmra-block amber"><div class="fmra-block-title">Organisation de la semaine</div>${fmraBase.map(q=>fmraQuestion(q)).join('')}</section><section class="card fmra-block red"><div class="fmra-block-title">Risques spécifiques — ${m==='Elec'?'Élec (HT-BT)':m==='Ref'?'Réfrigération':'HVAC'}</div>${fmraRisks[m].map(q=>fmraQuestion({id:q[0],q:q[1],trigger:'Oui',rec:q[2],free:q[3]})).join('')}</section></div><section class="card fmra-decision-dark"><h3>Décision</h3><p>Sur base des éléments identifiés ci-dessus :</p><div class="decision-buttons"><button class="decision go" onclick="saveFmra('GO')"><strong>OK GO</strong><span>Démarrage autorisé</span></button><button class="decision stop" onclick="saveFmra('STOP')"><strong>STOP</strong><span>Point bloquant à traiter</span></button></div></section></div>`}
function fmraChangeMetier(v){fmraState.metier=v;fmraState.answers={};renderFmraForm()}
function fmraQuestion(q){const v=fmraState.answers[q.id]||'';return `<div class="fmra-q"><div class="fmra-qline"><span>${q.q}</span><div class="yn"><button class="${v==='Oui'?'sel '+(q.trigger==='Oui'?'bad':'good'):''}" onclick="fmraAnswer('${q.id}','Oui')">Oui</button><button class="${v==='Non'?'sel '+(q.trigger==='Non'?'bad':'good'):''}" onclick="fmraAnswer('${q.id}','Non')">Non</button></div></div>${v===q.trigger?`<div class="fmra-rec">${q.rec}</div>`:''}${q.free&&v==='Oui'?`<textarea id="fautre" rows="2" placeholder="Précisez le risque..."></textarea>`:''}</div>`}
function fmraAnswer(id,v){fmraState.answers[id]=v;renderFmraForm()}
function saveFmra(status){const all=[...fmraBase.map(x=>x.id),...fmraRisks[fmraState.metier].map(x=>x[0])];if(all.some(id=>!fmraState.answers[id])){alert('Merci de répondre à toutes les questions avant de valider.');return}const site=document.getElementById('fsite')?.value||'Jumet',resp=document.getElementById('fresp')?.value||'Chef d’équipe',pm=document.getElementById('fpm')?.value||'PM — Démo';const flagged=[];fmraBase.forEach(q=>{if(fmraState.answers[q.id]===q.trigger)flagged.push(q.q)});fmraRisks[fmraState.metier].forEach(q=>{if(fmraState.answers[q[0]]==='Oui')flagged.push(q[1])});const id=`FMRA-2026-${String(85+fmraDemo.length).padStart(3,'0')}`;fmraDemo.unshift({id,date:'20/08/2026',site,metier:fmraState.metier==='Elec'?'Élec (HT-BT)':fmraState.metier==='Ref'?'Réfrigération':'HVAC',responsable:resp,pm,status});if(status==='STOP'&&typeof openStopFromFmra==='function'){openStopFromFmra({fmraId:id,site,responsable:resp,flagged});return}show('fmra',document.querySelector('[data-page=fmra]'))}
const riskyBaseShow=show;show=function(p,b){if(p==='fmra'){document.querySelectorAll('.navitem').forEach(x=>x.classList.remove('active'));b?.classList.add('active');document.querySelector('#title').textContent='FMRA';document.querySelector('#content').innerHTML=fmraPage();return}return riskyBaseShow(p,b)};
