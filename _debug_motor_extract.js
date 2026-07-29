rocessarAlocacao(input){
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

function executarMotorAlocacao(candidatos, escolas){
  // ── 1. Montar pool de salas de todas as escolas, ordenado por capacidade desc ──
  let salasPool = [];
  escolas.forEach(esc=>{
    const nomeEsc = esc.instituicao?.nome || esc.concurso?.escola || esc.token;
    (esc.salas||[]).forEach(s=>{
      salasPool.push({
        escola: nomeEsc, bloco: s.bloco||'', andar: s.andar||'',
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
    for(const sala of salasPool){
      const keyIndiv = sala.escola+'|'+sala.salaBase+'|IND'+salasIndividuaisUsadas.size;
      if(c._terreo && !sala.andar.toUpperCase().includes('TÉRREO') && !sala.andar.toUpperCase().includes('TERREO') && sala.andar !== '0' && sala.andar !== '1º Andar') continue;
      if(sala.capacidadeDisponivel >= 1){
        salaEscolhida = sala;
        break;
      }
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
        s.capacidadeDisponivel > 0 &&
        (s.andar.toUpperCase().includes('TÉRREO')||s.andar.toUpperCase().includes('TERREO')||s.andar==='0'||s.andar==='1º Andar')
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

async function gerarPlanilhaAlocacao(resultado){
  const wb = new ExcelJS.Workbook();
  const FONTE='Times New Roman';
  const BORDA={top:{style:'thin',color:{argb:'FF000000'}},bottom:{style:'thin',color:{argb:'FF000000'}},left:{style:'thin',color:{argb:'FF000000'}},right:{style:'thin',color:{argb:'FF000000'}}};

  function criarAba(nome, dados, cols){
    if(!dados.length) return;
    const ws = wb.addWorksheet(nome);
    const LARG = {'INSCRIÇÃO':12,'CANDIDATO':32,'CPF':14,'CONCURSO':40,'CÓDIGO':8,'CARGO':40,
      'DATA PROVA':16,'TURNO':10,'SALA':16,'ANDAR':12,'BLOCO':10,'ESCOLA':32};
    cols.forEach((c,ci)=>{
      const cell = ws.getCell(1,ci+1);
      cell.value = c;
      cell.font = {bold:true,color:{argb:'FFFFFFFF'},name:FONTE,size:9};
      cell.fill = {type:'pattern',pattern:'solid',fgColor:{argb:'FF1F4E8C'}};
      cell.alignment = {horizontal:'center',vertical:'middle'};
      cell.border = BORDA;
      ws.getColumn(ci+1).width = LARG[c]||14;
    });
    ws.getRow(1).height = 22;
    let corIdx=0, escolaAtual='';
    dados.forEach((row,ri)=>{
      if(row.ESCOLA !== escolaAtual){ escolaAtual = row.ESCOLA; corIdx=(corIdx+1)%2; }
      const cor = corIdx===0?'FFFFFFFF':'FFF0F4FF';
      cols.forEach((c,ci)=>{
        const cell = ws.getCell(ri+2,ci+1);
        cell.value = String(row[c]??'');
        cell.font = {name:FONTE,size:9};
        cell.fill = {type:'pattern',pattern:'solid',fgColor:{argb:cor}};
        cell.alignment = {vertical:'middle'};
        cell.border = BORDA;
      });
    });
    ws.views = [{state:'frozen',xSplit:0,ySplit:1}];
  }

  const colsAlocados = ['INSCRIÇÃO','CANDIDATO','CPF','CONCURSO','CÓDIGO','CARGO','DATA PROVA','TURNO','SALA','ANDAR','BLOCO','ESCOLA'];
  criarAba('ALOCAÇÃO', resultado.alocados, colsAlocados);

  if(resultado.naoAlocados.length){
    const colsNaoAloc = ['INSCRIÇÃO','CANDIDATO','CPF','CONCURSO','CÓDIGO','CARGO','DATA PROVA','TURNO'];
    criarAba('NÃO ALOCADOS', resultado.naoAlocados, colsNaoAloc);
  }

  const buf = await wb.xlsx.writeBuffer();
  const blob = new Blob([buf],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'ALOCACAO_CANDIDATOS.xlsx';
  a.click();
}

// ── REFRESH ──────────────────────────────────────────────────────────
async function refreshAll(){
  const btn=document.getElementById('refresh-btn');
  if(btn){ btn.classList.add('spinning'); btn.disabled=true; }

  try {
    // Busca tarefas diretamente da API Graph (sem depender do Python)
    // 1. Achar o plano
    if(!_planoId){
      const grps = await apiAll('https://graph.microsoft.com/v1.0/me/memberOf?$top=50');
      for(const g of grps){
        if(!g.id) continue;
        try{
          const plans = await api(`https://graph.microsoft.com/v1.0/groups/${g.id}/planner/plans`);
          for(const p of(plans.value||[])){
            if(p.title.toUpperCase().includes('PLANNER IBGP')){ _planoId=p.id; break; }
          }
        }catch(e){}
        if(_planoId) break;
      }
    }
    if(!_planoId){ alert('Plano não encontrado.'); return; }

    // 2. Buckets
    const bd = await api(`https://graph.microsoft.com/v1.0/planner/plans/${_planoId}/buckets`);
    _buckets = {};
    (bd.value||[]).forEach(b=>_buckets[b.id]=b.name);

    // 3. Tarefas abertas
    const rawTasks = await apiAll(`https://graph.microsoft.com/v1.0/planner/plans/${_planoId}/tasks`);
    const ATRIB = typeof ATRIBUICOES_JS!=='undefined'?ATRIBUICOES_JS:{};
    const novas = [];
    for(const t of rawTasks){
      if(t.percentComplete===100) continue;
      const nome=(t.title||'').trim();
      const resp=ATRIB[nome]; if(!resp) continue;
      novas.push({
        id:t.id,
        municipio:_buckets[t.bucketId]||'—',
        tarefa:nome,
        responsavel:resp,
        due:t.dueDateTime||'',
      });
    }

    // 4. Atualiza DADOS_INICIAIS e recarrega
    DADOS_INICIAIS.tarefas = novas;
    DADOS_INICIAIS.buckets = _buckets;
    // Buscar TODAS as concluídas (histórico completo, usado na Agenda)
    const rawConcl = await apiAll(`https://graph.microsoft.com/v1.0/planner/plans/${_planoId}/tasks?$filter=percentComplete eq 100`).catch(()=>[]);
    _concluidasTodas = rawConcl
      .filter(t=>ATRIB[(t.title||'').trim()])
      .map(t=>({
        id:t.id, municipio:_buckets[t.bucketId]||'—',
        tarefa:(t.title||'').trim(), responsavel:ATRIB[(t.title||'').trim()]||'',
        due:t.dueDateTime||'', completedAt:t.completedDateTime||'', concluida:true,
      }));
    // Concluídas nas últimas 48h, para o painel de sessão
    const limite = new Date(Date.now() - 48*3600*1000);
    _concluidasSessao = _concluidasTodas
      .filter(t=>t.completedAt && new Date(t.completedAt)>=limite)
      .sort((a,b)=>b.completedAt.localeCompare(a.completedAt))
      .slice(0,30)
      .map(t=>({...t, fromPlanner:true}));
    _allTasks = [];
    loadTarefas();
    renderConcluidas();
    addMov('Tarefas atualizadas do Planner', '#2e7d52');
    addNotif('🔄 Tarefas atualizadas com sucesso!');
  } catch(e){
    alert('Erro ao atualizar: '+e.message);
  } finally {
    setTimeout(()=>{ btn?.classList.remove('spinning'); btn && (btn.disabled=false); }, 600);
  }
}

// ── INIT ──────────────────────────────────────────────────────────────
// Preencher nome do usuário no topbar e sidebar
(function(){
  const nome = typeof NOME_USUARIO!=='undefined' ? NOME_USUARIO : 'Usuário';
  const isG  = typeof IS_GESTORA!=='undefined' && IS_GESTORA;
  const isCr = typeof IS_CRONOGRAMA!=='undefined' && IS_CRONOGRAMA;
  const perfil = isG ? 'Gestora · Equipe IBGP' : isCr ? 'Cronograma · IBGP' : 'Equipe IBGP';
  const inicial = nome.charAt(0).toUpperCase();
  const spanNome = document.getElementById('span-nome-usuario');
  if(spanNome) spanNome.textContent = nome;
  const av = document.getElementById('user-avatar');
  if(av) av.textContent = inicial;
  const nd = document.getElementById('user-name-display');
  if(nd) nd.textContent = nome;
  const rd = document.getElementById('user-role-display');
  if(rd) rd.textContent = perfil;
})();

// Carregar usuários do DADOS_INICIAIS
if(typeof DADOS_INICIAIS!=='undefined' && DADOS_INICIAIS.usuarios){
  _usuarios = DADOS_INICIAIS.usuarios;
}
renderUsuariosMsgInicial();

renderPhases();
renderNotifs();
renderCronResult();
if(typeof IS_CRONOGRAMA!=='undefined'&&IS_CRONOGRAMA){
  document.querySelector('[data-page="tarefas"]')?.style && (document.querySelector('[data-page="tarefas"]').style.display='none');
  document.querySelector('[data-page="dashboard"]')?.style && (document.querySelector('[data-page="dashboard"]').style.display='none');
  goPage('validar');
} else if(typeof IS_OPERACIONAL!=='undefined'&&IS_OPERACIONAL){
  // Operacional: esconde menus que não são dele
  ['validar','gerar','reajustar','indicadores','concluidas','usuarios','equipes','config'].forEach(id=>{
    const btn=document.querySelector(`[data-page="${id}"]`);
    if(btn) btn.style.display='none';
  });
  goPage('dashboard');
} else {
  loadTarefas();
  renderConcluidas();
}
</script>