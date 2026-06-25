import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import urlencode
import requests, json

CLIENT_ID    = "cf858739-80c5-4bf0-bc5c-6f5b0cefb70d"
TENANT_ID    = "e1362ab7-0546-4f12-9f44-0867415479b9"
REDIRECT_URI = "https://ibgp-minhas-tarefas-jkdmypmipxemkvhh6c5vjv.streamlit.app/"
SCOPES       = "Tasks.ReadWrite Group.Read.All User.Read offline_access"
NOME_PLANO   = "PLANNER IBGP"

NOME_MAP = {
    "execução": "Laryssa", "laryssa": "Laryssa",
    "lorena": "Lorena",
    "natália": "Natália", "natalia": "Natália",
    "manuela": "Manuela", "manu": "Manuela",
    "fabiano": "Fabiano", "fabiano costa barreiros": "Fabiano",
}

st.set_page_config(page_title="IBGP · Minhas Tarefas", page_icon="✅", layout="wide")
st.markdown("""<style>
header[data-testid='stHeader']{display:none}
.block-container{padding:0!important;max-width:100%!important}
footer{display:none}
#MainMenu{display:none}
</style>""", unsafe_allow_html=True)

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

def renovar_token(rt):
    resp = requests.post(f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"client_id": CLIENT_ID, "client_secret": st.secrets["CLIENT_SECRET"],
              "grant_type": "refresh_token", "refresh_token": rt, "scope": SCOPES})
    return resp.json()

# ── AUTH ──────────────────────────────────────────────────────────────────────
params = st.query_params
code = params.get("code")

if "access_token" not in st.session_state:
    if code:
        with st.spinner("Autenticando..."):
            td = trocar_codigo(code)
            if "access_token" in td:
                st.session_state["access_token"] = td["access_token"]
                st.session_state["refresh_token"] = td.get("refresh_token")
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"Erro: {td.get('error_description','')}")
    else:
        st.markdown("""
        <div style="display:flex;height:100vh;align-items:center;justify-content:center;background:#eef1f6;font-family:system-ui,sans-serif">
          <div style="background:#fff;border:1px solid #e2e7ef;border-radius:16px;padding:3rem 2.5rem;text-align:center;max-width:380px;box-shadow:0 4px 24px rgba(16,30,54,0.08)">
            <div style="width:52px;height:52px;background:linear-gradient(135deg,#2f6cc4,#1f4e8c);border-radius:13px;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:19px;margin:0 auto 1.25rem">IB</div>
            <h2 style="margin:0 0 .4rem;font-size:1.2rem;font-weight:700;color:#1f2a3d">IBGP · Minhas Tarefas</h2>
            <p style="color:#7a869c;font-size:.875rem;margin:0 0 1.5rem">Entre com sua conta Microsoft para acessar.</p>
          </div>
        </div>""", unsafe_allow_html=True)
        col1,col2,col3 = st.columns([1,1,1])
        with col2:
            st.link_button("🔐 Entrar com Microsoft", auth_url(), use_container_width=True)
        st.stop()

token = st.session_state["access_token"]

# ── USUÁRIO ───────────────────────────────────────────────────────────────────
try:
    me = requests.get("https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token}"}).json()
    display_name = me.get("displayName","")
    first_name = display_name.split()[0] if display_name else "Usuário"
    nome_interno = NOME_MAP.get(first_name.lower(), NOME_MAP.get(display_name.lower(), first_name))
except:
    if st.session_state.get("refresh_token"):
        td = renovar_token(st.session_state["refresh_token"])
        if "access_token" in td:
            st.session_state["access_token"] = td["access_token"]
            st.rerun()
    st.error("Sessão expirada.")
    if st.button("Entrar novamente"):
        del st.session_state["access_token"]
        st.rerun()
    st.stop()

is_gestora    = nome_interno == "Manuela"
is_cronograma = nome_interno == "Fabiano"
perfil = "Gestora · Equipe IBGP" if is_gestora else ("Cronograma · IBGP" if is_cronograma else "Equipe IBGP")

