const SALA_INDIVIDUAL = ['LEDOR','TRANSCRITOR','SOFTWARE','SALA INDIVIDUAL','LIBRAS'];
const MESMA_SALA_GRUPO = ['PROVA AMPLIADA','SALA AMAMENTAÇÃO','TEMPO ADICIONAL','APÓS AS 18H','APÓS 18H'];
const SEM_RESTRICAO = ['CADEIRA SEPARADA','CADEIRA CANHOTO','APOIO DE PÉ','PRÓTESE AUDITIVA','BOMBA DE INSULINA'];

function abreviarAtendimento(nome){
  const map = {
    'LEDOR':'ledor','TRANSCRITOR':'transc','SOFTWARE':'software','SALA INDIVIDUAL':'individual','LIBRAS':'libras',
    'PROVA AMPLIADA':'ampliada','SALA AMAMENTAÇÃO':'amamentação','TEMPO ADICIONAL':'15min','APÓS AS 18H':'18h','APÓS 18H':'18h',
    'CADEIRA SEPARADA':'cad.sep','CADEIRA CANHOTO':'canhoto','APOIO DE PÉ':'apoio pé','PRÓTESE AUDITIVA':'prótese aud','BOMBA DE INSULINA':'insulina'
  };
  return map[nome.toUpperCase()] || nome.toLowerCase();
}

async function processarAlocacao(input){
  const file = input.files[0];
  if(!file) return;
  const statusEl = document.getElementById('aloc-processamento-status');
  statusEl.innerHTML = '<div class="loading"><div class="spinner"></div>Processando alocação...</div>';

  const enviadas = (window._alocEscolas||[]).filter(e=>e._status?.enviado);
  if(!enviadas.length){
    statusEl.innerHTML = '<div style="color:#c0322f;padding:10px">Nenhuma escola com formulário enviado. Impossível gerar alocação.</div>';
    return;
  }

  carregarSheetJSAloc(()=>{
    carregarExcelJSAloc(async ()=>{
      try{
        const reader = new FileReader();
        reader.onload = async (e)=>{
          const wb = XLSX.read(e.target.result, {type:'binary', cellDates:true});
          let candidatos = [];
          for(const nome of wb.SheetNames){
            const rows = XLSX.utils.sheet_to_json(wb.Sheets[nome], {defval:'', range:1});
            candidatos = candidatos.concat(rows);
          }
          candidatos = candidatos.map(r=>{
            const n={};
            Object.keys(r).forEach(k=>{ n[k.trim()]=typeof r[k]==='string'?r[k].trim():r[k]; });
            return n;
          });

          if(!candidatos.length){
            statusEl.innerHTML = '<div style="color:#c0322f;padding:10px">Nenhum candidato encontrado na planilha.</div>';
            return;
          }

          const resultado = executarMotorAlocacao(candidatos, enviadas);
          await gerarPlanilhaAlocacao(resultado);

          statusEl.innerHTML = `<div style="background:#e4f3ea;border:1px solid #a8dbb8;border-radius:9px;padding:12px 16px;font-size:13px;color:#2e7d52;font-weight:600">
            ✅ Alocação gerada! ${resultado.alocados.length} candidatos alocados
            ${resultado.naoAlocados.length ? ` · ⚠️ ${resultado.naoAlocados.length} não alocados (capacidade insuficiente)` : ''}
          </div>`;
        };
        reader.readAsBinaryString(file);
      }catch(err){
        statusEl.innerHTML = `<div style="color:#c0322f;padding:10px">Erro: ${err.message}</div>`;
      }
    });
  });
}

function carregarSheetJSAloc(cb){
  if(typeof XLSX!=='undefined'){cb();return;}
  const s=document.createElement('script');
  s.src='https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js';
  s.onload=cb; document.head.appendChild(s);
}

function salaEhTerrea(andarRaw){
  let andar = String(andarRaw==null?'':andarRaw).toUpperCase();
  andar = andar.normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  andar = andar.replace(/°/g,'º').trim();
  if(andar==='0') return true;
  if(andar.includes('TERREO')) return true;
  if(/^1\s*[ºO]?\s*ANDAR$/.test(andar)) return true;
  return false;
}

