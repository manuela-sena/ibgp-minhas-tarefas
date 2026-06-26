import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import urlencode
import requests, json, re
from datetime import datetime, date

CLIENT_ID    = "cf858739-80c5-4bf0-bc5c-6f5b0cefb70d"
TENANT_ID    = "e1362ab7-0546-4f12-9f44-0867415479b9"
REDIRECT_URI = "https://ibgp-minhas-tarefas-jkdmypmipxemkvhh6c5vjv.streamlit.app/"
SCOPES       = "Tasks.ReadWrite Group.Read.All User.Read offline_access"
NOME_PLANO   = "PLANNER IBGP"

NOME_MAP = {
    "execução":"Laryssa","laryssa":"Laryssa","lorena":"Lorena",
    "natália":"Natália","natalia":"Natália",
    "manuela":"Manuela","manu":"Manuela",
    "fabiano":"Fabiano","fabiano costa barreiros":"Fabiano",
}

_atrib_raw = open("/mount/src/ibgp-minhas-tarefas/atribuicoes.js").read()
ATRIBUICOES = {k: v for k, v in re.findall(r'"([^"]+)":\s*"([^"]+)"', _atrib_raw)}

st.set_page_config(page_title="IBGP · Minhas Tarefas", page_icon="✅", layout="wide")

# Esconde todo o chrome do Streamlit
st.markdown("""<style>
header[data-testid="stHeader"]{display:none}
footer{display:none}
#MainMenu{display:none}
.stApp{overflow:hidden}
.block-container{padding:0!important;max-width:100%!important}
[data-testid="stAppViewContainer"]{padding:0!important}
[data-testid="stVerticalBlock"]{gap:0!important;padding:0!important}
</style>""", unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────────────
def auth_url():
    p = {"client_id":CLIENT_ID,"response_type":"code","redirect_uri":REDIRECT_URI,
         "scope":SCOPES,"response_mode":"query"}
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?" + urlencode(p)

def trocar_codigo(code):
    r = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"client_id":CLIENT_ID,"client_secret":st.secrets["CLIENT_SECRET"],
              "grant_type":"authorization_code","code":code,
              "redirect_uri":REDIRECT_URI,"scope":SCOPES})
    return r.json()

params = st.query_params
code   = params.get("code")

if "access_token" not in st.session_state:
    if code:
        with st.spinner("Autenticando..."):
            td = trocar_codigo(code)
        if "access_token" in td:
            st.session_state["access_token"]  = td["access_token"]
            st.session_state["refresh_token"] = td.get("refresh_token")
            st.query_params.clear()
            st.rerun()
        else:
            st.error(f"Erro: {td.get('error_description','')}")
    else:
        st.markdown("""
<div style="display:flex;height:100vh;align-items:center;justify-content:center;background:#eef1f6">
  <div style="background:#fff;border:1px solid #e2e7ef;border-radius:16px;padding:3rem;
              text-align:center;max-width:360px;box-shadow:0 4px 24px rgba(16,30,54,0.08)">
    <div style="width:52px;height:52px;background:linear-gradient(135deg,#2f6cc4,#1f4e8c);
                border-radius:13px;display:flex;align-items:center;justify-content:center;
                font-weight:800;color:#fff;font-size:19px;margin:0 auto 1.2rem">IB</div>
    <h2 style="margin:0 0 .4rem;font-size:1.15rem;font-weight:700;color:#1f2a3d">IBGP · Minhas Tarefas</h2>
    <p style="color:#7a869c;font-size:.875rem;margin:0 0 1.8rem">Entre com sua conta Microsoft para continuar.</p>
  </div>
</div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.link_button("🔐 Entrar com Microsoft", auth_url(), use_container_width=True)
    st.stop()

token = st.session_state["access_token"]

# ── USUÁRIO ───────────────────────────────────────────────────────────
try:
    me           = requests.get("https://graph.microsoft.com/v1.0/me",
                                headers={"Authorization":f"Bearer {token}"}).json()
    display_name = me.get("displayName","")
    first_name   = display_name.split()[0] if display_name else "Usuário"
    nome_interno = NOME_MAP.get(first_name.lower(),
                   NOME_MAP.get(display_name.lower(), first_name))
except Exception:
    st.error("Sessão expirada.")
    st.button("Entrar novamente", on_click=lambda: st.session_state.pop("access_token"))
    st.stop()

is_gestora   = nome_interno == "Manuela"
is_cronograma = nome_interno == "Fabiano"
perfil = ("Gestora · Equipe IBGP" if is_gestora
          else ("Cronograma · IBGP" if is_cronograma else "Equipe IBGP"))

# ── BUSCAR TAREFAS ────────────────────────────────────────────────────
def g(url):
    r = requests.get(url, headers={"Authorization":f"Bearer {token}"})
    r.raise_for_status(); return r.json()

def g_all(url):
    res, nxt = [], url
    while nxt:
        d = requests.get(nxt, headers={"Authorization":f"Bearer {token}"}).json()
        res.extend(d.get("value",[])); nxt = d.get("@odata.nextLink")
    return res

@st.cache_data(ttl=180, show_spinner=False)
def buscar_tarefas(token):
    plano_id = None
    for grp in g_all("https://graph.microsoft.com/v1.0/me/memberOf"):
        gid = grp.get("id")
        if not gid: continue
        try:
            for p in g(f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans").get("value",[]):
                if NOME_PLANO.upper() in p.get("title","").upper():
                    plano_id = p["id"]; break
        except Exception: pass
        if plano_id: break
    if not plano_id: return [], {}, None

    buckets = {b["id"]:b["name"]
               for b in g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets").get("value",[])}
    tarefas = []
    for t in g_all(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/tasks"):
        if t.get("percentComplete",0) == 100: continue
        nome = (t.get("title") or "").strip()
        resp = ATRIBUICOES.get(nome)
        if not resp: continue
        due = t.get("dueDateTime")
        due_iso = due or ""
        dt = None
        if due:
            try: dt = datetime.fromisoformat(due.replace("Z","+00:00")).replace(tzinfo=None)
            except Exception: pass
        tarefas.append({
            "id": t["id"],
            "municipio": buckets.get(t.get("bucketId",""),"—"),
            "tarefa": nome,
            "responsavel": resp,
            "due": due_iso,
        })
    return tarefas, buckets, plano_id

with st.spinner("Carregando tarefas..."):
    tarefas, buckets, plano_id = buscar_tarefas(token)

# ── MONTAR DADOS_INICIAIS para o JS ──────────────────────────────────
dados_iniciais = json.dumps({
    "tarefas": tarefas,
    "buckets": buckets,
    "planoId": plano_id,
})

# ── LER TEMPLATE ─────────────────────────────────────────────────────
with open("/mount/src/ibgp-minhas-tarefas/template.html", "r", encoding="utf-8") as f:
    html = f.read()

# ── INJETAR VARIÁVEIS ────────────────────────────────────────────────
html = html.replace(
    "// PLACEHOLDER_TOKEN",
    f"const TOKEN = {json.dumps(token)};"
)
html = html.replace(
    "// PLACEHOLDER_CONFIG",
    f"""const IS_GESTORA    = {'true' if is_gestora   else 'false'};
const IS_CRONOGRAMA = {'true' if is_cronograma else 'false'};
const NOME_USUARIO  = {json.dumps(nome_interno)};
const DADOS_INICIAIS = {dados_iniciais};"""
)
html = html.replace(
    "// PLACEHOLDER_ATRIB",
    ""  # atribuições já estão no Python via ATRIBUICOES
)

# Ajustar altura para preencher a tela toda
components.html(html, height=900, scrolling=False)
