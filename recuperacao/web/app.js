'use strict';
let data = null;
let selectedRows = [];
const $ = id => document.getElementById(id);
const ns = 'http://www.w3.org/2000/svg';
const fmtDate = value => value ? value.split('-').reverse().join('/') : 'Não definido';
const companyName = name => name.replace(' Incorporadora e Construtora', '').replace(' S.A.', '');

function element(tag, text, cls) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (cls) el.className = cls;
  return el;
}
function svgEl(tag, attrs = {}, text) {
  const el = document.createElementNS(ns, tag);
  Object.entries(attrs).forEach(([key, value]) => el.setAttribute(key, value));
  if (text !== undefined) el.textContent = text;
  return el;
}
function svgRoot(id, width, height, label) {
  $(id).replaceChildren();
  const svg = svgEl('svg', {viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': label});
  svg.append(svgEl('title', {}, label));
  $(id).append(svg);
  return svg;
}
function renderYears(rows) {
  const counts = new Map();
  rows.forEach(r => {const year = String(r.ano_pedido ?? 'Não apurado'); counts.set(year, (counts.get(year) || 0) + 1);});
  const entries = [...counts].sort(([a], [b]) => a.localeCompare(b));
  const width = 560, height = 240, base = 197, top = 25;
  const max = Math.max(1, ...entries.map(([, n]) => n));
  const svg = svgRoot('year-chart', width, height, entries.length ? `Pedidos por ano: ${entries.map(([y,n]) => `${y}: ${n}`).join('; ')}` : 'Nenhum episódio no recorte.');
  if (!entries.length) {svg.append(svgEl('text', {x: 30, y: 100}, 'Nenhum episódio no recorte.')); return;}
  for (let n = 0; n <= max; n++) {
    const y = base - n / max * (base - top);
    svg.append(svgEl('line', {x1: 35, x2: 540, y1: y, y2: y, class: 'grid'}));
    svg.append(svgEl('text', {x: 20, y: y + 4, class: 'tick'}, String(n)));
  }
  const step = 490 / entries.length;
  entries.forEach(([year, n], index) => {
    const w = Math.min(62, step * .58), x = 45 + index * step + (step - w) / 2;
    const h = n / max * (base - top);
    const bar = svgEl('rect', {x, y: base-h, width:w, height:h, rx:5, class:'bar'});
    bar.append(svgEl('title', {}, `${year}: ${n} episódio(s)`));
    svg.append(bar, svgEl('text', {x:x+w/2,y:base-h-8,'text-anchor':'middle',class:'value'},String(n)),svgEl('text',{x:x+w/2,y:222,'text-anchor':'middle'},year));
  });
}
function renderQuality(rows) {
  const fields = [['CNPJ','cnpj'],['Processo','processo'],['Pedido completo','pedido'],['Encerramento reportado','encerramento']];
  const counts = fields.map(([label,key]) => [label, rows.filter(r => r[key] !== null && r[key] !== undefined).length]);
  counts.push(['Status auditado', rows.filter(r => r.status_no_corte !== 'nao_auditado').length]);
  const svg = svgRoot('quality-chart',560,240,`Campos preenchidos em ${rows.length} episódios: ${counts.map(([l,n]) => `${l}: ${n}`).join('; ')}`);
  counts.forEach(([label,n],i) => {
    const y = 16+i*44;
    svg.append(svgEl('text',{x:0,y:y+17},label),svgEl('rect',{x:185,y,width:290,height:24,rx:5,class:'track'}));
    if(n) svg.append(svgEl('rect',{x:185,y,width:n/rows.length*290,height:24,rx:5,class:'bar'}));
    svg.append(svgEl('text',{x:492,y:y+17,class:'value'},`${n} / ${rows.length}`));
  });
}
function renderTimeline(rows) {
  const dates = rows.flatMap(r => [r.pedido,r.encerramento]).filter(Boolean).map(d => Date.parse(d));
  const min = dates.length ? Math.min(...dates) : Date.parse('2015-01-01');
  const max = Math.max(min + 366*86400000, ...dates);
  const x = d => 185+(Date.parse(d)-min)/(max-min)*650;
  const svg = svgRoot('timeline',1000,Math.max(120,rows.length*53+52),'Datas históricas por episódio; datas completas também disponíveis na tabela abaixo.');
  if(!rows.length) {svg.append(svgEl('text',{x:20,y:65},'Nenhum episódio no recorte.'));return;}
  rows.forEach((r,i) => {
    const y = 24+i*53;
    svg.append(svgEl('text',{x:0,y:y+4,class:'value'},`${companyName(r.empresa)} · ${r.episodio}`));
    if(r.pedido) {
      const start = x(r.pedido);
      if(r.encerramento) {
        const end = x(r.encerramento);
        svg.append(svgEl('line',{x1:start,x2:end,y1:y,y2:y,stroke:'#8eb699','stroke-width':5}));
        const point = svgEl('circle',{cx:end,cy:y,r:5,fill:'#8b7526'});
        point.append(svgEl('title',{},`Encerramento reportado: ${fmtDate(r.encerramento)}`));
        svg.append(point,svgEl('text',{x:end,y:y+21,'text-anchor':'end',class:'tick'},fmtDate(r.encerramento)));
      } else svg.append(svgEl('text',{x:Math.min(850,start+12),y:y+4,class:'tick'},'Encerramento não definido'));
      const point = svgEl('circle',{cx:start,cy:y,r:5,fill:'#19634c'});
      point.append(svgEl('title',{},`Pedido: ${fmtDate(r.pedido)}`));
      svg.append(point,svgEl('text',{x:start,y:y+21,class:'tick'},fmtDate(r.pedido)));
    } else svg.append(svgEl('text',{x:185,y:y+4},'Pedido sem data completa'));
  });
}
function renderDetails(rows) {
  const ids = new Set(rows.map(r => r.id));
  $('pending').replaceChildren(); $('evidence').replaceChildren();
  data.pendencias.filter(p => ids.has(p.id)).forEach(p => {
    const item = element('div',undefined,'detail-item');
    item.append(element('h3',`${p.id} · ${companyName(p.empresa)}`));
    const ul = element('ul'); p.pendencias.split('; ').forEach(t => ul.append(element('li',t)));
    item.append(ul); $('pending').append(item);
  });
  const sourceMap = new Map(data.fontes.map(s => [s.id,s]));
  rows.forEach(r => {
    const details = element('details'); details.append(element('summary',`${r.id} · ${companyName(r.empresa)} · ${r.fontes.length} fontes`));
    details.append(element('p',r.observacao));
    r.fontes.forEach(id => {
      const source = sourceMap.get(id); if(!source) return;
      const p = element('p'), a = element('a',`${id} · ${source.titulo}`);
      const url = new URL(source.url); if(['http:','https:'].includes(url.protocol)) a.href = url.href;
      a.target = '_blank'; a.rel = 'noopener noreferrer'; p.append(a); details.append(p);
    });
    data.evidencias.filter(e => e.episodio_id === r.id).forEach(e => {
      const p = element('p',`${e.campo}: ${e.valor} · ${e.fonte_id} · ${e.localizacao} · consulta ${fmtDate(e.consulta)}${e.situacao === 'alternativa_pendente' ? ' · ALTERNATIVA PENDENTE' : ''}`);
      if(e.situacao === 'alternativa_pendente') p.className = 'alternative';
      details.append(p);
    });
    $('evidence').append(details);
  });
}
function render() {
  const rows = data.registros.filter(r => (!$('company').value || r.empresa === $('company').value) && (!$('year').value || String(r.ano_pedido) === $('year').value));
  selectedRows = rows;
  $('scope').textContent = `${rows.length} de ${data.registros.length} episódios no recorte`;
  const evidence = data.evidencias.filter(e => rows.some(r => r.id === e.episodio_id) && e.situacao === 'incorporada');
  const cards = [
    ['Companhias pesquisadas',new Set(rows.map(r => r.empresa)).size,'Nomes distintos no recorte'],
    ['Episódios identificados',rows.length,'Participações em processos'],
    ['Evidências incorporadas',evidence.length,'Registros por campo e fonte'],
    ['Status não auditados',rows.filter(r => r.status_no_corte === 'nao_auditado').length,'Situação no corte ainda pendente']
  ];
  $('cards').replaceChildren();
  cards.forEach(([label,value,note]) => {const card=element('article',undefined,'card');card.append(element('span',label),element('strong',String(value)),element('small',note));$('cards').append(card);});
  renderYears(rows); renderQuality(rows); renderTimeline(rows);
  $('records').replaceChildren(); $('empty').hidden = rows.length !== 0;
  rows.forEach(r => {
    const tr = element('tr'), company = element('td');
    company.append(element('strong',companyName(r.empresa)),element('small',`${r.id} · episódio ${r.episodio}`));
    tr.append(company);
    [r.cnpj || 'Não identificado', fmtDate(r.pedido), fmtDate(r.encerramento), r.processo || 'Não identificado'].forEach(value => tr.append(element('td',value)));
    const status = element('td'); status.append(element('span','Não auditado','status'));tr.append(status);$('records').append(tr);
  });
  renderDetails(rows);
}
async function load() {
  const company = $('company').value, year = $('year').value;
  $('reload').disabled = true;
  try {
    const response = await fetch('/api/dados',{cache:'no-store'}), result = await response.json();
    if(!response.ok) throw new Error(result.erro || 'Não foi possível ler a base.');
    data = result;
    $('cutoff').textContent = fmtDate(data.corte); $('coverage').textContent = `Cobertura: ${data.cobertura}`;
    $('company').replaceChildren(element('option','Todas as companhias'));$('company').firstChild.value='';
    [...new Set(data.registros.map(r => r.empresa))].sort().forEach(name => {const option=element('option',companyName(name));option.value=name;$('company').append(option);});
    $('year').replaceChildren(element('option','Todos os anos'));$('year').firstChild.value='';
    [...new Set(data.registros.map(r => r.ano_pedido).filter(v => v !== null))].sort().forEach(year => {const option=element('option',String(year));option.value=String(year);$('year').append(option);});
    $('company').value = [...$('company').options].some(o => o.value===company) ? company : '';
    $('year').value = [...$('year').options].some(o => o.value===year) ? year : '';
    $('error').hidden = true; render();
  } catch(error) {
    $('error').textContent = `Não foi possível atualizar o painel: ${error.message}${data ? ' Os dados exibidos pertencem à última leitura válida.' : ''}`;
    $('error').hidden = false;
  } finally {$('reload').disabled = false;}
}
$('company').addEventListener('change',render);$('year').addEventListener('change',render);
$('reset').addEventListener('click',() => {if(!data)return;$('company').value='';$('year').value='';render();});
$('reload').addEventListener('click',load);
$('download').addEventListener('click',() => {
  if(!data) return;
  const fields=['id','empresa','episodio','cnpj','pedido','encerramento','processo','status_no_corte'];
  const cell = value => {let text=String(value ?? '');if(/^[=+@\-\t\r]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';};
  const csv = [fields,...selectedRows.map(r => fields.map(k => r[k]))].map(row => row.map(cell).join(';')).join('\r\n');
  const url=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'}));
  const link=element('a');link.href=url;link.download='recuperacao-em-foco-recorte.csv';link.click();setTimeout(() => URL.revokeObjectURL(url),1000);
});
load();