function executarMotorAlocacao(candidatos, escolas){
  // ── 1. Montar pool de salas de todas as escolas, ordenado por capacidade desc ──
  let salasPool = [];
  escolas.forEach(esc=>{
    const nomeEsc = esc.instituicao?.nome || esc.concurso?.escola || esc.token;
    (esc.salas||[]).forEach(s=>{
      salasPool.push({
        escola: nomeEsc, bloco: s.bloco||'', andar: (s.andar===undefined||s.andar===null) ? '' : String(s.andar),
        salaBase: s.sala||'', capacidadeOriginal: parseInt(s.capacidade)||0,
        capacidadeDisponivel: parseInt(s.capacidade)||0,
        turno: s.turno||'AMBOS', ocupantes: []
      });
    });
  });
  // Ordenar por capacidade desc (maior primeiro)
  salasPool.sort((a,b)=>b.capacidadeOriginal - a.capacidadeOriginal);

  // ── 2. Identificar atendimento especial de cada candidato ──
  function getAtendimentos(c){
    const campo = (c['ATENDIMENTO ESPECIAL']||c['CONDIÇÃO ESPECIAL']||c['ATENDIMENTOS']||'').toString().toUpperCase();
    if(!campo || campo==='NÃO'||campo==='NAO'||campo==='-') return [];
    return campo.split(/[,;]/).map(s=>s.trim()).filter(Boolean);
  }
  function precisaSalaIndividual(atendimentos){
    return atendimentos.some(a=>SALA_INDIVIDUAL.some(k=>a.toUpperCase().includes(k)));
  }
  function precisaTerreo(c){
    const t = (c['SALA TÉRREA']||c['TERREO']||'').toString().toUpperCase();
    return t==='SIM'||t==='S';
  }

  // ── 3. Ordenar candidatos: maior código cargo → CPF → alfabético ──
  candidatos.forEach(c=>{
    c._codNum = parseInt((c['CÓDIGO']||c['CODIGO']||'0').toString().replace(/\D/g,'')) || 0;
    c._cpf = (c['CPF']||'').toString().replace(/\D/g,'');
    c._atendimentos = getAtendimentos(c);
    c._individual = precisaSalaIndividual(c._atendimentos);
    c._terreo = precisaTerreo(c);
  });
  candidatos.sort((a,b)=>
    b._codNum - a._codNum ||
    a._cpf.localeCompare(b._cpf) ||
    (a['CANDIDATO']||'').localeCompare(b['CANDIDATO']||'')
  );

  const alocados = [];
  const naoAlocados = [];
  const salasIndividuaisUsadas = new Set();

  // ── 4. Alocar candidatos de sala individual primeiro ──
  const individuais = candidatos.filter(c=>c._individual);
  const demais = candidatos.filter(c=>!c._individual);

  individuais.forEach(c=>{
    // Buscar sala livre (preferência: térrea se necessário)
    let salaEscolhida = null;
    // Preferir sala dedicada (capacidade original = 1) quando exigido atendimento individual
    salaEscolhida = salasPool.find(s => s.capacidadeOriginal === 1 && s.capacidadeDisponivel >= 1 && (!c._terreo || salaEhTerrea(s.andar)));
    // Fallback: sem sala dedicada disponível, usa qualquer sala com vaga (respeitando térreo)
    if(!salaEscolhida){
      salaEscolhida = salasPool.find(s => s.capacidadeDisponivel >= 1 && (!c._terreo || salaEhTerrea(s.andar)));
    }
    if(salaEscolhida){
      salaEscolhida.capacidadeDisponivel -= 1;
      const abrevs = c._atendimentos.filter(a=>SALA_INDIVIDUAL.some(k=>a.toUpperCase().includes(k))).map(abreviarAtendimento);
      const nomeSalaFinal = `${salaEscolhida.salaBase} ${abrevs.join(', ')}`;
      alocados.push({
        ...mapCandidato(c),
        SALA: nomeSalaFinal, ANDAR: salaEscolhida.andar, BLOCO: salaEscolhida.bloco, ESCOLA: salaEscolhida.escola,
        _tipoSala: 'individual'
      });
      salaEscolhida.ocupantes.push(c);
    } else {
      naoAlocados.push(mapCandidato(c));
    }
  });

  // ── 5. Alocar demais candidatos em ordem, preenchendo salas de maior p/ menor ──
  let salaAtualIdx = 0;
  demais.forEach(c=>{
    let salaEscolhida = null;
    // Se precisa térreo, buscar entre as com capacidade
    if(c._terreo){
      salaEscolhida = salasPool.find(s=>
        s.capacidadeDisponivel > 0 && salaEhTerrea(s.andar)
      );
    }
    if(!salaEscolhida){
      // Pegar a sala atual com espaço (segue ordem, maior capacidade primeiro)
      while(salaAtualIdx < salasPool.length && salasPool[salaAtualIdx].capacidadeDisponivel <= 0){
        salaAtualIdx++;
      }
      if(salaAtualIdx < salasPool.length) salaEscolhida = salasPool[salaAtualIdx];
    }

    if(salaEscolhida){
      salaEscolhida.capacidadeDisponivel -= 1;
      let nomeSalaFinal = salaEscolhida.salaBase;
      // Se tem atendimento "mesma sala do grupo", adicionar abreviação
      const abrevsGrupo = c._atendimentos.filter(a=>MESMA_SALA_GRUPO.some(k=>a.toUpperCase().includes(k))).map(abreviarAtendimento);
      if(abrevsGrupo.length) nomeSalaFinal = `${salaEscolhida.salaBase} ${abrevsGrupo.join(', ')}`;
      alocados.push({
        ...mapCandidato(c),
        SALA: nomeSalaFinal, ANDAR: salaEscolhida.andar, BLOCO: salaEscolhida.bloco, ESCOLA: salaEscolhida.escola,
        _tipoSala: 'grupo'
      });
      salaEscolhida.ocupantes.push(c);
    } else {
      naoAlocados.push(mapCandidato(c));
    }
  });

  return {alocados, naoAlocados, salasPool};
}

function mapCandidato(c){
  return {
    INSCRIÇÃO: c['INSCRIÇÃO']||'', CANDIDATO: c['CANDIDATO']||'', CPF: c['CPF']||'',
    CONCURSO: c['CONCURSO']||'', CÓDIGO: c['CÓDIGO']||c['CODIGO']||'', CARGO: c['CARGO']||'',
    'DATA PROVA': c['DATA REALIZAÇÃO PROVA']||c['DATA PROVA']||'', TURNO: c['TURNO']||''
  };
}


module.exports={executarMotorAlocacao,SALA_INDIVIDUAL,MESMA_SALA_GRUPO,SEM_RESTRICAO,abreviarAtendimento,salaEhTerrea};