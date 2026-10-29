/* Motor de cronograma IBGP — movido por tabela de regras (cronograma_regras_v2.json).
   Substitui calcularConcurso / calcularPSS / calcularGuarda. Roda no navegador e no Node. */
(function(root){
'use strict';
const DOW={domingo:0,segunda:1,'terça':2,quarta:3,quinta:4,sexta:5,'sábado':6};
const sod=d=>new Date(d.getFullYear(),d.getMonth(),d.getDate());
const addDays=(d,n)=>{const r=sod(d); r.setDate(r.getDate()+n); return r;};
const dk=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
function pascoa(y){const a=y%19,b=Math.floor(y/100),c=y%100,d=Math.floor(b/4),e=b%4,f=Math.floor((b+8)/25),g=Math.floor((b-f+1)/3),
  h=(19*a+b-d-g+15)%30,i=Math.floor(c/4),k=c%4,l=(32+2*e+2*i-h-k)%7,m=Math.floor((a+11*h+22*l)/451),
  mes=Math.floor((h+l-7*m+114)/31),dia=((h+l-7*m+114)%31)+1; return new Date(y,mes-1,dia);}

/* ── CALENDÁRIO ─────────────────────────────────────────────────────────────
   Dia útil = segunda a sexta, exceto feriados nacionais, Sexta-feira da Paixão, feriados estaduais/municipais
   informados, pontos facultativos marcados (Carnaval, Corpus Christi, Cinzas) e o recesso de 20/12 a 05/01. */
class Calendario{
  constructor(o){ this.o=Object.assign({carnaval:true,corpusChristi:true,cinzas:false,recesso:true,estaduais:[],municipais:[]},o||{}); this.cache={}; this.locais=this._ler([].concat(this.o.estaduais,this.o.municipais)); }
  _ler(lista){ return lista.map(s=>{ s=String(s).trim(); let m;
      if((m=s.match(/^(\d{4})-(\d{2})-(\d{2})$/))) return {y:+m[1],m:+m[2],d:+m[3]};
      if((m=s.match(/^(\d{2})\/(\d{2})\/(\d{4})$/))) return {y:+m[3],m:+m[2],d:+m[1]};
      if((m=s.match(/^(\d{2})\/(\d{2})$/))) return {m:+m[2],d:+m[1]};          // DD/MM = todo ano
      throw new Error('Feriado local em formato inválido: '+s); }); }
  feriadosAno(y){ if(this.cache[y]) return this.cache[y]; const S=new Set(), add=(m,d)=>S.add(dk(new Date(y,m-1,d)));
    [[1,1],[4,21],[5,1],[9,7],[10,12],[11,2],[11,15],[11,20],[12,25]].forEach(([m,d])=>add(m,d));          // nacionais
    const P=pascoa(y); S.add(dk(addDays(P,-2)));                                                                // Sexta-feira da Paixão
    if(this.o.carnaval){ S.add(dk(addDays(P,-48))); S.add(dk(addDays(P,-47))); }
    if(this.o.cinzas) S.add(dk(addDays(P,-46)));
    if(this.o.corpusChristi) S.add(dk(addDays(P,60)));
    this.locais.forEach(f=>{ if(f.y===undefined||f.y===y) add(f.m,f.d); });
    return this.cache[y]=S; }
  isFeriado(d){ return this.feriadosAno(d.getFullYear()).has(dk(d)); }
  isRecesso(d){ if(!this.o.recesso) return false; const m=d.getMonth()+1,x=d.getDate(); return (m===12&&x>=20)||(m===1&&x<=5); }
  isUtil(d){ const w=d.getDay(); return w!==0&&w!==6&&!this.isFeriado(d)&&!this.isRecesso(d); }
  proxUtil(d){ let r=sod(d); while(!this.isUtil(r)) r=addDays(r,1); return r; }           // o próprio dia, se útil
  antUtil(d){ let r=sod(d); while(!this.isUtil(r)) r=addDays(r,-1); return r; }
  proxUtilApos(d){ return this.proxUtil(addDays(d,1)); }                                 // 1º dia útil seguinte
  addDU(d,n){ let r=sod(d),c=0; while(c<n){ r=addDays(r,1); if(this.isUtil(r)) c++; } return r; }
}
const proxDowApos=(d,w)=>{ let r=addDays(d,1); while(r.getDay()!==w) r=addDays(r,1); return r; };   // 1ª data > d com esse dia da semana
const prevDowAntes=(d,w)=>{ let r=addDays(d,-1); while(r.getDay()!==w) r=addDays(r,-1); return r; };
const primeiraDataComDow=(d,fn)=>{ let r=sod(d); while(!fn(r.getDay())) r=addDays(r,1); return r; };

/* ── MOTOR ──────────────────────────────────────────────────────────────── */
const TIPOS_COL_C=['CONCURSO','GUARDA','PSP'], TIPOS_CONC=['CONCURSO','PSS','PSP'];
function gerar(cfg,REGRAS){
  const cal=new Calendario(cfg.feriados), avisos=[], F=cfg.fases||{};
  const tipo=cfg.tipo||'CONCURSO', col=TIPOS_COL_C.includes(tipo)?'C':'D', grade=tipo==='GUARDA'?'guarda':'conc';
  const aplica=a=>a.aplicavel==='Todos'||(a.aplicavel==='Guarda'&&tipo==='GUARDA')||(a.aplicavel==='Concurso + PSS + PSP'&&TIPOS_CONC.includes(tipo));
  const faseOn=a=>{ switch(a.fase){
      case 'base': case 'guarda_classif': return true;
      case 'pre_edital': return !!F.pre_edital && !!cfg.dataEscopo;
      case 'adaptacao': return !!F.pratica && F.adaptacao!==false;
      case 'curso_intro': case 'curso_guarda': return !!F.curso;
      default: return !!F[a.fase]; } };
  const extra=a=>{ if(a.linha===98) return cfg.modalidadeHetero==='online';
      if(a.linha>=132&&a.linha<=138) return cfg.incluirExcedentes!==false;
      if(a.linha===140) return cfg.aulaMagna!==false; return true; };
  const ativ=REGRAS.filter(a=>aplica(a)&&faseOn(a)&&extra(a));
  const pos={}; ativ.forEach((a,i)=>pos[a.linha]=i);
  const memo={}, pilha=new Set(); const regraDe=a=>a.regras[col]||a.regras.C;
  const get=l=>{ if(memo[l]) return memo[l]; if(pilha.has(l)) throw new Error('Dependência circular em L'+l);
      pilha.add(l); const r=avaliar(ativ[pos[l]]); pilha.delete(l); return memo[l]=r; };
  const ne=(a,g)=> (cfg.duracoes&&cfg.duracoes[a.linha])||(a.linha===8&&cfg.diasIsencao)||(a.linha===9&&cfg.diasInscricao)||g.n;
  const RE={RES_POS_ANT:/^(resultado pós-recurso|resultado após recurso|publicação do resultado pós|classificação final)/i,
            RES_PRELIM_ANT:/^(resultado preliminar|publicação da classificação|classificação preliminar|gabarito preliminar)/i};
  function refLinha(kw,a,g){
    if(RE[kw]){ for(let i=pos[a.linha]-1;i>=0;i--) if(ativ[i].fase!=='adaptacao'&&RE[kw].test(ativ[i].nome)) return ativ[i].linha;   // a adaptação PcD é trilha paralela: não conta como "etapa anterior"
      avisos.push(`L${a.linha}: não achei a "etapa anterior" (${kw})`); return null; }
    if(kw==='PROVA_FINAL_CURSO') return 141;
    if(kw==='HOMOLOG_BASE') return (grade==='guarda'&&(149 in pos))?149:118;      // Guarda com curso → resultado final do curso; demais → Classificação Final
    const rl=g.ref_linhas&&g.ref_linhas[kw]; const l=rl?rl[grade]:null;
    if(l==null){ avisos.push(`L${a.linha}: referência ${kw} sem atividade correspondente`); return null; }
    return (l in pos)?l:-l;                       // negativo = a atividade referida está desligada
  }
  const ant=a=>ativ[pos[a.linha]-1];
  function avaliarRegra(a,g){
    const manual=cfg.manuais&&cfg.manuais[a.linha];
    if(manual){ const i=sod(manual.ini||manual.fim), f=sod(manual.fim||manual.ini); return {ini:i,fim:f}; }
    const R=kw=>{ const l=refLinha(kw,a,g); if(l==null) throw new Error(`L${a.linha} (${a.nome}): referência ${kw} não encontrada`); return l; };
    switch(g.tipo){
      case 'MANUAL': { const d=a.linha===3?cfg.dataEscopo:(a.linha===7?cfg.dataPublicacaoEdital:null);
          if(!d) throw new Error(`Informe a data de "${a.nome}"`); const x=cal.proxUtil(sod(d)); return {ini:x,fim:x}; }
      case 'APOS': { const l=R(g.ref); if(l<0) throw new Error(`L${a.linha}: ${g.ref} desligada`); const P=get(l), n=ne(a,g);
          if(g.periodo_apos||a.formato_data==='periodo'){ const ini=cal.proxUtilApos(P.fim);
              return {ini,fim:g.un==='du'?cal.addDU(ini,n-1):cal.proxUtil(addDays(ini,n-1))}; }
          const d=g.un==='du'?cal.addDU(P.fim,n):cal.proxUtil(addDays(P.fim,n)); return {ini:d,fim:d}; }
      case 'SEG': { const l=R(g.ref); const P=get(Math.abs(l)); const d=cal.addDU(P.fim,g.ordn); return {ini:d,fim:d}; }
      case 'MESMO': { const l=R(g.ref);
          if(l<0){ const P=get(ant(a).linha); const d=cal.addDU(P.fim,1); return {ini:d,fim:d}; }   // referência desligada → fluxo normal
          const P=get(l); return {ini:P.fim,fim:P.fim}; }
      case 'DIA': return diaRel(a,g,R);
      case 'PERIODO': { const I=g.inicio; let ini;
          if(I.tipo==='APOS'&&I.ref==='PUB_ED'){ const pub=get(7).fim; ini=cal.proxUtil(cfg.inicioInscricoes?sod(cfg.inicioInscricoes):addDays(pub,I.n)); }
          else if(I.tipo==='SEG'){ const l=R(I.ref); ini=cal.addDU(get(Math.abs(l)).fim,I.ordn); }
          else if(I.tipo==='MESMO_INICIO'){ const l=R(I.ref); ini=l<0?cal.proxUtilApos(get(ant(a).linha).fim):get(l).ini; }
          const n=ne(a,g); return {ini,fim:g.un==='du'?cal.addDU(ini,n-1):cal.proxUtil(addDays(ini,n-1))}; }
      case 'DUR': { const P=get(ant(a).linha), n=ne(a,g); const ini=cal.proxUtilApos(P.fim);
          if(g.un==='du') return {ini,fim:cal.addDU(ini,n-1)};
          let fim=cal.proxUtil(addDays(P.fim,n)); if(fim<ini) fim=ini; return {ini,fim}; }
      case 'FDS': return fimDeSemana(a,g,R);
      case 'MODALIDADE': return avaliarRegra(a,cfg.modalidadeHetero==='online'?Object.assign({ref_linhas:g.ref_linhas},g.online):Object.assign({ref_linhas:g.ref_linhas},g.presencial));
      case 'CURSO_CH': return cursoCH(a,g,R);
    }
    throw new Error('Tipo de regra desconhecido: '+g.tipo);
  }
  const avaliar=a=>avaliarRegra(a,regraDe(a));
  function diaRel(a,g,R){
    const w=DOW[g.dow]; let base,d;
    if(g.ref==='CURSO_FIM'){ const P=get(R(g.ref)); d=proxDowApos(P.fim,0); return {ini:d,fim:d}; }
    const lr=R(g.ref);
    if(g.dire==='seg'){ const P=lr<0?get(ant(a).linha):get(lr);
        const ajusta=x=>{ if(cal.isUtil(x)) return x; const fb=g.fallback;
          if(/^terça/.test(fb)) return cal.proxUtil(addDays(x,1));
          if(/^sexta/.test(fb)){ x=addDays(x,4); return cal.isUtil(x)?x:cal.antUtil(x); }
          if(/^quinta/.test(fb)){ x=addDays(x,-1); return cal.isUtil(x)?x:cal.antUtil(x); }
          return cal.proxUtil(x); };
        d=ajusta(proxDowApos(P.fim,w));
        if(a.linha===55&&pos[54]!==undefined){           // adaptação PcD: o resultado não pode ficar depois do início da Prova Prática;
          const ad=get(54).fim, op=cfg.fimDeSemanaEtapas||'sab_dom';   // a realização é o próximo fim de semana após a convocação, então a convocação é que espera
          const fds=c=>primeiraDataComDow(addDays(c,1),x=>op==='dom'?x===0:(op==='sab'?x===6:(x===6||x===0)));
          while(fds(d)<=ad) d=ajusta(proxDowApos(d,w)); }
        return {ini:d,fim:d}; }
    const P=get(Math.abs(lr)); d=prevDowAntes(P.ini,w);                    // dire==='ant': 1ª data antes do início do evento
    if(!cal.isUtil(d)){ d=/^sexta/.test(g.fallback)?addDays(d,-3):d; d=cal.antUtil(d); }
    return {ini:d,fim:d};
  }
  function fimDeSemana(a,g,R){
    let base;
    if(g.ref){ const P=get(Math.abs(R(g.ref))); base=addDays(P.fim,g.n===0?1:g.n); }
    else { // PSS/Certificação/Outros: data da prova informada pelo usuário
      if(cfg.dataProva) base=sod(cfg.dataProva);
      else { avisos.push(`L${a.linha}: data da prova não informada — usei 30 dias corridos após as inscrições`); base=addDays(get(9).fim,30); } }
    const op=a.linha===20?(cfg.haSabado?'sab_dom':'dom'):(cfg.fimDeSemanaEtapas||'sab_dom');
    let ds;
    if(op==='dom'){ const d=primeiraDataComDow(base,w=>w===0); ds=[d]; }
    else if(op==='sab'){ const d=primeiraDataComDow(base,w=>w===6); ds=[d]; }
    else { const d=primeiraDataComDow(base,w=>w===6||w===0); ds=d.getDay()===6?[d,addDays(d,1)]:[d]; }
    return {ini:ds[0],fim:ds[ds.length-1],datas:ds};
  }
  function cursoCH(a,g,R){
    const horas=cfg.cargaHoraria||40, hpd=cfg.horasPorDia||8, dias=Math.max(1,Math.ceil(horas/hpd)); let ini;
    if(g.ref==='CONVOC'){ const P=get(Math.abs(R('CONVOC'))); ini=cal.proxUtil(proxDowApos(P.fim,1)); }
    else if(pos[140]!==undefined){ ini=cal.addDU(get(140).fim,1); }
    else { const P=get(139); ini=cal.proxUtil(proxDowApos(P.fim,1)); }
    return {ini,fim:cal.addDU(ini,dias-1),dias};
  }
  const nomeAtiv=a=>{ let n=a.nome; const np=cfg.nomePratica||'Prova Prática/Prova de Capacidade Física';
      if(np!=='Prova Prática/Prova de Capacidade Física'){ n=n.replace(/Prova Prática\/Prova de Capacidade Física/g,np).replace(/Prova de Capacidade Física/g,np).replace(/prova de capacidade física/g,np.toLowerCase()); }
      if(a.linha===20) n=F.discursiva?'Prova Objetiva e Prova Discursiva':'Prova Objetiva';
      return n; };
  const tarefas=ativ.map((a,i)=>{ const r=get(a.linha); return {seq:i+1,linha:a.linha,fase:a.fase,atividade:nomeAtiv(a),nome_original:a.nome,
      data_inicio:r.ini,data_fim:r.fim,datas:r.datas||null,formato:a.formato_data,dia_semana:a.dia_semana,regra:regraDe(a).tipo,dias:r.dias}; });
  // ── conferências automáticas (viram avisos para a tela) ──
  const T=Object.fromEntries(tarefas.map(t=>[t.linha,t]));
  for(let i=1;i<tarefas.length;i++){ const p=tarefas[i-1],t=tarefas[i];
    if(p.fase===t.fase&&t.linha!==106&&t.data_inicio<p.data_inicio) avisos.push(`Ordem cronológica: "${t.atividade}" (${t.data_inicio.toLocaleDateString('pt-BR')}) ficou antes de "${p.atividade}" (${p.data_inicio.toLocaleDateString('pt-BR')}). Confira as regras dessa etapa.`); }
  if(T[54]&&T[56]&&T[54].data_fim>=T[56].data_inicio) avisos.push('O resultado pós-recurso da adaptação PcD ('+T[54].data_fim.toLocaleDateString('pt-BR')+') não pode ficar depois do início da Prova Prática ('+T[56].data_inicio.toLocaleDateString('pt-BR')+').');
  if(T[150]&&T[124]&&T[150].data_inicio<=T[124].data_fim) avisos.push('A Homologação ('+T[150].data_inicio.toLocaleDateString('pt-BR')+') sai antes do fim da Avaliação Biopsicossocial ('+T[124].data_fim.toLocaleDateString('pt-BR')+').');
  if(T[13]&&T[9]&&T[13].data_fim>T[9].data_fim) avisos.push('O resultado pós-recurso da isenção saiu depois do fim das inscrições (deve ser antes).');
  return {tarefas,avisos,cal};
}
const api={Calendario,gerar,pascoa,addDays,dk};
if(typeof module!=='undefined'&&module.exports) module.exports=api; else root.CronogramaMotor=api;
})(typeof window!=='undefined'?window:globalThis);
