// Demo environment normalization: VMA Sud is the organization; HVAC / REF / ELEC are the primary reporting axes.
const riskyDemoMap={
  'Jumet':'ELEC',
  'LLN':'HVAC',
  'Louvain-la-Neuve':'HVAC',
  'Alleur':'REF',
  'Tous les sites':'VMA Sud — tous métiers',
  'Tous sites':'VMA Sud — tous métiers',
  'Site':'Métier / entité',
  'Site *':'Métier / entité *'
};
function normalizeRiskyDemo(root=document){
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
  const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  nodes.forEach(n=>{const raw=n.nodeValue,trim=raw.trim();if(riskyDemoMap[trim])n.nodeValue=raw.replace(trim,riskyDemoMap[trim]);});
  root.querySelectorAll?.('option').forEach(o=>{const t=o.textContent.trim();if(riskyDemoMap[t]){o.textContent=riskyDemoMap[t];if(!o.hasAttribute('value'))o.value=riskyDemoMap[t];}});
}
const envShowBase=show;show=function(p,b){envShowBase(p,b);normalizeRiskyDemo(document.querySelector('#content'));};
normalizeRiskyDemo(document);

const sidebarSignature=document.getElementById('bycco-signature');
if(sidebarSignature)sidebarSignature.src='winston_bycco_logo.png';
