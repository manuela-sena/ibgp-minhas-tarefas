import streamlit as st
import requests
from datetime import datetime, date
from urllib.parse import urlencode

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CLIENT_ID     = "cf858739-80c5-4bf0-bc5c-6f5b0cefb70d"
TENANT_ID     = "e1362ab7-0546-4f12-9f44-0867415479b9"
REDIRECT_URI  = "COLE_AQUI_A_URL_DO_NOVO_APP"   # ex: https://ibgp-tarefas.streamlit.app/
SCOPES        = "Tasks.ReadWrite Group.Read.All User.Read offline_access"
NOME_PLANO    = "PLANNER IBGP"

# ─── PÁGINA ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IBGP · Minhas Tarefas",
    page_icon="✅",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.header {
    background: linear-gradient(135deg, #1B3A6B 0%, #2D5FA8 100%);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    color: white;
}
.header h1 { font-size: 1.5rem; font-weight: 700; margin: 0; }
.header p  { color: #B8D0F0; font-size: 0.875rem; margin: 0.25rem 0 0; }

.login-box {
    background: #F0F4FA;
    border: 1px solid #D0DAEA;
    border-radius: 12px;
    padding: 3rem 2rem;
    text-align: center;
    max-width: 420px;
    margin: 4rem auto;
}
.login-box h2 { color: #1B3A6B; font-size: 1.2rem; margin-bottom: 0.5rem; }
.login-box p  { color: #5A6A80; font-size: 0.9rem; margin-bottom: 1.5rem; }

.hoje-header {
    background: #1B3A6B;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px 8px 0 0;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.semana-header {
    background: #2D5FA8;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px 8px 0 0;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.futuro-header {
    background: #4A5568;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px 8px 0 0;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.vencida-header {
    background: #C53030;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 8px 8px 0 0;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.tarefa-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-top: none;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
}
.tarefa-card:last-child { border-radius: 0 0 8px 8px; }
.tarefa-card:hover { background: #F7FAFC; }

.municipio {
    color: #2B6CB0;
    font-weight: 600;
    min-width: 200px;
    font-size: 0.8rem;
    text-transform: uppercase;
}
.tarefa-nome {
    color: #2D3748;
    flex: 1;
}
.chip {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
}
.chip-hoje    { background: #FFF9DB; color: #744210; border: 1px solid #F6E05E; }
.chip-semana  { background: #FFFBEB; color: #B7791F; border: 1px solid #F6AD55; }
.chip-ok      { background: #EBF8FF; color: #2B6CB0; border: 1px solid #90CDF4; }
.chip-vencida { background: #FFF5F5; color: #C53030; border: 1px solid #FC8181; }

.empty-state {
    text-align: center;
    padding: 3rem;
    color: #718096;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─── AUTH ─────────────────────────────────────────────────────────────────────

def auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "response_mode": "query",
    }
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?" + urlencode(params)

def trocar_codigo(code):
    resp = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": st.secrets["CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
        }
    )
    return resp.json()

def renovar_token(refresh_token):
    resp = requests.post(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": st.secrets["CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": SCOPES,
        }
    )
    return resp.json()

# ─── GRAPH ────────────────────────────────────────────────────────────────────

def graph_get(token, url):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def graph_get_all(token, url):
    headers = {"Authorization": f"Bearer {token}"}
    results = []
    next_url = url
    while next_url:
        resp = requests.get(next_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        results.extend(data.get("value", []))
        next_url = data.get("@odata.nextLink")
    return results

@st.cache_data(ttl=300, show_spinner=False)
def buscar_minhas_tarefas(token, user_id, _cache_key=0):
    # Busca planos
    groups = graph_get(token, "https://graph.microsoft.com/v1.0/me/memberOf")
    planos = []
    for g in groups.get("value", []):
        gid = g.get("id")
        if not gid:
            continue
        try:
            result = graph_get(token, f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans")
            for p in result.get("value", []):
                if NOME_PLANO.upper() in p.get("title", "").upper():
                    planos.append({"id": p["id"], "title": p.get("title", "")})
        except:
            continue

    tarefas = []
    for plano in planos:
        buckets_data = graph_get(token, f"https://graph.microsoft.com/v1.0/planner/plans/{plano['id']}/buckets")
        buckets = {b["id"]: b["name"] for b in buckets_data.get("value", [])}

        todas = graph_get_all(token, f"https://graph.microsoft.com/v1.0/planner/plans/{plano['id']}/tasks")
        for t in todas:
            # Ignora concluídas
            if t.get("percentComplete", 0) == 100:
                continue
            # Filtra por tarefas atribuídas ao usuário logado
            assignments = t.get("assignments", {})
            if user_id not in assignments:
                continue

            nome = t.get("title", "")
            bucket = buckets.get(t.get("bucketId", ""), "—")
            due = t.get("dueDateTime")
            data_fmt = "Sem data"
            dias = None
            if due:
                dt = datetime.fromisoformat(due.replace("Z", "+00:00")).replace(tzinfo=None)
                data_fmt = dt.strftime("%d/%m/%Y")
                dias = (dt.date() - date.today()).days

            tarefas.append({
                "municipio": bucket,
                "tarefa": nome,
                "data": data_fmt,
                "dias": dias,
            })

    # Ordena: vencidas primeiro, depois por data
    def sort_key(x):
        if x["dias"] is None:
            return (2, "9999")
        if x["dias"] < 0:
            return (0, str(x["dias"]).zfill(6))
        return (1, str(x["dias"]).zfill(6))

    return sorted(tarefas, key=sort_key)

# ─── ESTADO DE AUTH ───────────────────────────────────────────────────────────

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
        st.markdown("""
        <div class="login-box">
            <h2>✅ IBGP · Minhas Tarefas</h2>
            <p>Entre com sua conta do IBGP para ver suas tarefas do Planner de forma organizada.</p>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            st.link_button("🔐 Entrar com Microsoft", auth_url(), use_container_width=True)
        st.stop()

token = st.session_state["access_token"]

# Busca info do usuário logado
try:
    me = graph_get(token, "https://graph.microsoft.com/v1.0/me")
    user_id = me["id"]
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

hoje = date.today().strftime("%d/%m/%Y — %A").replace(
    "Monday","Segunda").replace("Tuesday","Terça").replace("Wednesday","Quarta").replace(
    "Thursday","Quinta").replace("Friday","Sexta").replace("Saturday","Sábado").replace("Sunday","Domingo")

st.markdown(f"""
<div class="header">
    <h1>✅ Olá, {user_name}!</h1>
    <p>Suas tarefas no Planner IBGP · {hoje}</p>
</div>
""", unsafe_allow_html=True)

col_info, col_refresh = st.columns([8, 1])
with col_refresh:
    if st.button("↻ Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ─── DADOS ────────────────────────────────────────────────────────────────────

with st.spinner("Buscando suas tarefas..."):
    tarefas = buscar_minhas_tarefas(token, user_id)

if not tarefas:
    st.markdown('<div class="empty-state">🎉 Nenhuma tarefa pendente encontrada no Planner!</div>', unsafe_allow_html=True)
    st.stop()

# Agrupa
vencidas  = [t for t in tarefas if t["dias"] is not None and t["dias"] < 0]
hoje_list = [t for t in tarefas if t["dias"] == 0]
semana    = [t for t in tarefas if t["dias"] is not None and 1 <= t["dias"] <= 7]
futuras   = [t for t in tarefas if t["dias"] is None or t["dias"] > 7]

# ─── MÉTRICAS ────────────────────────────────────────────────────────────────

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total de tarefas", len(tarefas))
c2.metric("⚠️ Vencidas", len(vencidas))
c3.metric("📅 Hoje", len(hoje_list))
c4.metric("📆 Próximos 7 dias", len(semana))

st.divider()

# ─── RENDERIZA GRUPO ──────────────────────────────────────────────────────────

def render_grupo(titulo, classe_header, lista):
    if not lista:
        return
    st.markdown(f'<div class="{classe_header}">{titulo} · {len(lista)} tarefa(s)</div>', unsafe_allow_html=True)
    for t in lista:
        if t["dias"] is None:
            chip = '<span class="chip chip-ok">Sem data</span>'
        elif t["dias"] < 0:
            chip = f'<span class="chip chip-vencida">Venceu há {abs(t["dias"])}d</span>'
        elif t["dias"] == 0:
            chip = '<span class="chip chip-hoje">⚡ Hoje</span>'
        elif t["dias"] <= 7:
            chip = f'<span class="chip chip-semana">{t["dias"]}d restantes</span>'
        else:
            chip = f'<span class="chip chip-ok">{t["data"]} · {t["dias"]}d</span>'

        st.markdown(f"""
        <div class="tarefa-card">
            <span class="municipio">🏛 {t["municipio"]}</span>
            <span class="tarefa-nome">{t["tarefa"]}</span>
            {chip}
        </div>
        """, unsafe_allow_html=True)

render_grupo("⚠️ VENCIDAS", "vencida-header", vencidas)
if vencidas: st.write("")
render_grupo("⚡ HOJE", "hoje-header", hoje_list)
if hoje_list: st.write("")
render_grupo("📆 PRÓXIMOS 7 DIAS", "semana-header", semana)
if semana: st.write("")
render_grupo("🗓 FUTURAS", "futuro-header", futuras)
