
    a.click();
  });
}

function carregarExcelJSAloc(cb){
  if(typeof ExcelJS!=='undefined'){cb();return;}
  const s=document.createElement('script');
  s.src='https://cdnjs.cloudflare.com/ajax/libs/exceljs/4.3.0/exceljs.min.js';
  s.onload=cb; document.head.appendChild(s);
}

// ── MOTOR DE ALOCAÇÃO ─────────────────────────────────────────────────
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

async function p