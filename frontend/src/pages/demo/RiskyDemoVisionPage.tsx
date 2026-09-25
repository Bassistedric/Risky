import './RiskyDemoVisionPage.css'

type Props={onBack:()=>void}

export default function RiskyDemoVisionPage({_onBack}:Props){
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
  <div className="demo-vision__bar"><div><span>RISKY DEMO</span><strong>Vision cible — interconnexion des modules</strong></div><span className="demo-vision__mode">PROJECTION</span></div>
  <section className="demo-vision__intro"><div><span className="demo-kicker">DÉMONSTRATION — VISION CIBLE</span><h2>Du dossier collaborateur au pilotage QHSE</h2><p>Les écrans ci-dessous illustrent la trajectoire de développement. Ils ne représentent pas des fonctions déjà mises en production.</p></div><div className="demo-vision__tags"><span>Centraliser</span><span>Analyser</span><span>Agir</span><span>Communiquer</span></div></section>
  <section className="demo-grid">
   <article className="demo-card demo-card--person"><div className="demo-card__head"><span>01 · PERSONNEL 360°</span><b>À venir</b></div><div className="demo-person"><div className="demo-avatar">JD</div><div><h3>Jean Dupont</h3><p>Ouvrier HVAC · VMA Sud · PM1</p></div><i>Actif</i></div><div className="demo-tabs"><b>Synthèse</b><span>Formations</span><span>Habilitations</span><span>Événements</span><span>Actions</span></div><table><thead><tr><th>Événements liés</th><th>Conséquence</th><th>Statut</th></tr></thead><tbody><tr><td>Accident · Chute d'un escabeau</td><td>10 j arrêt</td><td><em>Analysé</em></td></tr><tr><td>Incident · Chute de plain-pied</td><td>Aucune</td><td><em>Clôturé</em></td></tr></tbody></table></article>
   <article className="demo-card"><div className="demo-card__head"><span>02 · FORMATIONS & HABILITATIONS</span><b>À venir</b></div><table><thead><tr><th>Intitulé</th><th>Échéance</th><th>Statut</th></tr></thead><tbody><tr><td>VCA**</td><td>15/03/2029</td><td><em>Valide</em></td></tr><tr><td>BA4</td><td>10/01/2029</td><td><em>Valide</em></td></tr><tr><td>Travail en hauteur</td><td>05/04/2028</td><td><em>Valide</em></td></tr><tr><td>Premiers secours</td><td>18/10/2026</td><td><em className="warn">À renouveler</em></td></tr></tbody></table></article>
  </section>
  <section className="demo-ops">
   <div className="demo-card__head"><span>03 · ACTIVITÉ TERRAIN & INDICATEURS</span><b>À venir</b></div>
   <div className="demo-kpis">
    <div><span>Toolbox</span><strong>184</strong><small>participations enregistrées</small><em>92 % objectif</em></div>
    <div><span>ILT</span><strong>126</strong><small>inspections terrain</small><em>88 % objectif</em></div>
    <div><span>FMRA</span><strong>1 248</strong><small>analyses terrain</small><em>96 % réalisées</em></div>
    <div><span>STOP</span><strong>73</strong><small>signalements / actions</small><em>61 clôturés</em></div>
   </div>
   <div className="demo-ops__note">Les données terrain alimentent directement les indicateurs par entité, métier, période et collaborateur.</div>
  </section>

  <section className="demo-group">
   <div className="demo-card__head"><span>04 · PILOTAGE MULTI-ENTITÉS VMA</span><b>Vision consolidée</b></div>
   <div className="demo-group__top"><div><small>Périmètre</small><strong>VMA</strong><span>Vue consolidée du cluster</span></div><div className="demo-group__headline"><span><b>2 431</b> h terrain suivies</span><span><b>310</b> ILT / Toolbox</span><span><b>146</b> actions QHSE</span><span><b>91 %</b> complétude</span></div></div>
   <table className="demo-group__table"><thead><tr><th>Entité</th><th>Accidents</th><th>Toolbox</th><th>ILT</th><th>Actions ouvertes</th><th>Complétude</th></tr></thead><tbody>
    <tr><td><strong>VMA Sud</strong><small>HVAC · REF · ELEC</small></td><td>12</td><td>184</td><td>126</td><td>38</td><td><em>94 %</em></td></tr>
    <tr><td><strong>VMA Nord</strong><small>Entité</small></td><td>7</td><td>142</td><td>98</td><td>27</td><td><em>90 %</em></td></tr>
    <tr><td><strong>VMA Maintenance</strong><small>Maintenance</small></td><td>5</td><td>116</td><td>83</td><td>19</td><td><em>92 %</em></td></tr>
    <tr><td><strong>VMA Polska</strong><small>Entité</small></td><td>4</td><td>101</td><td>71</td><td>14</td><td><em>87 %</em></td></tr>
   </tbody></table>
   <div className="demo-group__footer"><span>VMA</span><b>→</b><span>Entité</span><b>→</b><span>Métier</span><b>→</b><span>Collaborateur / activité</span><p>Données fictives de démonstration</p></div>
  </section>

  <section className="demo-network"><div className="demo-card__head"><span>05 · INTERCONNEXION DES MODULES</span><b>Architecture cible</b></div><div className="demo-network__stage"><div className="demo-core"><strong>RISKY</strong><span>Q H S E</span><small>Source structurée</small></div>{modules.map((m,i)=><div key={m[1]} className={'demo-node demo-node--'+i}><i>{m[0]}</i><div><strong>{m[1]}</strong><span>{m[2]}</span></div></div>)}</div></section>
  <section className="demo-flow"><div className="demo-card__head"><span>06 · EXEMPLE DE FLUX DE DONNÉES</span><b>Une donnée, plusieurs usages</b></div><div className="demo-flow__row"><div><i>△</i><strong>Accident encodé</strong><span>Classification · causes</span></div><b>→</b><div><i>♙</i><strong>Fiche personnel</strong><span>Événement lié · impact</span></div><b>→</b><div><i>☑</i><strong>Plan d'action</strong><span>Responsable · échéance</span></div><b>→</b><div><i>▦</i><strong>Tableau de bord</strong><span>Indicateurs actualisés</span></div></div></section>
  <footer className="demo-final"><div><strong>RISKY <span>QHSE</span></strong><h2>Une donnée. Une source. Plusieurs usages.</h2><p>Centraliser · Analyser · Agir · Communiquer</p></div><div className="demo-benefits"><span>▤<b>Données centralisées</b></span><span>↔<b>Processus connectés</b></span><span>▦<b>Pilotage amélioré</b></span><span>◇<b>Culture QHSE renforcée</b></span></div></footer>
 </div>
}