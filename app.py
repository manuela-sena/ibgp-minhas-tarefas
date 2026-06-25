import streamlit as st
import requests
from datetime import datetime, date
from urllib.parse import urlencode

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CLIENT_ID     = "cf858739-80c5-4bf0-bc5c-6f5b0cefb70d"
TENANT_ID     = "e1362ab7-0546-4f12-9f44-0867415479b9"
REDIRECT_URI  = "https://ibgp-minhas-tarefas-jkdmypmipxemkvhh6c5vjv.streamlit.app/"
SCOPES        = "Tasks.ReadWrite Group.Read.All User.Read offline_access"
NOME_PLANO    = "PLANNER IBGP"
EQUIPE        = ["Lorena", "Laryssa", "Natália", "Manuela"]

# Mapeamento: nome no Microsoft 365 -> nome interno usado nas atribuições
NOME_MAP = {
    "execução": "Laryssa",
    "laryssa": "Laryssa",
    "lorena": "Lorena",
    "natália": "Natália",
    "natalia": "Natália",
    "manuela": "Manuela",
    "manu": "Manuela",
    "fabiano": "Fabiano",
    "fabiano costa barreiros": "Fabiano",
}

ATRIBUICOES = {
    'CLASSIFICAÇÃO FINAL': 'Manuela',
    'CLASSIFICAÇÃO FINAL (APENAS PARA OS CARGOS DA PROVA PRÁTICA)': 'Manuela',
    'CLASSIFICAÇÃO FINAL (EXCETO CARGOS DA PROVA PRÁTICA)': 'Manuela',
    'CLASSIFICAÇÃO PRELIMINAR': 'Manuela',
    'CLASSIFICAÇÃO PRELIMINAR - (EXCETO CARGOS DA PROVA PRÁTICA)': 'Manuela',
    'CLASSIFICAÇÃO PRELIMINAR -(APENAS PARA OS CARGOS DA PROVA PRÁTICA)': 'Manuela',
    'COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI)': 'Laryssa',
    'COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI) - PUBLICAÇÃO DO LOCAL DE PROVA': 'Laryssa',
    'COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI) - PUBLICAÇÃO DO LOCAL DE PROVA.': 'Laryssa',
    'COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI) - PUBLICAÇÃO DO LOCAL DE PROVAS.': 'Laryssa',
    'CONVOCAÇÃO AV. MÉD. PERICIAL MULTI/BIOPSICOSSOCIAL': 'Laryssa',
    'CONVOCAÇÃO CURSO FORMAÇÃO INTRODUTÓRIA BÁSICA': 'Laryssa',
    'CONVOCAÇÃO DE CANDIDATOS EXCEDENTES PARA MATRÍCULA DO CURSO DE FORMAÇÃO (SE HOUVER)': 'Natália',
    'CONVOCAÇÃO PARA A ENTREVISTA DEVOLUTIVA ON-LINE': 'Laryssa',
    'CONVOCAÇÃO PARA A PROVA PRÁTICA': 'Laryssa',
    'CONVOCAÇÃO PARA AVALIAÇÃO SOCIAL': 'Laryssa',
    'CONVOCAÇÃO PARA ENVIO DE DOCUMENTOS DA PROVA DE TÍTULOS': 'Natália',
    'CONVOCAÇÃO PARA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'CONVOCAÇÃO PARA O CURSO DE FORMAÇÃO': 'Natália',
    'CONVOCAÇÃO PARA O CURSO DE FORMAÇÃO E CAPACITAÇÃO': 'Natália',
    'CONVOCAÇÃO PARA O PROCEDIMENTO DE VERIFICAÇÃO DA VERACIDADE DA AUTODECLARAÇÃO': 'Laryssa',
    'CONVOCAÇÃO PARA PROVA DE TÍTULOS': 'Natália',
    'CONVOCAÇÃO PARA PROVA PRÁTICA': 'Laryssa',
    'CONVOCAÇÃO PARA REALIZAÇÃO DO CURSO DE FORMAÇÃO': 'Natália',
    'CONVOCAÇÃO PROCEDIMENTO HETEROIDENTIFICAÇÃO': 'Natália',
    'CONVOCAÇÃO PROCEDIMENTO HETEROIDENTIFICAÇÃO - ONLINE': 'Natália',
    'DISPONIBILIZAÇÃO DO COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI)': 'Laryssa',
    'DISPONIBILIZAÇÃO DO COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI) – PUBLICAÇÃO DO LOCAL DE PROVA': 'Laryssa',
    'ENVIAR PROVAS DISCURSIVAS PARA CORREÇÃO': 'Natália',
    'ENVIAR QUESTÕES PARA A BANCA': 'Natália',
    'ENVIAR QUESTÕES PROVA OBJETIVA PARA A BANCA': 'Natália',
    'ENVIAR QUESTÕES À BANCA': 'Natália',
    'GABARITO PRELIMINAR': 'Natália',
    'GABARITO PRELIMINAR DA PROVA FINAL': 'Natália',
    'GABARITO PÓS-RECURSO': 'Natália',
    'GABARITO PÓS-RECURSO (NÍVEIS FUNDAMENTAL INCOMPLETO, MÉDIO E TÉCNICO)': 'Natália',
    'GABARITO PÓS-RECURSO - RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA FOLHA DE RESPOSTAS DA PROVA OBJETIVA': 'Natália',
    'GABARITO PÓS-RECURSO - RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA FOLHA DE RESPOSTAS DA PROVA OBJETIVA (NÍVEIS FUNDAMENTAL INCOMPLETO, MÉDIO E TÉCNICO)': 'Natália',
    'GABARITO PÓS-RECURSO - RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA FOLHA DE RESPOSTAS DA PROVA OBJETIVA -': 'Natália',
    'GABARITO PÓS-RECURSO - RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PÓS-RECURSOS DA TOTALIZAÇÃO DA PROVA OBJETIVA': 'Natália',
    'GABARITO PÓS-RECURSO RETIFICADO E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA': 'Natália',
    'GABARITO PÓS-RECURSO- RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA FOLHA DE RESPOSTAS DA PROVA OBJETIVA': 'Natália',
    'HOMOLOGAÇÃO': 'Manuela',
    'HOMOLOGAÇÃO (APENAS PARA OS CARGOS DA PROVA PRÁTICA)': 'Manuela',
    'HOMOLOGAÇÃO (EXCETO CARGOS DA PROVA PRÁTICA)': 'Manuela',
    'HOMOLOGAÇÃO FINAL': 'Manuela',
    'INSCRIÇÕES/ENVIO DE LAUDOS MÉDICOS PARA VAGAS PCD E SOLICITAÇÃO DE CONDIÇÃO ESPECIAL': 'Lorena',
    'MANIFESTAÇÃO DE INTERESSE EM REALIZAR A ENTREVISTA DEVOLUTIVA ON-LINE': 'Laryssa',
    'MANIFESTAÇÃO DE INTERESSE PARA ENTREVISTA DEVOLUTIVA ON-LINE': 'Laryssa',
    'ORGANIZAÇÃO DO PROCEDIMENTO DE VERIFICAÇÃO DA VERACIDADE DA AUTODECLARAÇÃO': 'Laryssa',
    'ORGANIZAÇÃO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO - PRESENCIAL - INFORMAR PARA COMISSÃO DA CÂMARA MUNICIPAL DE CATAGUASES/MG O QUANTITATIVO DE CANDIDATOS': 'Laryssa',
    'ORGANIZAÇÃO PROVA PRÁTICA': 'Laryssa',
    'PERÍODO DE INSCRIÇÕES/PCD/NEGROS/FEM./SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS': 'Lorena',
    'PERÍODO DE INSCRIÇÕES/PCD/NEGROS/SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS': 'Lorena',
    'PERÍODO DE INSCRIÇÕES/PCD/SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS': 'Lorena',
    'PERÍODO SOLICITAÇÃO DE ISENÇÃO': 'Lorena',
    'PROCEDIMENTO HETEROIDENTIFICAÇÃO - AVALIAÇÃO DA BANCA': 'Laryssa',
    'PROCEDIMENTO HETEROIDENTIFICAÇÃO - PRESENCIAL - COMISSÃO DA CÂMARA MUNICIPAL DE CATAGUASES/MG': 'Laryssa',
    'PROCEDIMENTO HETEROIDENTIFICAÇÃO - RECEBIMENTO DA AVALIAÇÃO DA BANCA': 'Laryssa',
    'PROVA OBJETIVA': 'Laryssa',
    'PROVA OBJETIVA E PROVA DISCURSIVA': 'Laryssa',
    'PUBLICAÇÃO DA CLASSIFICAÇÃO PRELIMINAR': 'Laryssa',
    'PUBLICAÇÃO DA CLASSIFICAÇÃO PRELIMINAR DA TOTALIZAÇÃO DAS NOTAS DA PROVA OBJETIVA E PROVA DISCURSA (REDAÇÃO) (AMPLA CONCORRÊNCIA/PCD)': 'Manuela',
    'PUBLICAÇÃO DA CONVOCAÇÃO DE CANDIDATOS EXCEDENTES PARA MATRÍCULA DO CURSO DE FORMAÇÃO (SE HOUVER)': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO DE EXCEDENTES PARA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA A AVALIAÇÃO PSICOLÓGICA': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA AVALIAÇÃO CLÍNICA': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA AVALIAÇÃO MÉDICA': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA AVALIAÇÃO MÉDICA E PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA AVALIAÇÃO PSICOLÓGICA': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA ENTREGA DE DOCUMENTAÇÃO – SINDICÂNCIA SOCIAL': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA ENTREGA DOCUMENTAÇÃO PARA SINDICÂNCIA SOCIAL': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA ENVIO DOCUMENTAÇÃO DA SINDICÂNCIA SOCIAL': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA O CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA O PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA PROVA DE CAPACIDADE FÍSICA': 'Laryssa',
    'PUBLICAÇÃO DA CONVOCAÇÃO PARA REALIZAÇÃO DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DA PORTARIA DE INVESTIGAÇÃO SOCIAL': 'Natália',
    'PUBLICAÇÃO DE PORTARIA COM COMPOSIÇÃO EQUIPE INVESTIGAÇÃO SOCIAL': 'Natália',
    'PUBLICAÇÃO DO DEFERIMENTO PRELIMINAR DA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DO GABARITO DEFINITIVO E RESULTADO PRELIMINAR CURSO FORMAÇÃO INTRODUTÓRIA BÁSICA': 'Natália',
    'PUBLICAÇÃO DO GABARITO PRELIMINAR': 'Natália',
    'PUBLICAÇÃO DO GABARITO PRELIMINAR CURSO FORMAÇÃO INTRODUTÓRIA BÁSICA': 'Natália',
    'PUBLICAÇÃO DO GABARITO PÓS-RECURSO QUESTÕES DA PROVA OBJETIVA - RETIFICADO (SE HOUVER)': 'Natália',
    'PUBLICAÇÃO DO RESULTADO FINAL': 'Manuela',
    'PUBLICAÇÃO DO RESULTADO FINAL DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA AVALIAÇÃO CLÍNICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA AVALIAÇÃO MÉDICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA AVALIAÇÃO MÉDICA E DO PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA AVALIAÇÃO PSICOLÓGICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA PROVA DE CAPACIDADE FÍSICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA SINDICÂNCIA SOCIAL': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA SOLICITAÇÃO ADAPTAÇÃO DA PROVA DE CAPACIDADE FÍSICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA DISCURSA (REDAÇÃO) - DISPONIBILIZAÇÃO DE ESPELHOS DA CORREÇÃO DA PROVA DISCURSA (REDAÇÃO)': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA FOLHA DE RESPOSTAS DA PROVA OBJETIVA': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DAS INSCRIÇÕES/PCD/NEGROS/INDÍGENAS/QUILOMBOLAS/CANDIDATAS DO SEXO FEMININO/SOLICITAÇÃO DE CONDIÇÃO ESPECIAL': 'Lorena',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DAS SOLICITAÇÕES DE ISENÇÃO': 'Lorena',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR DO PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/FEM./SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS': 'Lorena',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO CONTRA QUESTÕES DA PROVA OBJETIVA': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO CONTRA RESULTADO DA AVALIAÇÃO CLÍNICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO CONTRA RESULTADO DA AVALIAÇÃO MÉDICA E DO PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO CONTRA RESULTADO DO PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO CONTRA SINDICÂNCIA SOCIAL': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO CURSO FORMAÇÃO INTRODUTÓRIA BÁSICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA AVALIAÇÃO MÉDICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA AVALIAÇÃO PSICOLÓGICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA CLASSIFICAÇÃO PRELIMINAR': 'Manuela',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA CLASSIFICAÇÃO PRELIMINAR DA TOTALIZAÇÃO DAS NOTAS DA PROVA OBJETIVA E PROVA DISCURSA (REDAÇÃO) (AMPLA CONCORRÊNCIA/PCD)': 'Manuela',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA MATRÍCULA CANDIDATOS EXCEDENTES DO CURSO DE FORMAÇÃO (SE HOUVER)': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA MATRÍCULA DE EXCEDENTES': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA PROVA DE CAPACIDADE FÍSICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA PROVA DISCURSIVA': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA SINDICÂNCIA SOCIAL': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA SOLICITAÇÃO ADAPTAÇÃO DA PROVA DE CAPACIDADE FÍSICA': 'Laryssa',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA DISCURSA (REDAÇÃO)': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA': 'Natália',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DAS INSCRIÇÕES/PCD/NEGROS/FEM./SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS.': 'Lorena',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DAS INSCRIÇÕES/PCD/NEGROS/INDÍGENAS/QUILOMBOLAS/CANDIDATAS DO SEXO FEMININO/SOLICITAÇÃO DE CONDIÇÃO ESPECIAL': 'Lorena',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DAS SOLICITAÇÕES DE ISENÇÃO': 'Lorena',
    'PUBLICAÇÃO DO RESULTADO PÓS-RECURSO DO CURSO DE FORMAÇÃO': 'Natália',
    'REALIZAÇÃO CURSO FORMAÇÃO INTRODUTÓRIA BÁSICA - 40 HORAS (ON-LINE)': 'Laryssa',
    'REALIZAÇÃO DA AVALIAÇÃO CLÍNICA': 'Laryssa',
    'REALIZAÇÃO DA AVALIAÇÃO MÉDICA': 'Laryssa',
    'REALIZAÇÃO DA AVALIAÇÃO PSICOLÓGICA': 'Laryssa',
    'REALIZAÇÃO DA PROVA DE CAPACIDADE FÍSICA': 'Laryssa',
    'REALIZAÇÃO DA PROVA FINAL DO CURSO DE FORMAÇÃO (PRESENCIAL)': 'Laryssa',
    'REALIZAÇÃO DA PROVA OBJETIVA': 'Laryssa',
    'REALIZAÇÃO DA PROVA OBJETIVA E PROVA DISCURSA (REDAÇÃO)': 'Laryssa',
    'REALIZAÇÃO DA PROVA PRÁTICA': 'Laryssa',
    'REALIZAÇÃO DAS ENTREVISTAS DEVOLUTIVAS': 'Laryssa',
    'REALIZAÇÃO DAS ENTREVISTAS DEVOLUTIVAS DA AVALIAÇÃO PSICOLÓGICA ON-LINE': 'Laryssa',
    'REALIZAÇÃO DO CURSO DE FORMAÇÃO': 'Laryssa',
    'REALIZAÇÃO DO CURSO DE FORMAÇÃO E CAPACITAÇÃO': 'Laryssa',
    'REALIZAÇÃO DO PROCEDIMENTO DE VERIFICAÇÃO DA VERACIDADE DA AUTODECLARAÇÃO (SAAE PASSOS)': 'Laryssa',
    'REALIZAÇÃO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO': 'Laryssa',
    'REALIZAÇÃO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO PELA COMISSÃO ESPECÍFICA': 'Laryssa',
    'REALIZAÇÃO PROVA PRÁTICA': 'Laryssa',
    'REALIZAÇÃO/AV. MÉD. PERICIAL MULTI/BIOPSICOSSOCIAL': 'Laryssa',
    'RESULTADO FINAL E HOMOLOGAÇÃO': 'Manuela',
    'RESULTADO PRELIMINAR DA AV. MÉD. PERICIAL MULTI/BIOPSICOSSOCIAL': 'Laryssa',
    'RESULTADO PRELIMINAR DA AVALIAÇÃO DE SINDICÂNCIA SOCIAL': 'Natália',
    'RESULTADO PRELIMINAR DA AVALIAÇÃO SOCIAL': 'Laryssa',
    'RESULTADO PRELIMINAR DA MATRÍCULA DE CANDIDATOS EXCEDENTES DO CURSO DE FORMAÇÃO (SE HOUVER)': 'Natália',
    'RESULTADO PRELIMINAR DA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'RESULTADO PRELIMINAR DA PROVA DE TÍTULOS': 'Natália',
    'RESULTADO PRELIMINAR DA PROVA PRÁTICA': 'Laryssa',
    'RESULTADO PRELIMINAR DA SOLICITAÇÃO DE ISENÇÃO': 'Lorena',
    'RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA FOLHA DE RESPOSTAS DA PROVA OBJETIVA': 'Natália',
    'RESULTADO PRELIMINAR DO CURSO DE FORMAÇÃO': 'Natália',
    'RESULTADO PRELIMINAR DO PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Natália',
    'RESULTADO PRELIMINAR DO PROCEDIMENTO DE VERIFICAÇÃO DA VERACIDADE DA AUTODECLARAÇÃO': 'Natália',
    'RESULTADO PRELIMINAR DO PROCEDIMENTO HETEROIDENTIFICAÇÃO': 'Natália',
    'RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL': 'Lorena',
    'RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLICITAÇÃO CONDIÇÃO ESPECIAL': 'Lorena',
    'RESULTADO PRELIMINAR INSCRIÇÕES/PCD/SOLIC CONDIÇÃO ESPECIAL': 'Lorena',
    'RESULTADO PRELIMINAR PROVA DE TÍTULOS': 'Natália',
    'RESULTADO PRELIMINAR PROVA PRÁTICA': 'Laryssa',
    'RESULTADO PÓS-RECURSO AVALIAÇÃO AV. MÉD. PERICIAL MULTI/BIOPSICOSSOCIAL': 'Laryssa',
    'RESULTADO PÓS-RECURSO DA AVALIAÇÃO DE SINDICÂNCIA SOCIAL': 'Natália',
    'RESULTADO PÓS-RECURSO DA AVALIAÇÃO SOCIAL': 'Laryssa',
    'RESULTADO PÓS-RECURSO DA MATRÍCULA CANDIDATOS EXCEDENTES DO CURSO DE FORMAÇÃO (SE HOUVER)': 'Natália',
    'RESULTADO PÓS-RECURSO DA MATRÍCULA DO CURSO DE FORMAÇÃO': 'Natália',
    'RESULTADO PÓS-RECURSO DA PROVA DE TÍTULOS': 'Natália',
    'RESULTADO PÓS-RECURSO DA PROVA DISCURSIVA': 'Natália',
    'RESULTADO PÓS-RECURSO DA PROVA PRÁTICA': 'Laryssa',
    'RESULTADO PÓS-RECURSO DA SOLICITAÇÃO DE ISENÇÃO': 'Lorena',
    'RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA': 'Natália',
    'RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA (NÍVEIS FUNDAMENTAL INCOMPLETO, MÉDIO E TÉCNICO)': 'Natália',
    'RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA (NÍVEL SUPERIOR)': 'Natália',
    'RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA E RESULTADO PRELIMINAR DA PROVA DISCURSIVA - DISPONIBILIZAÇÃO DE ESPELHOS DA CORREÇÃO DA PROVA DISCURSIVA': 'Natália',
    'RESULTADO PÓS-RECURSO DO CURSO DE FORMAÇÃO': 'Natália',
    'RESULTADO PÓS-RECURSO DO PROCEDIMENTO DE HETEROIDENTIFICAÇÃO': 'Natália',
    'RESULTADO PÓS-RECURSO DO PROCEDIMENTO DE VERIFICAÇÃO DA VERACIDADE DA AUTODECLARAÇÃO': 'Natália',
    'RESULTADO PÓS-RECURSO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO': 'Natália',
    'RESULTADO PÓS-RECURSO INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL': 'Lorena',
    'RESULTADO PÓS-RECURSO INSCRIÇÕES/PCD/NEGROS/SOLICITAÇÃO CONDIÇÃO ESPECIAL': 'Lorena',
    'RESULTADO PÓS-RECURSO INSCRIÇÕES/PCD/SOLIC CONDIÇÃO ESPECIAL': 'Lorena',
    'RESULTADO PÓS-RECURSO INSCRIÇÕES/PcD/NEGROS/SOLIC CONDIÇÃO ESPECIAL': 'Lorena',
    'SOLICITAÇÃO DE ISENÇÃO': 'Lorena',
}

