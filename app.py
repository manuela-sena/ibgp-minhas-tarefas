import streamlit as st
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

# Lê atribuições
_atrib_raw = open("/mount/src/ibgp-minhas-tarefas/atribuicoes.js").read()
ATRIBUICOES = {k: v for k, v in re.findall(r'"([^"]+)":\s*"([^"]+)"', _atrib_raw)}

st.set_page_config(page_title="IBGP · Minhas Tarefas", page_icon="✅", layout="wide")

# CSS que imita o mockup usando sidebar nativa do Streamlit
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');
html,body,[class*="css"]{font-family:'Public Sans',system-ui,sans-serif;color:#1f2a3d}
/* Sidebar dark */
[data-testid="stSidebar"]{background:#16243d!important;min-width:220px!important;max-width:220px!important}
[data-testid="stSidebar"] *{color:#9caac2!important}
[data-testid="stSidebarContent"]{padding:16px 12px!important}
/* Botões da sidebar */
[data-testid="stSidebar"] .stButton button{
  display:flex;align-items:center;gap:10px;width:100%;
  padding:10px 12px;border:none;border-left:3px solid transparent;
  background:transparent;color:#9caac2!important;font:600 13px 'Public Sans',system-ui,sans-serif;
  border-radius:8px;cursor:pointer;text-align:left;margin-bottom:2px
}
[data-testid="stSidebar"] .stButton button:hover{background:rgba(255,255,255,0.07)!important;color:#dde4ef!important}
/* Página principal */
.stApp{background:#eef1f6}
.block-container{padding:1.5rem 2rem!important;max-width:100%!important}
header[data-testid="stHeader"]{display:none}
footer{display:none}
#MainMenu{display:none}
/* KPI cards */
.kpi-card{background:#fff;border:1px solid #e2e7ef;border-radius:14px;box-shadow:0 1px 3px rgba(16,30,54,0.05);padding:16px 18px}
.kpi-val{font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:600;line-height:1.1}
/* Task groups */
.group-card{background:#fff;border:1px solid #e2e7ef;border-radius:14px;overflow:hidden;margin-bottom:14px;box-shadow:0 1px 3px rgba(16,30,54,0.05)}
.group-hdr{display:flex;align-items:center;gap:9px;padding:11px 16px}
.group-lbl{font-size:11px;font-weight:800;letter-spacing:.07em}
.group-badge{margin-left:auto;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px}
.t-row{display:flex;align-items:center;gap:10px;padding:11px 16px;border-top:1px solid #eef1f6}
.t-row:hover{background:#fafbfc}
.t-mun{font-size:10.5px;font-weight:700;color:#7a869c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.t-desc{font-size:13px;color:#28344a;font-weight:500}
.chip-d{font-size:11px;font-weight:700;padding:4px 10px;border-radius:20px;white-space:nowrap;flex:none}
.chip-Lorena{display:inline-block;padding:2px 8px;border-radius:5px;font-size:10.5px;font-weight:700;background:#e8f0fb;color:#2860b0}
.chip-Laryssa{display:inline-block;padding:2px 8px;border-radius:5px;font-size:10.5px;font-weight:700;background:#e4f3ea;color:#2e7d52}
.chip-Natália{display:inline-block;padding:2px 8px;border-radius:5px;font-size:10.5px;font-weight:700;background:#e4f3ea;color:#2e7d52}
.chip-Manuela{display:inline-block;padding:2px 8px;border-radius:5px;font-size:10.5px;font-weight:700;background:#efeafb;color:#6b4fa3}
</style>""", unsafe_allow_html=True)

# ── AUTH ──────────────────────────────────────────────────────────────────────
def auth_url():
    p = {"client_id":CLIENT_ID,"response_type":"code","redirect_uri":REDIRECT_URI,"scope":SCOPES,"response_mode":"query"}
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?" + urlencode(p)

def trocar_codigo(code):
    r = requests.post(f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data={"client_id":CLIENT_ID,"client_secret":st.secrets["CLIENT_SECRET"],
              "grant_type":"authorization_code","code":code,"redirect_uri":REDIRECT_URI,"scope":SCOPES})
    return r.json()

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
        st.markdown("""<div style="display:flex;height:80vh;align-items:center;justify-content:center">
          <div style="background:#fff;border:1px solid #e2e7ef;border-radius:16px;padding:3rem;text-align:center;max-width:360px">
            <div style="width:48px;height:48px;background:linear-gradient(135deg,#2f6cc4,#1f4e8c);border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:18px;margin:0 auto 1rem">IB</div>
            <h2 style="margin:0 0 .4rem;font-size:1.1rem;font-weight:700">IBGP · Minhas Tarefas</h2>
            <p style="color:#7a869c;font-size:.875rem;margin:0 0 1.5rem">Entre com sua conta Microsoft.</p>
          </div></div>""", unsafe_allow_html=True)
        col1,col2,col3 = st.columns([1,1,1])
        with col2: st.link_button("🔐 Entrar com Microsoft", auth_url(), use_container_width=True)
        st.stop()

token = st.session_state["access_token"]

# ── USUÁRIO ───────────────────────────────────────────────────────────────────
try:
    me = requests.get("https://graph.microsoft.com/v1.0/me", headers={"Authorization":f"Bearer {token}"}).json()
    display_name = me.get("displayName","")
    first_name = display_name.split()[0] if display_name else "Usuário"
    nome_interno = NOME_MAP.get(first_name.lower(), NOME_MAP.get(display_name.lower(), first_name))
except:
    st.error("Sessão expirada."); st.button("Entrar novamente", on_click=lambda: st.session_state.pop("access_token")); st.stop()

is_gestora    = nome_interno == "Manuela"
is_cronograma = nome_interno == "Fabiano"
perfil = "Gestora · Equipe IBGP" if is_gestora else ("Cronograma · IBGP" if is_cronograma else "Equipe IBGP")

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""<div style="display:flex;align-items:center;gap:9px;padding:2px 6px 18px">
      <div style="width:34px;height:34px;border-radius:8px;background:linear-gradient(135deg,#2f6cc4,#1f4e8c);display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:13px;flex:none">IB</div>
      <div><div style="color:#fff!important;font-weight:700;font-size:13.5px">IBGP</div>
      <div style="color:#7e8ca6!important;font-size:10px;font-weight:600;letter-spacing:.04em">Minhas Tarefas</div></div>
    </div>
    <div style="font-size:9.5px;font-weight:700;letter-spacing:.12em;color:#5f6e8a;padding:2px 8px 8px">FLUXO DE CRONOGRAMA</div>
    """, unsafe_allow_html=True)

    paginas = [("tarefas", "≡  Tarefas"), ("validar", "↑  Validar"), ("gerar", "▦  Gerar"), ("reajustar", "⊞  Reajustar")]
    if not is_cronograma:
        pass
    else:
        paginas = paginas[1:]

    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "cronograma" if is_cronograma else "tarefas"

    for pid, plabel in paginas:
        ativo = st.session_state["pagina"] == pid
        style = "background:rgba(255,255,255,0.10)!important;color:#fff!important;border-left:3px solid #2f6cc4!important" if ativo else ""
        if st.button(plabel, key=f"nav_{pid}", use_container_width=True):
            st.session_state["pagina"] = pid
            st.rerun()
        if ativo:
            st.markdown(f"""<style>
            div[data-testid="stSidebar"] div:has(> button[kind="secondary"][id*="nav_{pid}"]) button {{
              background:rgba(255,255,255,0.10)!important;color:#fff!important;border-left:3px solid #2f6cc4!important
            }}</style>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="position:fixed;bottom:16px;left:0;width:220px;padding:12px 14px;border-top:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;gap:9px">
      <div style="width:30px;height:30px;border-radius:50%;background:#6b4fa3;color:#fff!important;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex:none">{nome_interno[0].upper()}</div>
      <div><div style="color:#eef2f8!important;font-weight:600;font-size:12px">{nome_interno}</div>
      <div style="color:#7e8ca6!important;font-size:10px">{perfil}</div></div>
    </div>""", unsafe_allow_html=True)

# ── API HELPERS ───────────────────────────────────────────────────────────────
def g(url):
    r = requests.get(url, headers={"Authorization":f"Bearer {token}"}); r.raise_for_status(); return r.json()
def g_all(url):
    res, nxt = [], url
    while nxt:
        d = requests.get(nxt, headers={"Authorization":f"Bearer {token}"}).json()
        res.extend(d.get("value",[])); nxt = d.get("@odata.nextLink")
    return res
def patch(url, body):
    r1 = requests.get(url, headers={"Authorization":f"Bearer {token}"})
    etag = r1.headers.get("ETag","*")
    return requests.patch(url, headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","If-Match":etag}, json=body)

@st.cache_data(ttl=180, show_spinner=False)
def buscar_tarefas(token):
    plano_id = None
    for grp in g_all("https://graph.microsoft.com/v1.0/me/memberOf"):
        gid = grp.get("id"); 
        if not gid: continue
        try:
            for p in g(f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans").get("value",[]):
                if NOME_PLANO.upper() in p.get("title","").upper(): plano_id = p["id"]; break
        except: pass
        if plano_id: break
    if not plano_id: return [], {}
    buckets = {b["id"]:b["name"] for b in g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets").get("value",[])}
    tarefas = []
    for t in g_all(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/tasks"):
        if t.get("percentComplete",0)==100: continue
        nome = (t.get("title") or "").strip()
        resp = ATRIBUICOES.get(nome)
        if not resp: continue
        due = t.get("dueDateTime")
        dt = None
        if due:
            try: dt = datetime.fromisoformat(due.replace("Z","+00:00")).replace(tzinfo=None)
            except: pass
        dias = (dt.date()-date.today()).days if dt else None
        tarefas.append({"id":t["id"],"municipio":buckets.get(t.get("bucketId",""),"—"),"tarefa":nome,"responsavel":resp,"data":dt.strftime("%d/%m/%Y") if dt else "","dias":dias})
    tarefas.sort(key=lambda x: (2 if x["dias"] is None else (0 if x["dias"]<0 else 1), x["dias"] or 9999))
    return tarefas, buckets

# ── CHIPS ─────────────────────────────────────────────────────────────────────
def chip_data(dias, data):
    if dias is None: return f'<span class="chip-d" style="background:#eef1f6;color:#4a566d;border:1px solid #d8dee8">Sem data</span>'
    if dias < 0:     return f'<span class="chip-d" style="background:#fdeceb;color:#c0322f;border:1px solid #f3cfcd">Venceu há {abs(dias)}d</span>'
    if dias == 0:    return f'<span class="chip-d" style="background:#fbf1de;color:#a06c12;border:1px solid #ecd6a8">⚡ Hoje</span>'
    if dias <= 7:    return f'<span class="chip-d" style="background:#e9f1fb;color:#2860b0;border:1px solid #b8d0ef">{data} · {dias}d</span>'
    return f'<span class="chip-d" style="background:#eef1f6;color:#4a566d;border:1px solid #d8dee8">{data} · {dias}d</span>'

def chip_pessoa(nome):
    return f'<span class="chip-{nome}">{nome}</span>'

def render_grupo(lista, titulo, bg_hdr, cor_lbl, bg_badge, cor_badge, show_pessoa):
    if not lista: return
    rows = ""
    for t in lista:
        pessoa = chip_pessoa(t["responsavel"]) if show_pessoa else ""
        rows += f"""<div class="t-row">
          <div style="flex:1;min-width:0">
            <div class="t-mun">{t["municipio"]}</div>
            <div style="display:flex;align-items:center;gap:7px;margin-top:3px">{pessoa}<span class="t-desc">{t["tarefa"]}</span></div>
          </div>
          {chip_data(t["dias"], t["data"])}
        </div>"""
    st.markdown(f"""<div class="group-card">
      <div class="group-hdr" style="background:{bg_hdr}">
        <span class="group-lbl" style="color:{cor_lbl}">{titulo}</span>
        <span class="group-badge" style="background:{bg_badge};color:{cor_badge}">{len(lista)} tarefas</span>
      </div>{rows}</div>""", unsafe_allow_html=True)

# ── PÁGINA ────────────────────────────────────────────────────────────────────
pagina = st.session_state.get("pagina", "tarefas")
hoje_str = date.today().strftime("%d/%m/%Y — %A").replace("Monday","Segunda").replace("Tuesday","Terça").replace("Wednesday","Quarta").replace("Thursday","Quinta").replace("Friday","Sexta").replace("Saturday","Sábado").replace("Sunday","Domingo")

# Topbar
col_t, col_b = st.columns([9,1])
with col_t:
    st.markdown(f"""<div style="margin-bottom:20px">
      <div style="font-size:17px;font-weight:700;color:#1f2a3d">Olá, {nome_interno}! 👋</div>
      <div style="font-size:12px;color:#7a869c;font-weight:500">{hoje_str}</div>
    </div>""", unsafe_allow_html=True)
with col_b:
    if st.button("↻ Atualizar", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# ══════════ TAREFAS ══════════
if pagina == "tarefas":
    st.markdown('<div style="display:flex;align-items:center;gap:9px;margin-bottom:4px"><span style="font-size:19px;font-weight:800;color:#1f2a3d">Minhas Tarefas</span></div>' if not is_gestora else '<div style="display:flex;align-items:center;gap:9px;margin-bottom:4px"><span style="font-size:19px;font-weight:800;color:#1f2a3d">Visão da Gestora</span></div>', unsafe_allow_html=True)

    with st.spinner("Carregando..."):
        tarefas, buckets = buscar_tarefas(token)

    # Filtros
    with st.container():
        st.markdown('<div style="background:#fff;border:1px solid #e2e7ef;border-radius:14px;padding:16px 18px;margin-bottom:16px">', unsafe_allow_html=True)
        if is_gestora:
            filtro_pessoa = st.selectbox("Visualizar tarefas de", ["Toda a equipe","Lorena","Laryssa","Natália","Manuela"], label_visibility="visible")
        else:
            filtro_pessoa = nome_interno

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            concursos = sorted(set(t["municipio"] for t in tarefas))
            filtro_conc = st.selectbox("🔍 Filtrar por concurso", ["Todos"]+concursos, label_visibility="visible")
        with col_f2:
            nomes_tarefas = sorted(set(t["tarefa"] for t in tarefas))
            filtro_tar = st.selectbox("📄 Filtrar por tarefa", ["Todas"]+nomes_tarefas, label_visibility="visible")
        st.markdown('</div>', unsafe_allow_html=True)

    # Aplica filtros
    exibir = tarefas
    if is_gestora and filtro_pessoa != "Toda a equipe":
        exibir = [t for t in exibir if t["responsavel"] == filtro_pessoa]
    elif not is_gestora:
        exibir = [t for t in exibir if t["responsavel"] == nome_interno]
    if filtro_conc != "Todos":
        exibir = [t for t in exibir if t["municipio"] == filtro_conc]
    if filtro_tar != "Todas":
        exibir = [t for t in exibir if t["tarefa"] == filtro_tar]

    # KPIs
    vencidas  = [t for t in exibir if t["dias"] is not None and t["dias"] < 0]
    hoje_list = [t for t in exibir if t["dias"] == 0]
    semana    = [t for t in exibir if t["dias"] is not None and 1 <= t["dias"] <= 7]
    futuras   = [t for t in exibir if t["dias"] is None or t["dias"] > 7]

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="kpi-card"><div style="font-size:10.5px;font-weight:700;letter-spacing:.06em;color:#7a869c;margin-bottom:6px">● TOTAL</div><div class="kpi-val">{len(exibir)}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div style="font-size:10.5px;font-weight:700;letter-spacing:.06em;color:#7a869c;margin-bottom:6px"><span style="color:#d93b3b">●</span> VENCIDAS</div><div class="kpi-val" style="color:#d93b3b">{len(vencidas)}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div style="font-size:10.5px;font-weight:700;letter-spacing:.06em;color:#7a869c;margin-bottom:6px"><span style="color:#d98a1f">●</span> HOJE</div><div class="kpi-val" style="color:#c9821a">{len(hoje_list)}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi-card"><div style="font-size:10.5px;font-weight:700;letter-spacing:.06em;color:#7a869c;margin-bottom:6px"><span style="color:#2f6cc4">●</span> PRÓXIMOS 7 DIAS</div><div class="kpi-val" style="color:#2f6cc4">{len(semana)}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    show_pessoa = is_gestora and filtro_pessoa == "Toda a equipe"
    render_grupo(vencidas,  "⚠ VENCIDAS",        "#fdeceb","#b3322f","#f7d6d4","#b3322f", show_pessoa)
    render_grupo(hoje_list, "⚡ HOJE",             "#fbf1de","#a06c12","#f3e2bf","#a06c12", show_pessoa)
    render_grupo(semana,    "📅 PRÓXIMOS 7 DIAS", "#e9f1fb","#2860b0","#cfe0f5","#2860b0", show_pessoa)
    render_grupo(futuras,   "🕐 FUTURAS",          "#eef1f6","#4a566d","#dfe4ec","#4a566d", show_pessoa)

    if not exibir:
        st.success("🎉 Nenhuma tarefa pendente encontrada!")

# ══════════ VALIDAR ══════════
elif pagina == "validar":
    st.markdown('<span style="font-size:19px;font-weight:800;color:#1f2a3d">📊 Validar Novo Cronograma</span>', unsafe_allow_html=True)
    st.caption("Suba a planilha do novo concurso para verificar conflitos e sobrecarga antes de cadastrar no Planner.")
    arquivo = st.file_uploader("Selecione a planilha (.xlsx)", type=["xlsx"])
    if arquivo:
        st.info("Validação disponível — integração em andamento.")

# ══════════ GERAR ══════════
elif pagina == "gerar":
    st.markdown('<span style="font-size:19px;font-weight:800;color:#1f2a3d">🗓 Gerador de Cronograma Completo</span>', unsafe_allow_html=True)
    st.caption("Informe a data de publicação e as fases do concurso para calcular todas as datas automaticamente.")
    st.info("Use a versão anterior do app para gerar cronogramas com o motor de regras IBGP.")

# ══════════ REAJUSTAR ══════════
elif pagina == "reajustar":
    st.markdown('<span style="font-size:19px;font-weight:800;color:#1f2a3d">🔧 Reajustar Cronograma no Planner</span>', unsafe_allow_html=True)
    st.caption("Selecione um concurso e ajuste as datas das tarefas já cadastradas no Planner.")
    st.info("Reajuste disponível — integração em andamento.")
