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
is_gestora = user_name.lower() in ["manuela", "manu"]

if is_gestora:
    st.markdown("### 👥 Visão da Gestora")
    filtro_pessoa = st.selectbox("Visualizar tarefas de:", ["Toda a equipe"] + EQUIPE)
else:
    filtro_pessoa = user_name.title()
    st.caption(f"Exibindo suas tarefas — {filtro_pessoa}")

# ─── DADOS ────────────────────────────────────────────────────────────────────
with st.spinner("Buscando tarefas..."):
    todas = buscar_tarefas(token)

if filtro_pessoa != "Toda a equipe":
    tarefas = [t for t in todas if t["responsavel"].lower() == filtro_pessoa.lower()]
else:
    tarefas = todas

if not tarefas:
    st.success("🎉 Nenhuma tarefa pendente encontrada!")
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
    if t["dias"] <= 7: return f'<span class="chip chip-semana">{t["dias"]}d restantes</span>'
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