# ─── PÁGINA ───────────────────────────────────────────────────────────────────
st.set_page_config(page_title="IBGP · Minhas Tarefas", page_icon="✅", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800&family=JetBrains+Mono:wght@400;500;600&display=swap');
*{box-sizing:border-box}
html,body,[class*="css"]{font-family:'Public Sans',system-ui,sans-serif;color:#1f2a3d;-webkit-font-smoothing:antialiased}
/* Oculta sidebar padrão do Streamlit e padding */
section[data-testid="stSidebar"]{display:none}
.stApp{background:#eef1f6}
.block-container{padding:0!important;max-width:100%!important}
header[data-testid="stHeader"]{display:none}
/* Login box */
.login-box{background:#fff;border:1px solid #e2e7ef;border-radius:14px;padding:3rem 2rem;text-align:center;max-width:420px;margin:4rem auto;box-shadow:0 2px 8px rgba(16,30,54,0.06)}
.login-box h2{color:#1f2a3d;font-size:1.2rem;margin-bottom:.5rem;font-weight:700}
.login-box p{color:#7a869c;font-size:.9rem;margin-bottom:1.5rem}
/* Cards de grupo */
.group-card{background:#fff;border:1px solid #e2e7ef;border-radius:14px;box-shadow:0 1px 2px rgba(16,30,54,0.04);overflow:hidden;margin-bottom:16px}
.group-header{display:flex;align-items:center;gap:10px;padding:13px 20px}
.group-header-venc{background:#fdeceb}
.group-header-hoje{background:#fbf1de}
.group-header-semana{background:#e9f1fb}
.group-header-futuro{background:#eef1f6}
.group-label-venc{font-weight:800;color:#b3322f;font-size:12px;letter-spacing:.07em}
.group-label-hoje{font-weight:800;color:#a06c12;font-size:12px;letter-spacing:.07em}
.group-label-semana{font-weight:800;color:#2860b0;font-size:12px;letter-spacing:.07em}
.group-label-futuro{font-weight:800;color:#4a566d;font-size:12px;letter-spacing:.07em}
.group-badge-venc{background:#f7d6d4;color:#b3322f;font-weight:700;font-size:11px;padding:2px 9px;border-radius:20px;margin-left:auto}
.group-badge-hoje{background:#f3e2bf;color:#a06c12;font-weight:700;font-size:11px;padding:2px 9px;border-radius:20px;margin-left:auto}
.group-badge-semana{background:#cfe0f5;color:#2860b0;font-weight:700;font-size:11px;padding:2px 9px;border-radius:20px;margin-left:auto}
.group-badge-futuro{background:#dfe4ec;color:#4a566d;font-weight:700;font-size:11px;padding:2px 9px;border-radius:20px;margin-left:auto}
/* Linha de tarefa */
.t-row{display:flex;align-items:center;gap:14px;padding:14px 20px;border-top:1px solid #eef1f6}
.t-concurso{font-size:11.5px;font-weight:700;color:#7a869c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.01em}
.t-nome{font-size:14px;color:#28344a;font-weight:500}
/* Chips de pessoa */
.chip-lorena{display:inline-block;padding:2px 10px;border-radius:6px;font-size:11.5px;font-weight:700;white-space:nowrap;background:#e8f0fb;color:#2860b0}
.chip-laryssa{display:inline-block;padding:2px 10px;border-radius:6px;font-size:11.5px;font-weight:700;white-space:nowrap;background:#e4f3ea;color:#2e7d52}
.chip-natalia{display:inline-block;padding:2px 10px;border-radius:6px;font-size:11.5px;font-weight:700;white-space:nowrap;background:#e4f3ea;color:#2e7d52}
.chip-manuela{display:inline-block;padding:2px 10px;border-radius:6px;font-size:11.5px;font-weight:700;white-space:nowrap;background:#efeafb;color:#6b4fa3}
.chip-pessoa{display:inline-block;padding:2px 10px;border-radius:6px;font-size:11.5px;font-weight:700;white-space:nowrap;background:#eef0f4;color:#5b6577}
/* Chips de data */
.chip-venc{flex:none;background:#fdeceb;color:#c0322f;border:1px solid #f3cfcd;font-weight:700;font-size:11.5px;padding:5px 11px;border-radius:20px;white-space:nowrap}
.chip-hoje{flex:none;background:#fbf1de;color:#a06c12;border:1px solid #ecd6a8;font-weight:700;font-size:11.5px;padding:5px 11px;border-radius:20px;white-space:nowrap}
.chip-semana{flex:none;background:#e9f1fb;color:#2860b0;border:1px solid #b8d0ef;font-weight:700;font-size:11.5px;padding:5px 11px;border-radius:20px;white-space:nowrap}
.chip-ok{flex:none;background:#eef1f6;color:#4a566d;border:1px solid #d8dee8;font-weight:700;font-size:11.5px;padding:5px 11px;border-radius:20px;white-space:nowrap}
/* KPI cards */
.kpi-card{background:#fff;border:1px solid #e2e7ef;border-radius:14px;box-shadow:0 1px 2px rgba(16,30,54,0.04);padding:18px 20px}
.kpi-label{font-size:11.5px;font-weight:700;letter-spacing:.05em;color:#7a869c;text-transform:uppercase}
.kpi-val{font-family:'JetBrains Mono',monospace;font-size:34px;font-weight:600;color:#1f2a3d;line-height:1.1}
.kpi-val-venc{color:#d93b3b}
.kpi-val-hoje{color:#c9821a}
.kpi-val-semana{color:#2f6cc4}
/* Nota inline */
.nota-inline{padding:4px 20px 8px;font-size:12px;color:#7a869c;background:#fafbfc;border-top:1px dashed #e2e7ef}
</style>
""", unsafe_allow_html=True)

# ─── AUTH ─────────────────────────────────────────────────────────────────────
def auth_url():
    params = {"client_id": CLIENT_ID, "response_type": "code", "redirect_uri": REDIRECT_URI,
               "scope": SCOPES, "response_mode": "query"}
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?" + urlencode(params)

def trocar_codigo(code):
    resp = requests.post(f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"client_id": CLIENT_ID, "client_secret": st.secrets["CLIENT_SECRET"],
              "grant_type": "authorization_code", "code": code,
              "redirect_uri": REDIRECT_URI, "scope": SCOPES})
    return resp.json()

def renovar_token(refresh_token):
    resp = requests.post(f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"client_id": CLIENT_ID, "client_secret": st.secrets["CLIENT_SECRET"],
              "grant_type": "refresh_token", "refresh_token": refresh_token, "scope": SCOPES})
    return resp.json()

# ─── GRAPH ────────────────────────────────────────────────────────────────────
def graph_get(token, url):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def graph_get_all(token, url):
    headers = {"Authorization": f"Bearer {token}"}
    results, next_url = [], url
    while next_url:
        resp = requests.get(next_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data.get("value", []))
        next_url = data.get("@odata.nextLink")
    return results

def graph_patch(token, url, body):
    etag_resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    etag = etag_resp.headers.get("ETag", "")
    resp = requests.patch(url, headers={"Authorization": f"Bearer {token}",
        "Content-Type": "application/json", "If-Match": etag}, json=body)
    return resp.status_code

@st.cache_data(ttl=600, show_spinner=False)
def buscar_plano_id(token):
    groups = graph_get(token, "https://graph.microsoft.com/v1.0/me/memberOf")
    for g in groups.get("value", []):
        gid = g.get("id")
        if not gid: continue
        try:
            result = graph_get(token, f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans")
            for p in result.get("value", []):
                if NOME_PLANO.upper() in p.get("title", "").upper():
                    return p["id"], gid
        except: continue
    return None, None

@st.cache_data(ttl=300, show_spinner=False)
def buscar_buckets_planner(token, plano_id):
    data = graph_get(token, f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets")
    return {b["name"]: b["id"] for b in data.get("value", [])}

@st.cache_data(ttl=180, show_spinner=False)
def buscar_tarefas(token, _cache_key=0):
    groups = graph_get(token, "https://graph.microsoft.com/v1.0/me/memberOf")
    planos = []
    for g in groups.get("value", []):
        gid = g.get("id")
        if not gid: continue
        try:
            result = graph_get(token, f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans")
            for p in result.get("value", []):
                if NOME_PLANO.upper() in p.get("title", "").upper():
                    planos.append({"id": p["id"], "title": p.get("title", "")})
        except: continue

    tarefas = []
    for plano in planos:
        buckets_data = graph_get(token, f"https://graph.microsoft.com/v1.0/planner/plans/{plano['id']}/buckets")
        buckets = {b["id"]: b["name"] for b in buckets_data.get("value", [])}
        todas = graph_get_all(token, f"https://graph.microsoft.com/v1.0/planner/plans/{plano['id']}/tasks")
        for t in todas:
            if t.get("percentComplete", 0) == 100: continue
            nome = t.get("title", "").strip()
            responsavel = ATRIBUICOES.get(nome)
            if not responsavel: continue
            bucket = buckets.get(t.get("bucketId", ""), "—")
            due = t.get("dueDateTime")
            data_fmt, dias = "Sem data", None
            if due:
                dt = datetime.fromisoformat(due.replace("Z", "+00:00")).replace(tzinfo=None)
                data_fmt = dt.strftime("%d/%m/%Y")
                dias = (dt.date() - date.today()).days
            tarefas.append({"id": t["id"], "municipio": bucket, "tarefa": nome,
                            "data": data_fmt, "dias": dias, "responsavel": responsavel})

    def sort_key(x):
        if x["dias"] is None: return (2, "9999")
        if x["dias"] < 0: return (0, str(x["dias"]).zfill(6))
        return (1, str(x["dias"]).zfill(6))
    return sorted(tarefas, key=sort_key)

# ─── AUTH STATE ───────────────────────────────────────────────────────────────
params = st.query_params
code = params.get("code")

if "access_token" not in st.session_state:
    if code:
        with st.spinner("Autenticando..."):
            token_data = trocar_codigo(code)
            if "access_token" in token_data:
                st.session_state["access_token"] = token_data["access_token"]
                st.session_state["refresh_token"] = token_data.get("refresh_token")
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"Erro: {token_data.get('error_description', 'Erro desconhecido')}")
    else:
        st.markdown('<div class="login-box"><h2>✅ IBGP · Tarefas da Equipe</h2><p>Entre com sua conta do IBGP para visualizar as tarefas.</p></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.link_button("🔐 Entrar com Microsoft", auth_url(), use_container_width=True)
        st.stop()

token = st.session_state["access_token"]

try:
    me = graph_get(token, "https://graph.microsoft.com/v1.0/me")
    user_name = me.get("displayName", "").split()[0]
except requests.HTTPError as e:
    if e.response.status_code == 401 and st.session_state.get("refresh_token"):
        new_token = renovar_token(st.session_state["refresh_token"])
        if "access_token" in new_token:
            st.session_state["access_token"] = new_token["access_token"]
            st.rerun()
    st.error("Sessão expirada.")
    if st.button("Entrar novamente"):
        del st.session_state["access_token"]
        st.rerun()
    st.stop()

# ─── HEADER ───────────────────────────────────────────────────────────────────
hoje_str = date.today().strftime("%d/%m/%Y — %A").replace(
    "Monday","Segunda").replace("Tuesday","Terça").replace("Wednesday","Quarta").replace(
    "Thursday","Quinta").replace("Friday","Sexta").replace("Saturday","Sábado").replace("Sunday","Domingo")

# ─── TOPBAR ───────────────────────────────────────────────────────────────────
perfil_label = "Gestora · Equipe IBGP" if is_gestora else ("Cronograma · IBGP" if is_cronograma else "Equipe IBGP")
st.markdown(f"""
<div style="display:flex;align-items:center;gap:16px;padding:16px 32px;background:#fff;border-bottom:1px solid #e2e7ef;margin-bottom:0">
  <div style="display:flex;flex-direction:column;line-height:1.25">
    <span style="font-size:18px;font-weight:700;color:#1f2a3d">Olá, {user_name}! 👋</span>
    <span style="font-size:12.5px;color:#7a869c;font-weight:500">Tarefas da equipe · {hoje_str}</span>
  </div>
  <div style="margin-left:auto;display:flex;align-items:center;gap:10px">
    <div style="display:flex;align-items:center;gap:9px;padding:8px 14px;background:#f4f6fa;border:1px solid #e2e7ef;border-radius:9px;font-size:13px;font-weight:600;color:#41506b">
      <div style="width:28px;height:28px;border-radius:50%;background:#6b4fa3;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">{user_name[0].upper()}</div>
      <span>{user_name}</span>
      <span style="font-size:11px;color:#9aa6b8">{perfil_label}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Navegação + Atualizar
nav_col, btn_col = st.columns([9, 1])
with nav_col:
    if is_gestora or is_cronograma:
        tabs = st.tabs(["📋 Tarefas", "📊 Validar", "🗓 Gerar", "🔧 Reajustar"] if is_gestora else ["📊 Validar", "🗓 Gerar", "🔧 Reajustar"])
        tab_idx = st.session_state.get("tab_idx", 0)
with btn_col:
    if st.button("↻ Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─── PERFIL ───────────────────────────────────────────────────────────────────
nome_interno = NOME_MAP.get(user_name.lower(), user_name.title())
is_gestora = nome_interno == "Manuela"
is_cronograma = nome_interno == "Fabiano"

# Fabiano vê só a seção de cronograma
if is_cronograma:
    st.info("👋 Olá, Fabiano! Acesse abaixo o validador e gerador de cronograma.")
    # Pula direto para a seção de cronograma (st.stop() ao fim do bloco de tarefas)

if not is_cronograma:
    if is_gestora:
        st.markdown("### 👥 Visão da Gestora")
        filtro_pessoa = st.selectbox("Visualizar tarefas de:", ["Toda a equipe"] + EQUIPE)
    else:
        filtro_pessoa = nome_interno
        st.caption(f"Exibindo suas tarefas — {filtro_pessoa}")

# ─── DADOS ────────────────────────────────────────────────────────────────────
if not is_cronograma:
    with st.spinner("🔄 Buscando tarefas no Planner..."):
        todas = buscar_tarefas(token)

    if filtro_pessoa != "Toda a equipe":
        tarefas_base = [t for t in todas if t["responsavel"].lower() == filtro_pessoa.lower()]
    else:
        tarefas_base = todas

    if not tarefas_base:
        st.success("🎉 Nenhuma tarefa pendente encontrada!")
        st.stop()

    # ─── FILTROS ──────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        concursos_disponiveis = sorted(set(t["municipio"] for t in tarefas_base))
        filtro_concurso = st.multiselect("🔍 Filtrar por concurso", options=concursos_disponiveis)
    with col_f2:
        tarefas_disponiveis = sorted(set(t["tarefa"] for t in tarefas_base))
        filtro_tarefa = st.multiselect("📋 Filtrar por tarefa", options=tarefas_disponiveis)

    # Aplica filtros
    tarefas = tarefas_base
    if filtro_concurso:
        tarefas = [t for t in tarefas if t["municipio"] in filtro_concurso]
    if filtro_tarefa:
        tarefas = [t for t in tarefas if t["tarefa"] in filtro_tarefa]

    if not tarefas:
        st.info("Nenhuma tarefa encontrada com os filtros selecionados.")
        st.stop()

    # ─── MÉTRICAS ─────────────────────────────────────────────────────────────────
    vencidas  = [t for t in tarefas if t["dias"] is not None and t["dias"] < 0]
    hoje_list = [t for t in tarefas if t["dias"] == 0]
    semana    = [t for t in tarefas if t["dias"] is not None and 1 <= t["dias"] <= 7]
    futuras   = [t for t in tarefas if t["dias"] is None or t["dias"] > 7]

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:20px 0">
      <div class="kpi-card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="width:8px;height:8px;border-radius:50%;background:#94a1b6"></span><span class="kpi-label">Total</span></div><div class="kpi-val">{len(tarefas)}</div></div>
      <div class="kpi-card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="width:8px;height:8px;border-radius:50%;background:#d93b3b"></span><span class="kpi-label">Vencidas</span></div><div class="kpi-val kpi-val-venc">{len(vencidas)}</div></div>
      <div class="kpi-card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="width:8px;height:8px;border-radius:50%;background:#d98a1f"></span><span class="kpi-label">Hoje</span></div><div class="kpi-val kpi-val-hoje">{len(hoje_list)}</div></div>
      <div class="kpi-card"><div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="width:8px;height:8px;border-radius:50%;background:#2f6cc4"></span><span class="kpi-label">Próximos 7 dias</span></div><div class="kpi-val kpi-val-semana">{len(semana)}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ─── RENDER ───────────────────────────────────────────────────────────────────
    def chip(t):
        if t["dias"] is None: return '<span class="chip-ok">Sem data</span>'
        if t["dias"] < 0: return f'<span class="chip-venc">Venceu há {abs(t["dias"])}d</span>'
        if t["dias"] == 0: return '<span class="chip-hoje">⚡ Hoje</span>'
        if t["dias"] <= 7: return f'<span class="chip-semana">{t["data"]} · {t["dias"]}d</span>'
        return f'<span class="chip-ok">{t["data"]} · {t["dias"]}d</span>'

    def pessoa_chip(nome):
        key = nome.lower().replace("á","a").replace("â","a").replace("ã","a")
        classes = {"lorena":"chip-lorena","laryssa":"chip-laryssa","natalia":"chip-natalia","manuela":"chip-manuela"}
        cls = classes.get(key, "chip-pessoa")
        return f'<span class="{cls}">{nome}</span>'

    # ─── NOTAS ───────────────────────────────────────────────────────────────
    if "notas_cache" not in st.session_state:
        st.session_state["notas_cache"] = {}

    def carregar_nota(task_id, _token):
        return st.session_state["notas_cache"].get(task_id, "")

    def salvar_nota(task_id, texto, _token):
        try:
            headers = {"Authorization": f"Bearer {_token}"}
            resp = requests.get(
                f"https://graph.microsoft.com/v1.0/planner/tasks/{task_id}/details",
                headers=headers
            )
            if resp.status_code != 200:
                return False
            etag = resp.headers.get("ETag", "")
            patch_resp = requests.patch(
                f"https://graph.microsoft.com/v1.0/planner/tasks/{task_id}/details",
                headers={**headers, "Content-Type": "application/json", "If-Match": etag},
                json={"description": texto}
            )
            if patch_resp.status_code in [200, 204]:
                st.session_state["notas_cache"][task_id] = texto
                return True
        except:
            pass
        return False

    GRUPO_STYLES = {
        "vencida": ("group-header-venc", "group-label-venc", "group-badge-venc",
                    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#c0322f" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>', "VENCIDAS"),
        "hoje": ("group-header-hoje", "group-label-hoje", "group-badge-hoje",
                 '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#b8780f" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>', "HOJE"),
        "semana": ("group-header-semana", "group-label-semana", "group-badge-semana",
                   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2860b0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>', "PRÓXIMOS 7 DIAS"),
        "futuro": ("group-header-futuro", "group-label-futuro", "group-badge-futuro",
                   '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#56627a" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/></svg>', "FUTURAS"),
    }

    def render_grupo(tipo, lista, show_pessoa=False):
        if not lista: return
        hdr_cls, lbl_cls, badge_cls, icon, label = GRUPO_STYLES[tipo]
        st.markdown(f'''
        <div class="group-card">
          <div class="group-header {hdr_cls}">
            {icon}
            <span class="{lbl_cls}">{label}</span>
            <span class="{badge_cls}">{len(lista)} tarefas</span>
          </div>''', unsafe_allow_html=True)

        for t in lista:
            nota_salva = carregar_nota(t["id"], token)
            p_chip = pessoa_chip(t["responsavel"]) if show_pessoa else ""
            col_card, col_btns = st.columns([12, 1])
            with col_card:
                st.markdown(f'''
                <div class="t-row">
                  <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:5px">
                    <div class="t-concurso">{t["municipio"]}</div>
                    <div style="display:flex;align-items:center;gap:9px">{p_chip}<span class="t-nome">{t["tarefa"]}</span></div>
                    {"" if not nota_salva else f'<div style="font-size:11.5px;color:#9aa6b8;font-style:italic">📝 {nota_salva}</div>'}
                  </div>
                  {chip(t)}
                </div>''', unsafe_allow_html=True)
            with col_btns:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("📝", key=f"nota_{t['id']}", help="Nota", use_container_width=True):
                        st.session_state[f"editando_nota_{t['id']}"] = not st.session_state.get(f"editando_nota_{t['id']}", False)
                with c2:
                    if st.button("✅", key=f"ok_{t['id']}", help="Concluída", use_container_width=True):
                        graph_patch(token, f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}", {"percentComplete": 100})
                        st.cache_data.clear()
                        st.rerun()
            if st.session_state.get(f"editando_nota_{t['id']}"):
                nova_nota = st.text_input("✏️", value=nota_salva, key=f"input_nota_{t['id']}",
                    placeholder="Ex: Data alterada para 15/07", label_visibility="collapsed")
                col_s, col_c, _ = st.columns([1, 1, 8])
                with col_s:
                    if st.button("💾 Salvar", key=f"salvar_nota_{t['id']}", type="primary"):
                        if salvar_nota(t["id"], nova_nota, token):
                            st.session_state[f"editando_nota_{t['id']}"] = False
                            st.rerun()
                with col_c:
                    if st.button("✖", key=f"cancelar_nota_{t['id']}"):
                        st.session_state[f"editando_nota_{t['id']}"] = False
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    show_pessoa = (filtro_pessoa == "Toda a equipe")
    render_grupo("vencida", vencidas, show_pessoa)
    render_grupo("hoje", hoje_list, show_pessoa)
    render_grupo("semana", semana, show_pessoa)
    if semana: st.write("")
    render_grupo("futuro", futuras, show_pessoa)

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — VALIDAR CRONOGRAMA (só para gestora)
# ═══════════════════════════════════════════════════════════════════════════════

if is_gestora or is_cronograma:
    st.divider()
    st.markdown("---")
    st.markdown("## 📊 Validar Novo Cronograma")
    st.caption("Suba a planilha do novo concurso para verificar conflitos e sobrecarga antes de cadastrar no Planner.")

    arquivo = st.file_uploader("Selecione a planilha (.xlsx)", type=["xlsx"])

    if arquivo:
        import pandas as pd
        from datetime import timedelta

        df_novo = pd.read_excel(arquivo, sheet_name="TAREFAS")
        df_novo.columns = [c.strip() for c in df_novo.columns]
        df_novo = df_novo.dropna(subset=["Nome da tarefa", "Data de conclusão"])
        df_novo["Data de conclusão"] = pd.to_datetime(df_novo["Data de conclusão"], errors="coerce")
        df_novo["Data de início"] = pd.to_datetime(df_novo["Data de início"], errors="coerce")
        df_novo = df_novo.dropna(subset=["Data de conclusão"])

        # Mapeia responsável pelo nome da tarefa
        df_novo["Responsável"] = df_novo["Nome da tarefa"].str.strip().map(ATRIBUICOES).fillna("—")

        nome_concurso = df_novo["Nome do Bucket"].iloc[0] if "Nome do Bucket" in df_novo.columns else "Novo Concurso"
        st.success(f"✅ **{len(df_novo)} tarefas** carregadas — {nome_concurso}")

        # Busca tarefas já existentes no Planner
        with st.spinner("Comparando com o Planner..."):
            tarefas_planner = buscar_tarefas(token)

        # Monta DataFrame do Planner para comparação
        planner_rows = []
        for t in tarefas_planner:
            if t["data"] != "Sem data":
                try:
                    dt = datetime.strptime(t["data"], "%d/%m/%Y").date()
                    planner_rows.append({
                        "tarefa": t["tarefa"],
                        "data": dt,
                        "municipio": t["municipio"],
                        "responsavel": t["responsavel"],
                    })
                except: pass
        df_planner = pd.DataFrame(planner_rows) if planner_rows else pd.DataFrame(columns=["tarefa","data","municipio","responsavel"])

        # ── ANÁLISE DE CONFLITOS ──────────────────────────────────────────────
        conflitos = []
        for _, row in df_novo.iterrows():
            nome = row["Nome da tarefa"].strip()
            data_nova = row["Data de conclusão"].date()
            resp = row["Responsável"]

            # Conflito: mesma tarefa no mesmo dia em outro concurso
            iguais = df_planner[(df_planner["tarefa"] == nome) & (df_planner["data"] == data_nova)]
            for _, p in iguais.iterrows():
                conflitos.append({
                    "tarefa": nome,
                    "data": data_nova.strftime("%d/%m/%Y"),
                    "conflito_com": p["municipio"],
                    "responsavel": resp,
                    "tipo": "⚠️ Conflito de atividade",
                })

        # ── ANÁLISE DE SOBRECARGA ─────────────────────────────────────────────
        sobrecargas = []
        LIMITE_DIA = 3  # mais de 3 tarefas no mesmo dia = sobrecarga

        for resp in EQUIPE:
            # Tarefas novas dessa pessoa
            novas_pessoa = df_novo[df_novo["Responsável"] == resp][["Nome da tarefa","Data de conclusão"]].copy()
            novas_pessoa["data"] = novas_pessoa["Data de conclusão"].dt.date
            novas_pessoa["origem"] = "novo"

            # Tarefas existentes dessa pessoa no Planner
            planner_pessoa = df_planner[df_planner["responsavel"] == resp][["tarefa","data"]].copy()
            planner_pessoa.rename(columns={"tarefa":"Nome da tarefa"}, inplace=True)
            planner_pessoa["origem"] = "planner"

            combinado = pd.concat([
                novas_pessoa[["Nome da tarefa","data","origem"]],
                planner_pessoa[["Nome da tarefa","data","origem"]]
            ], ignore_index=True)

            por_dia = combinado.groupby("data")
            for dia, grupo in por_dia:
                total = len(grupo)
                novas_no_dia = len(grupo[grupo["origem"] == "novo"])
                if total > LIMITE_DIA and novas_no_dia > 0:
                    sobrecargas.append({
                        "responsavel": resp,
                        "data": dia.strftime("%d/%m/%Y"),
                        "total_tarefas": total,
                        "tarefas_novas": novas_no_dia,
                        "tarefas_planner": total - novas_no_dia,
                    })

        # ── EXIBIÇÃO ──────────────────────────────────────────────────────────
        col_conf, col_sobre = st.columns(2)
        col_conf.metric("⚠️ Conflitos de atividade", len(conflitos))
        col_sobre.metric("🔴 Dias sobrecarregados", len(sobrecargas))

        st.divider()

        if conflitos:
            st.markdown("### ⚠️ Conflitos de Atividade")
            st.caption("Mesma atividade já existe no Planner na mesma data, em outro concurso.")
            for c in conflitos:
                st.markdown(f"""
                <div class="t-card" style="margin-bottom:4px; border-top:1px solid #E2E8F0; border-radius:8px;">
                    <span class="municipio">📅 {c['data']}</span>
                    <span class="t-nome">{c['tarefa']}</span>
                    <span class="chip chip-venc">Conflito com: {c['conflito_com']}</span>
                </div>
                """, unsafe_allow_html=True)

            # Sugestão de datas alternativas
            st.markdown("#### 💡 Sugestões de datas alternativas")
            for c in conflitos:
                tarefa_nome = c["tarefa"]
                data_original = datetime.strptime(c["data"], "%d/%m/%Y").date()
                datas_ocupadas = set(df_planner[df_planner["tarefa"] == tarefa_nome]["data"].tolist())

                sugestoes = []
                for delta in [-2, -1, 1, 2, 3]:
                    candidata = data_original + timedelta(days=delta)
                    if candidata not in datas_ocupadas and candidata >= date.today():
                        sugestoes.append(candidata.strftime("%d/%m/%Y"))
                    if len(sugestoes) == 2:
                        break

                sug_str = " ou ".join(sugestoes) if sugestoes else "Sem sugestão disponível"
                st.markdown(f"- **{tarefa_nome}** `{c['data']}` → sugestão: **{sug_str}**")

        if sobrecargas:
            st.markdown("### 🔴 Dias Sobrecarregados por Pessoa")
            st.caption(f"Dias com mais de {LIMITE_DIA} tarefas para a mesma pessoa (considerando Planner + novo concurso).")
            for s in sobrecargas:
                st.markdown(f"""
                <div class="t-card" style="margin-bottom:4px; border-top:1px solid #E2E8F0; border-radius:8px;">
                    <span class="municipio">👤 {s['responsavel']}</span>
                    <span class="t-nome">📅 {s['data']} — {s['total_tarefas']} tarefas no total</span>
                    <span class="chip chip-venc">+{s['tarefas_novas']} novas · {s['tarefas_planner']} já no Planner</span>
                </div>
                """, unsafe_allow_html=True)

        if not conflitos and not sobrecargas:
            st.success("🎉 Nenhum conflito ou sobrecarga encontrado! Cronograma pode ser cadastrado.")

        st.divider()

        # ── CADASTRAR NO PLANNER ──────────────────────────────────────────────
        st.markdown("### 🚀 Cadastrar no Planner")
        st.caption("Após revisar os conflitos acima, cadastre as tarefas diretamente no Planner.")

        if st.button("🚀 Cadastrar todas as tarefas no Planner", type="primary"):
            plano_id, group_id = buscar_plano_id(token)
            if not plano_id:
                st.error("Não foi possível encontrar o plano PLANNER IBGP.")
            else:
                buckets = buscar_buckets_planner(token, plano_id)
                bucket_nome = df_novo["Nome do Bucket"].iloc[0].strip()

                # Cria bucket se não existir
                if bucket_nome not in buckets:
                    resp_bucket = requests.post(
                        "https://graph.microsoft.com/v1.0/planner/buckets",
                        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                        json={"name": bucket_nome, "planId": plano_id, "orderHint": " !"}
                    )
                    if resp_bucket.status_code == 201:
                        bucket_id = resp_bucket.json()["id"]
                        st.info(f"✅ Bucket '{bucket_nome}' criado.")
                    else:
                        st.error(f"Erro ao criar bucket: {resp_bucket.text}")
                        st.stop()
                else:
                    bucket_id = buckets[bucket_nome]

                # Cadastra tarefas
                sucesso, erro = 0, 0
                progress = st.progress(0)
                total = len(df_novo)

                for i, (_, row) in enumerate(df_novo.iterrows()):
                    due = row["Data de conclusão"]
                    inicio = row["Data de início"] if pd.notna(row.get("Data de início")) else due
                    due_str = due.strftime("%Y-%m-%dT03:00:00Z")
                    inicio_str = inicio.strftime("%Y-%m-%dT03:00:00Z")

                    payload = {
                        "planId": plano_id,
                        "bucketId": bucket_id,
                        "title": row["Nome da tarefa"].strip(),
                        "dueDateTime": due_str,
                        "startDateTime": inicio_str,
                    }
                    resp_t = requests.post(
                        "https://graph.microsoft.com/v1.0/planner/tasks",
                        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                        json=payload
                    )
                    if resp_t.status_code == 201:
                        sucesso += 1
                    else:
                        erro += 1
                    progress.progress((i + 1) / total)

                st.cache_data.clear()
                if sucesso:
                    st.success(f"✅ {sucesso} tarefa(s) cadastrada(s) no Planner com sucesso!")
                if erro:
                    st.warning(f"⚠️ {erro} tarefa(s) não foram cadastradas.")

    # ── GERADOR DE CRONOGRAMA COMPLETO ────────────────────────────────────────
    st.divider()
    st.markdown("### 🗓 Gerador de Cronograma Completo")
    st.caption("Informe a data de publicação e as fases do concurso para calcular todas as datas automaticamente, respeitando dias úteis, feriados e recesso IBGP.")

    from cronograma_engine import calcular_cronograma, is_util, is_recesso
    import pandas as pd
    from datetime import timedelta

    nome_novo_concurso = st.text_input("Nome do concurso (será o nome do bucket no Planner)", placeholder="Ex: MUNICÍPIO X - EDITAL Nº 01/2026 - CONCURSO PÚBLICO")

    tipo_certame = st.radio("Tipo de certame", ["CONCURSO", "PSS", "GUARDA"], horizontal=True)

    data_pub = st.date_input("Data de publicação do edital", value=date.today(), key="data_pub_gerador")

    col_insc1, col_insc2 = st.columns(2)
    with col_insc1:
        usar_data_manual = st.checkbox("Definir data de início das inscrições manualmente")
        data_inicio_inscricao = st.date_input("Data de início das inscrições", value=date.today(), key="data_inicio_insc") if usar_data_manual else None
    with col_insc2:
        dias_inscricao = st.number_input("Duração das inscrições (dias corridos)", min_value=1, max_value=60, value=10 if tipo_certame == "PSS" else 30, key="dias_insc")

    carga_horaria_curso = 0
    if tipo_certame == "GUARDA":
        carga_horaria_curso = st.number_input("Carga horária total do Curso de Formação (0 = sem curso)", min_value=0, max_value=2000, value=0, step=10, key="ch_curso")
        if carga_horaria_curso > 0:
            dias_curso = -(-carga_horaria_curso // 10)
            st.caption(f"📚 {carga_horaria_curso}h ÷ 10h/dia = **{dias_curso} dias úteis** de curso")

    col1, col2, col3 = st.columns(3)
    with col1:
        f_objetiva    = st.checkbox("Prova Objetiva", value=True)
        f_isencao     = st.checkbox("Isenção", value=True)
        f_inscricao   = st.checkbox("Inscrições", value=True)
        f_discursiva  = st.checkbox("Prova Discursiva")
        f_pratica     = st.checkbox("Prova Prática")
    with col2:
        f_taf         = st.checkbox("TAF / Capacidade Física")
        f_titulos     = st.checkbox("Prova de Títulos")
        f_psicologica = st.checkbox("Avaliação Psicológica")
        f_medica      = st.checkbox("Avaliação Médica")
    with col3:
        f_clinica     = st.checkbox("Avaliação Clínica")
        f_hetero      = st.checkbox("Heteroidentificação")
        f_entrevista  = st.checkbox("Entrevista Devolutiva")
        f_competencias = st.checkbox("Entrevista por Competências")
        f_sindicancia = st.checkbox("Sindicância Social") if tipo_certame == "GUARDA" else False
        concom        = st.checkbox("Concomitância Títulos + Prática/TAF") if f_titulos and (f_pratica or f_taf) else False

    if st.button("🗓 Calcular cronograma", type="primary", key="btn_calcular"):
        cronograma = calcular_cronograma(
            tipo_certame=tipo_certame,
            data_publicacao=data_pub,
            tem_objetiva=f_objetiva,
            tem_inscricao=f_inscricao,
            tem_isencao=f_isencao,
            tem_discursiva=f_discursiva,
            tem_pratica=f_pratica,
            tem_taf=f_taf,
            tem_titulos=f_titulos,
            tem_psicologica=f_psicologica,
            tem_medica=f_medica,
            tem_clinica=f_clinica,
            tem_hetero=f_hetero,
            tem_entrevista=f_entrevista,
            tem_competencias=f_competencias,
            tem_sindicancia=f_sindicancia,
            concomitancia_titulos_pratica=concom,
            data_inicio_inscricao=data_inicio_inscricao,
            dias_inscricao=int(dias_inscricao),
            carga_horaria_curso=int(carga_horaria_curso),
        )
        st.session_state["cronograma_gerado"] = cronograma
        st.session_state["nome_concurso_gerado"] = nome_novo_concurso

    if "cronograma_gerado" in st.session_state:
        cronograma = st.session_state["cronograma_gerado"]
        nome_concurso_gerado = st.session_state.get("nome_concurso_gerado", "")
        st.success(f"✅ {len(cronograma)} atividades calculadas!")

        df_cron = pd.DataFrame(cronograma)
        df_cron["data_inicio_fmt"] = df_cron["data_inicio"].apply(lambda d: d.strftime("%d/%m/%Y"))
        df_cron["data_fim_fmt"]    = df_cron["data_fim"].apply(lambda d: d.strftime("%d/%m/%Y"))
        # Cruza com Planner para detectar conflitos
        with st.spinner("Verificando conflitos com o Planner..."):
            tarefas_planner = buscar_tarefas(token)

        planner_rows = []
        for t in tarefas_planner:
            if t["data"] != "Sem data":
                try:
                    dt = datetime.strptime(t["data"], "%d/%m/%Y").date()
                    planner_rows.append({"tarefa": t["tarefa"], "data": dt, "municipio": t["municipio"]})
                except: pass
        df_planner_cron = pd.DataFrame(planner_rows) if planner_rows else pd.DataFrame(columns=["tarefa","data","municipio"])

        # Marca conflitos em cada tarefa do cronograma
        from cronograma_engine import is_util as _is_util, is_recesso as _is_recesso
        conflitos_cron = {}
        for row in cronograma:
            nome = row["atividade"]
            data_fim = row["data_fim"]
            match = df_planner_cron[(df_planner_cron["tarefa"] == nome) & (df_planner_cron["data"] == data_fim)]
            if not match.empty:
                conflitos_cron[row["seq"]] = match.iloc[0]["municipio"]

        # Verificação de sobrecarga por pessoa
        LIMITE_SOBRECARGA = 3
        sobrecarga_pessoa = {}
        for row in cronograma:
            nome_tarefa = row["atividade"]
            resp = ATRIBUICOES.get(nome_tarefa)
            if not resp:
                continue
            data_fim = row["data_fim"]
            # Conta tarefas do Planner para essa pessoa nesse dia
            planner_pessoa_dia = df_planner_cron[
                (df_planner_cron["responsavel"] == resp) &
                (df_planner_cron["data"] == data_fim)
            ] if "responsavel" in df_planner_cron.columns else pd.DataFrame()
            novas_pessoa_dia = [r for r in cronograma if ATRIBUICOES.get(r["atividade"]) == resp and r["data_fim"] == data_fim]
            total = len(planner_pessoa_dia) + len(novas_pessoa_dia)
            if total > LIMITE_SOBRECARGA:
                chave = f"{resp}|{data_fim.strftime('%d/%m/%Y')}"
                if chave not in sobrecarga_pessoa:
                    sobrecarga_pessoa[chave] = {"resp": resp, "data": data_fim.strftime("%d/%m/%Y"), "total": total}

        # Exibe tabela com indicação de conflitos
        total_conflitos = len(conflitos_cron)
        total_sobrecarga = len(sobrecarga_pessoa)
        col_m1, col_m2 = st.columns(2)
        if total_conflitos:
            col_m1.warning(f"⚠️ {total_conflitos} tarefa(s) com conflito de mesma atividade no Planner.")
        else:
            col_m1.success("✅ Sem conflitos de atividade!")
        if total_sobrecarga:
            col_m2.warning(f"🔴 {total_sobrecarga} dia(s) com sobrecarga por pessoa.")
        else:
            col_m2.success("✅ Sem sobrecarga por pessoa!")

        if sobrecarga_pessoa:
            st.markdown("##### 🔴 Dias sobrecarregados por pessoa")
            for s in sobrecarga_pessoa.values():
                st.markdown(f"- **{s['resp']}** em {s['data']} — {s['total']} tarefas no total")

        # Monta tabela com coluna de status
        rows_exib = []
        for row in cronograma:
            conflito = conflitos_cron.get(row["seq"])
            status = f"⚠️ Conflito com: {conflito}" if conflito else "✅ OK"
            rows_exib.append({
                "Seq": row["seq"],
                "Atividade": row["atividade"],
                "Data Início": row["data_inicio"].strftime("%d/%m/%Y"),
                "Data Fim": row["data_fim"].strftime("%d/%m/%Y"),
                "Status": status,
            })
        df_exib = pd.DataFrame(rows_exib)
        st.dataframe(df_exib, use_container_width=True, hide_index=True)

        # Sugere ajustes para conflitos com recálculo em cascata
        if conflitos_cron:
            st.markdown("#### 💡 Ajuste sugerido — recálculo em cascata")
            st.caption("O sistema identifica o primeiro conflito e recalcula todo o cronograma a partir dele, respeitando todas as regras IBGP.")

            from cronograma_engine import encontrar_primeira_data_livre

            # Pega o primeiro conflito na sequência
            primeiro_seq = min(conflitos_cron.keys())
            primeiro_row = next(t for t in cronograma if t["seq"] == primeiro_seq)
            datas_ocupadas = set(df_planner_cron[df_planner_cron["tarefa"] == primeiro_row["atividade"]]["data"].tolist())
            nova_data = encontrar_primeira_data_livre(
                primeiro_row["data_fim"], datas_ocupadas,
                tipo_certame=tipo_certame,
                nome_atividade=primeiro_row["atividade"]
            )

            st.markdown(f"**Primeiro conflito:** `{primeiro_row['atividade']}`")
            st.markdown(f"~~{primeiro_row['data_fim'].strftime('%d/%m/%Y')}~~ → **{nova_data.strftime('%d/%m/%Y')}**")
            st.caption("Todas as datas seguintes serão recalculadas em cascata a partir desta.")

            # Recalcula cronograma completo com nova data
            from cronograma_engine import calcular_cronograma as _calc
            deslocamento = nova_data - primeiro_row["data_fim"]
            data_pub_original = cronograma[0]["data_fim"]
            nova_data_pub = data_pub_original + deslocamento

            cronograma_ajustado = _calc(
                tipo_certame=tipo_certame,
                data_publicacao=nova_data_pub,
                tem_objetiva=f_objetiva,
                tem_inscricao=f_inscricao,
                tem_isencao=f_isencao,
                tem_discursiva=f_discursiva,
                tem_pratica=f_pratica,
                tem_taf=f_taf,
                tem_titulos=f_titulos,
                tem_psicologica=f_psicologica,
                tem_medica=f_medica,
                tem_clinica=f_clinica,
                tem_hetero=f_hetero,
                tem_entrevista=f_entrevista,
                tem_competencias=f_competencias,
                tem_sindicancia=f_sindicancia,
                concomitancia_titulos_pratica=concom,
            )

            st.session_state["cronograma_ajustado"] = cronograma_ajustado

            if st.button("✅ Usar cronograma recalculado", key="btn_usar_ajustadas"):
                st.session_state["cronograma_gerado"] = cronograma_ajustado
                st.rerun()

        # Botão cadastrar no Planner
        if nome_concurso_gerado:
            if st.button("🚀 Cadastrar cronograma no Planner", type="primary", key="btn_cad_cron"):
                plano_id, group_id = buscar_plano_id(token)
                if not plano_id:
                    st.error("Não foi possível encontrar o plano PLANNER IBGP.")
                else:
                    buckets = buscar_buckets_planner(token, plano_id)
                    bucket_nome = nome_concurso_gerado.strip()

                    if bucket_nome not in buckets:
                        resp_bucket = requests.post(
                            "https://graph.microsoft.com/v1.0/planner/buckets",
                            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                            json={"name": bucket_nome, "planId": plano_id, "orderHint": " !"}
                        )
                        if resp_bucket.status_code == 201:
                            bucket_id = resp_bucket.json()["id"]
                        else:
                            st.error(f"Erro ao criar bucket: {resp_bucket.text}")
                            st.stop()
                    else:
                        bucket_id = buckets[bucket_nome]

                    sucesso, erro = 0, 0
                    progress = st.progress(0)
                    total = len(cronograma)

                    for i, t in enumerate(cronograma):
                        due_str   = t["data_fim"].strftime("%Y-%m-%dT03:00:00Z")
                        inicio_str = t["data_inicio"].strftime("%Y-%m-%dT03:00:00Z")
                        payload = {
                            "planId": plano_id,
                            "bucketId": bucket_id,
                            "title": t["atividade"],
                            "dueDateTime": due_str,
                            "startDateTime": inicio_str,
                        }
                        resp_t = requests.post(
                            "https://graph.microsoft.com/v1.0/planner/tasks",
                            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                            json=payload
                        )
                        if resp_t.status_code == 201:
                            sucesso += 1
                        else:
                            erro += 1
                        progress.progress((i + 1) / total)

                    st.cache_data.clear()
                    if sucesso:
                        st.success(f"✅ {sucesso} tarefa(s) cadastrada(s) no Planner!")
                    if erro:
                        st.warning(f"⚠️ {erro} tarefa(s) não cadastradas.")
        else:
            st.info("Preencha o nome do concurso acima para habilitar o cadastro no Planner.")

    # ═══════════════════════════════════════════════════════════════════════════
    # SEÇÃO 3 — REAJUSTAR CRONOGRAMA
    # ═══════════════════════════════════════════════════════════════════════════
    st.divider()
    st.markdown("### 🔧 Reajustar Cronograma no Planner")
    st.caption("Selecione um concurso e ajuste as datas das tarefas já cadastradas no Planner.")

    # Busca todos os buckets disponíveis
    with st.spinner("Carregando concursos..."):
        try:
            plano_id_re, _ = buscar_plano_id(token)
            if plano_id_re:
                buckets_re = buscar_buckets_planner(token, plano_id_re)
                concurso_selecionado = st.selectbox(
                    "Selecione o concurso:",
                    options=[""] + sorted(buckets_re.keys()),
                    key="reajuste_concurso"
                )
            else:
                st.error("Não foi possível carregar os concursos.")
                concurso_selecionado = ""
        except:
            st.error("Erro ao carregar concursos.")
            concurso_selecionado = ""

    if concurso_selecionado:
        bucket_id_re = buckets_re[concurso_selecionado]

        # Busca tarefas do bucket selecionado
        @st.cache_data(ttl=60, show_spinner=False)
        def buscar_tarefas_bucket(token, bucket_id):
            headers = {"Authorization": f"Bearer {token}"}
            results = []
            next_url = f"https://graph.microsoft.com/v1.0/planner/buckets/{bucket_id}/tasks"
            while next_url:
                resp = requests.get(next_url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                results.extend(data.get("value", []))
                next_url = data.get("@odata.nextLink")
            resultado = []
            for t in results:
                if t.get("percentComplete", 0) == 100:
                    continue
                due = t.get("dueDateTime")
                start = t.get("startDateTime")
                data_fim_fmt = ""
                data_ini_fmt = ""
                if due:
                    dt = datetime.fromisoformat(due.replace("Z", "+00:00")).replace(tzinfo=None)
                    data_fim_fmt = dt.strftime("%d/%m/%Y")
                if start:
                    dt = datetime.fromisoformat(start.replace("Z", "+00:00")).replace(tzinfo=None)
                    data_ini_fmt = dt.strftime("%d/%m/%Y")
                resultado.append({
                    "id": t["id"],
                    "titulo": t.get("title", ""),
                    "data_ini": data_ini_fmt,
                    "data_fim": data_fim_fmt,
                    "start_iso": start or "",
                    "due_iso": due or "",
                })
            return sorted(resultado, key=lambda x: x["due_iso"])

        with st.spinner("Carregando tarefas..."):
            tarefas_bucket = buscar_tarefas_bucket(token, bucket_id_re)

        if not tarefas_bucket:
            st.info("Nenhuma tarefa em aberto neste concurso.")
        else:
            import pandas as pd
            from cronograma_engine import is_util, proximo_util

            st.caption(f"**{len(tarefas_bucket)} tarefas em aberto** — edite as datas na coluna 'Nova Data ✏️' e clique em Salvar.")

            df_re = pd.DataFrame([{
                "id": t["id"],
                "Tarefa": t["titulo"],
                "Data Início Atual": t["data_ini"],
                "Data Fim Atual": t["data_fim"],
                "Nova Data Início": datetime.strptime(t["data_ini"], "%d/%m/%Y").date() if t["data_ini"] else None,
                "Nova Data Fim": datetime.strptime(t["data_fim"], "%d/%m/%Y").date() if t["data_fim"] else date.today(),
                "start_iso": t["start_iso"],
                "due_iso": t["due_iso"],
            } for t in tarefas_bucket])

            df_editado = st.data_editor(
                df_re[["Tarefa", "Data Início Atual", "Data Fim Atual", "Nova Data Início", "Nova Data Fim"]],
                column_config={
                    "Tarefa": st.column_config.TextColumn("Tarefa", disabled=True, width="large"),
                    "Data Início Atual": st.column_config.TextColumn("Início Atual", disabled=True, width="small"),
                    "Data Fim Atual": st.column_config.TextColumn("Fim Atual", disabled=True, width="small"),
                    "Nova Data Início": st.column_config.DateColumn("Nova Início ✏️", width="small", format="DD/MM/YYYY"),
                    "Nova Data Fim": st.column_config.DateColumn("Nova Fim ✏️", width="small", format="DD/MM/YYYY"),
                },
                hide_index=True,
                use_container_width=True,
                key="editor_datas"
            )

            alteradas = []
            for i, row in df_editado.iterrows():
                fim_orig = df_re.iloc[i]["Nova Data Fim"]
                fim_nova = row["Nova Data Fim"]
                ini_orig = df_re.iloc[i]["Nova Data Início"]
                ini_nova = row["Nova Data Início"]
                if fim_nova != fim_orig or ini_nova != ini_orig:
                    alteradas.append({
                        "idx": i, "id": df_re.iloc[i]["id"],
                        "titulo": row["Tarefa"],
                        "data_orig": fim_orig, "data_nova": fim_nova,
                        "ini_orig": ini_orig, "ini_nova": ini_nova,
                        "due_iso": df_re.iloc[i]["due_iso"],
                        "start_iso": df_re.iloc[i]["start_iso"],
                    })

            if alteradas:
                st.caption(f"**{len(alteradas)} tarefa(s) com data alterada**")
                modo = st.radio(
                    "Para as tarefas posteriores à primeira alteração:",
                    ["Manter datas originais", "Recalcular em cascata (mesmo deslocamento)"],
                    key="reajuste_modo", horizontal=True
                )
                if st.button("🔧 Salvar ajustes no Planner", type="primary", key="btn_reajuste"):
                    tarefas_para_salvar = list(alteradas)
                    if modo == "Recalcular em cascata (mesmo deslocamento)":
                        primeira = min(alteradas, key=lambda x: x["idx"])
                        deslocamento = primeira["data_nova"] - primeira["data_orig"]
                        for i, t in enumerate(tarefas_bucket):
                            if i <= primeira["idx"]: continue
                            if any(a["id"] == t["id"] for a in alteradas): continue
                            if not t["due_iso"]: continue
                            dt_orig = datetime.fromisoformat(t["due_iso"].replace("Z", "+00:00")).replace(tzinfo=None).date()
                            dt_nova = dt_orig + deslocamento
                            if not is_util(dt_nova):
                                dt_nova = proximo_util(dt_nova)
                            dt_ini_orig = datetime.fromisoformat(t["start_iso"].replace("Z", "+00:00")).replace(tzinfo=None).date() if t.get("start_iso") else None
                            dt_ini_nova = (dt_ini_orig + deslocamento) if dt_ini_orig else None
                            if dt_ini_nova and not is_util(dt_ini_nova):
                                dt_ini_nova = proximo_util(dt_ini_nova)
                            tarefas_para_salvar.append({"id": t["id"], "titulo": t["titulo"], "data_nova": dt_nova, "ini_nova": dt_ini_nova, "due_iso": t["due_iso"], "start_iso": t.get("start_iso","")})

                    progress = st.progress(0)
                    sucesso, erro = 0, 0
                    for i, t in enumerate(tarefas_para_salvar):
                        payload = {"dueDateTime": f"{t['data_nova'].strftime('%Y-%m-%d')}T03:00:00Z"}
                        if t.get("ini_nova"):
                            payload["startDateTime"] = f"{t['ini_nova'].strftime('%Y-%m-%d')}T03:00:00Z"
                        result = graph_patch(token, f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}", payload)
                        if result in [200, 204]: sucesso += 1
                        else: erro += 1
                        progress.progress((i + 1) / len(tarefas_para_salvar))
                    buscar_tarefas_bucket.clear()
                    st.cache_data.clear()
                    if sucesso: st.success(f"✅ {sucesso} tarefa(s) atualizada(s) no Planner!")
                    if erro: st.warning(f"⚠️ {erro} tarefa(s) não atualizadas.")
                    st.rerun()
            else:
                st.info("Edite as datas na coluna 'Nova Data ✏️' para habilitar o ajuste.")
