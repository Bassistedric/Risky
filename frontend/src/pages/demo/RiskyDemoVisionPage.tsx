import './RiskyDemoVisionPage.css'

type Props={onBack:()=>void}

export default function RiskyDemoVisionPage({onBack}:Props){
 const modules=[
  ['△','Accidents & incidents','Événements, analyses, rapports'],
  ['♙','Personnel','Fiche 360°, événements, formations, actions'],
  ['✓','Formations','Compétences, habilitations, certificats'],
  ['◇','Analyse de risques','Kinney, RePSS, Standard, Ergonomie'],
  ['▣','Équipements','Contrôles, entretiens, trois feux verts'],
  ['⌖','Terrain','FMRA, STOP, Toolbox, ILT'],
  ['☑',"Plans d'action",'Actions issues des analyses et événements'],
 ]
 return <div className="demo-vision">
  <div className="demo-vision__bar"><div><span>RISKY DEMO</span><strong>Vision cible — interconnexion des modules</strong></div><button onClick={onBack}>← Retour à RISKY</button></div>
  <section className="demo-vision__intro"><div><span className="demo-kicker">DÉMONSTRATION — VISION CIBLE</span><h2>Du dossier collaborateur au pilotage QHSE</h2><p>Les écrans ci-dessous illustrent la trajectoire de développement. Ils ne représentent pas des fonctions déjà mises en production.</p></div><div className="demo-vision__tags"><span>Centraliser</span><span>Analyser</span><span>Agir</span><span>Communiquer</span></div></section>
  <section className="demo-grid">
   <article className="demo-card demo-card--person"><div className="demo-card__head"><span>01 · PERSONNEL 360°</span><b>À venir</b></div><div className="demo-person"><div className="demo-avatar">JD</div><div><h3>Dupont Jean</h3><p>Ouvrier HVAC · VMA Sud · PM1</p></div><i>Actif</i></div><div className="demo-tabs"><b>Synthèse</b><span>Formations</span><span>Habilitations</span><span>Événements</span><span>Actions</span></div><table><thead><tr><th>Événements liés</th><th>Conséquence</th><th>Statut</th></tr></thead><tbody><tr><td>Accident · Chute d'un escabeau</td><td>10 j arrêt</td><td><em>Analysé</em></td></tr><tr><td>Incident · Chute de plain-pied</td><td>Aucune</td><td><em>Clôturé</em></td></tr></tbody></table></article>
   <article className="demo-card"><div className="demo-card__head"><span>02 · FORMATIONS & HABILITATIONS</span><b>À venir</b></div><table><thead><tr><th>Intitulé</th><th>Échéance</th><th>Statut</th></tr></thead><tbody><tr><td>VCA**</td><td>15/03/2029</td><td><em>Valide</em></td></tr><tr><td>BA4</td><td>10/01/2029</td><td><em>Valide</em></td></tr><tr><td>Travail en hauteur</td><td>05/04/2028</td><td><em>Valide</em></td></tr><tr><td>Premiers secours</td><td>18/10/2026</td><td><em className="warn">À renouveler</em></td></tr></tbody></table></article>
  </section>
  <section className="demo-network"><div className="demo-card__head"><span>03 · INTERCONNEXION DES MODULES</span><b>Architecture cible</b></div><div className="demo-network__stage"><div className="demo-core"><strong>RISKY</strong><span>Q H S E</span><small>Source structurée</small></div>{modules.map((m,i)=><div key={m[1]} className={'demo-node demo-node--'+i}><i>{m[0]}</i><div><strong>{m[1]}</strong><span>{m[2]}</span></div></div>)}</div></section>
  <section className="demo-flow"><div className="demo-card__head"><span>04 · EXEMPLE DE FLUX DE DONNÉES</span><b>Une donnée, plusieurs usages</b></div><div className="demo-flow__row"><div><i>△</i><strong>Accident encodé</strong><span>Classification · causes</span></div><b>→</b><div><i>♙</i><strong>Fiche personnel</strong><span>Événement lié · impact</span></div><b>→</b><div><i>☑</i><strong>Plan d'action</strong><span>Responsable · échéance</span></div><b>→</b><div><i>▦</i><strong>Tableau de bord</strong><span>Indicateurs actualisés</span></div></div></section>
  <footer className="demo-final"><div><strong>RISKY <span>QHSE</span></strong><h2>Une donnée. Une source. Plusieurs usages.</h2><p>Centraliser · Analyser · Agir · Communiquer</p></div><div className="demo-benefits"><span>▤<b>Données centralisées</b></span><span>↔<b>Processus connectés</b></span><span>▦<b>Pilotage amélioré</b></span><span>◇<b>Culture QHSE renforcée</b></span></div></footer>
 </div>
}