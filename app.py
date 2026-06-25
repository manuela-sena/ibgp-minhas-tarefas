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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.header {
    background: linear-gradient(135deg, #1B3A6B 0%, #2D5FA8 100%);
    padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; color: white;
}
.header h1 { font-size: 1.5rem; font-weight: 700; margin: 0; }
.header p  { color: #B8D0F0; font-size: 0.875rem; margin: 0.25rem 0 0; }
.login-box {
    background: #F0F4FA; border: 1px solid #D0DAEA; border-radius: 12px;
    padding: 3rem 2rem; text-align: center; max-width: 420px; margin: 4rem auto;
}
.hoje-h    { background:#1B3A6B; color:white; padding:.5rem 1rem; border-radius:8px 8px 0 0; font-size:.8rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
.semana-h  { background:#2D5FA8; color:white; padding:.5rem 1rem; border-radius:8px 8px 0 0; font-size:.8rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
.futuro-h  { background:#4A5568; color:white; padding:.5rem 1rem; border-radius:8px 8px 0 0; font-size:.8rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
.vencida-h { background:#C53030; color:white; padding:.5rem 1rem; border-radius:8px 8px 0 0; font-size:.8rem; font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
.t-card { background:white; border:1px solid #E2E8F0; border-top:none; padding:.9rem 1.2rem; display:flex; align-items:center; gap:1rem; font-size:.875rem; }
.t-card:last-child { border-radius:0 0 8px 8px; }
.municipio { color:#2B6CB0; font-weight:600; min-width:220px; font-size:.8rem; text-transform:uppercase; }
.t-nome { color:#2D3748; flex:1; }
.chip { padding:.25rem .75rem; border-radius:20px; font-size:.8rem; font-weight:600; white-space:nowrap; }
.chip-hoje   { background:#FFF9DB; color:#744210; border:1px solid #F6E05E; }
.chip-semana { background:#FFFBEB; color:#B7791F; border:1px solid #F6AD55; }
.chip-ok     { background:#EBF8FF; color:#2B6CB0; border:1px solid #90CDF4; }
.chip-venc   { background:#FFF5F5; color:#C53030; border:1px solid #FC8181; }
.pessoa-tag  { font-size:.75rem; font-weight:600; padding:.15rem .5rem; border-radius:4px; background:#EDF2F7; color:#4A5568; }
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

@st.cache_data(ttl=300, show_spinner=False)
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

st.markdown(f'<div class="header"><h1>✅ Olá, {user_name}!</h1><p>Tarefas da equipe · {hoje_str}</p></div>', unsafe_allow_html=True)

col_r, col_u = st.columns([8,1])
with col_u:
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
    with st.spinner("Buscando tarefas..."):
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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", len(tarefas))
    c2.metric("⚠️ Vencidas", len(vencidas))
    c3.metric("📅 Hoje", len(hoje_list))
    c4.metric("📆 Próximos 7 dias", len(semana))

    st.divider()

    # ─── RENDER ───────────────────────────────────────────────────────────────────
    def chip(t):
        if t["dias"] is None: return '<span class="chip chip-ok">Sem data</span>'
        if t["dias"] < 0: return f'<span class="chip chip-venc">Venceu há {abs(t["dias"])}d</span>'
        if t["dias"] == 0: return '<span class="chip chip-hoje">⚡ Hoje</span>'
        if t["dias"] <= 7: return f'<span class="chip chip-semana">{t["data"]} · {t["dias"]}d restantes</span>'
        return f'<span class="chip chip-ok">{t["data"]} · {t["dias"]}d</span>'

    def render_grupo(titulo, classe, lista, show_pessoa=False):
        if not lista: return
        st.markdown(f'<div class="{classe}">{titulo} · {len(lista)} tarefa(s)</div>', unsafe_allow_html=True)
        for t in lista:
            pessoa_tag = f'<span class="pessoa-tag">{t["responsavel"]}</span>' if show_pessoa else ""
            col_card, col_btn = st.columns([10, 1])
            with col_card:
                st.markdown(f'''<div class="t-card">
                    <span class="municipio">🏛 {t["municipio"]}</span>
                    <span class="t-nome">{pessoa_tag} {t["tarefa"]}</span>
                    {chip(t)}
                </div>''', unsafe_allow_html=True)
            with col_btn:
                if st.button("✅", key=f"ok_{t['id']}", help="Marcar como concluída"):
                    graph_patch(token, f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}", {"percentComplete": 100})
                    st.cache_data.clear()
                    st.rerun()

    show_pessoa = (filtro_pessoa == "Toda a equipe")
    render_grupo("⚠️ VENCIDAS", "vencida-h", vencidas, show_pessoa)
    if vencidas: st.write("")
    render_grupo("⚡ HOJE", "hoje-h", hoje_list, show_pessoa)
    if hoje_list: st.write("")
    render_grupo("📆 PRÓXIMOS 7 DIAS", "semana-h", semana, show_pessoa)
    if semana: st.write("")
    render_grupo("🗓 FUTURAS", "futuro-h", futuras, show_pessoa)

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

        # Busca ID do plano PLANNER IBGP
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
    
    tipo_certame = st.radio("Tipo de certame", ["CONCURSO/PSP", "GUARDA"], horizontal=True)
    
    data_pub = st.date_input("Data de publicação do edital", value=date.today(), key="data_pub_gerador")

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

        # Exibe tabela com indicação de conflitos
        total_conflitos = len(conflitos_cron)
        if total_conflitos:
            st.warning(f"⚠️ {total_conflitos} tarefa(s) com conflito de data com outros concursos no Planner.")
        else:
            st.success("✅ Nenhum conflito encontrado com o Planner!")

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