# ── DADOS DO PLANNER (buscados no Python) ────────────────────────────────────
@st.cache_data(ttl=180, show_spinner=False)
def buscar_tudo(token):
    """Busca plano, buckets e tarefas — retorna JSON para o JS."""
    def g(url):
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        r.raise_for_status()
        return r.json()
    def g_all(url):
        results, next_url = [], url
        while next_url:
            d = requests.get(next_url, headers={"Authorization": f"Bearer {token}"}).json()
            results.extend(d.get("value", []))
            next_url = d.get("@odata.nextLink")
        return results

    # Busca plano
    plano_id = None
    groups = g_all("https://graph.microsoft.com/v1.0/me/memberOf")
    for grp in groups:
        gid = grp.get("id")
        if not gid: continue
        try:
            plans = g(f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans")
            for p in plans.get("value", []):
                if NOME_PLANO.upper() in p.get("title","").upper():
                    plano_id = p["id"]
                    break
        except: continue
        if plano_id: break

    if not plano_id:
        return {"tarefas": [], "buckets": {}, "planoId": None}

    # Buckets
    bd = g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets")
    buckets = {b["id"]: b["name"] for b in bd.get("value", [])}

    # Tarefas
    todas = g_all(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/tasks")

    # Lê ATRIBUICOES do arquivo
    atrib_raw = open("/mount/src/ibgp-minhas-tarefas/atribuicoes.js").read()
    import re
    entries = re.findall(r'"([^"]+)":\s*"([^"]+)"', atrib_raw)
    ATRIBUICOES = {k: v for k, v in entries}

    tarefas = []
    for t in todas:
        if t.get("percentComplete", 0) == 100: continue
        nome = (t.get("title") or "").strip()
        resp = ATRIBUICOES.get(nome)
        if not resp: continue
        tarefas.append({
            "id": t["id"],
            "municipio": buckets.get(t.get("bucketId",""), "—"),
            "tarefa": nome,
            "responsavel": resp,
            "due": t.get("dueDateTime"),
        })

    return {"tarefas": tarefas, "buckets": buckets, "planoId": plano_id}

with st.spinner("🔄 Carregando tarefas..."):
    dados = buscar_tudo(token)

# ── HTML ──────────────────────────────────────────────────────────────────────
html = open("/mount/src/ibgp-minhas-tarefas/template.html").read()
atrib_js = open("/mount/src/ibgp-minhas-tarefas/atribuicoes.js").read()

config_js = f"""
const TOKEN = {json.dumps(token)};
const IS_GESTORA = {'true' if is_gestora else 'false'};
const IS_CRONOGRAMA = {'true' if is_cronograma else 'false'};
const NOME_USUARIO = {json.dumps(nome_interno)};
const DADOS_INICIAIS = {json.dumps(dados)};
"""

html = html.replace("// PLACEHOLDER_TOKEN", "// injected")
html = html.replace("// PLACEHOLDER_CONFIG", config_js)
html = html.replace("// PLACEHOLDER_ATRIB", atrib_js)

init_js = f"""
document.getElementById('topbar-title').textContent = 'Olá, {nome_interno}! 👋';
document.getElementById('user-avatar').textContent = '{nome_interno[0].upper()}';
document.getElementById('user-name-display').textContent = {json.dumps(nome_interno)};
document.getElementById('user-role-display').textContent = {json.dumps(perfil)};
document.getElementById('page-tarefas-title').textContent = {'JSON.stringify("Visão da Gestora")' if is_gestora else 'JSON.stringify("Minhas Tarefas")'};
{'document.getElementById("sel-pessoa-wrap").style.display = "block";' if is_gestora else ''}
"""
html = html.replace("loadTarefas();", f"{init_js}\nloadTarefas();")

components.html(html, height=870, scrolling=False)
