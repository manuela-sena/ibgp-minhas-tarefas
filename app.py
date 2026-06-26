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
/* Botões da sidebar — remove todo espaço padrão */
[data-testid="stSidebar"] .stButton{margin:0!important;padding:0!important}
[data-testid="stSidebar"] .stButton>div{margin:0!important;padding:0!important}
[data-testid="stSidebar"] .stButton button{
  display:flex!important;align-items:center;gap:10px;width:100%;
  padding:9px 12px!important;border:none!important;border-left:3px solid transparent!important;
  background:transparent!important;color:#9caac2!important;
  font:600 13px 'Public Sans',system-ui,sans-serif!important;
  border-radius:7px!important;cursor:pointer;text-align:left!important;
  margin:0 0 1px 0!important;line-height:1.3!important;min-height:0!important
}
[data-testid="stSidebar"] .stButton button:hover{
  background:rgba(255,255,255,0.07)!important;color:#dde4ef!important
}
[data-testid="stSidebar"] .stButton button:focus{
  box-shadow:none!important;outline:none!important
}
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

    paginas = [("tarefas", "📋  Tarefas"), ("validar", "📊  Validar"), ("gerar", "🗓  Gerar"), ("reajustar", "🔧  Reajustar")]
    if is_cronograma:
        paginas = paginas[1:]

    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "validar" if is_cronograma else "tarefas"

    pagina_atual = st.session_state["pagina"]

    # CSS dinâmico para botão ativo
    ativo_css = ""
    for pid, _ in paginas:
        if pagina_atual == pid:
            ativo_css += f"""
            [data-testid="stSidebar"] div:has(button[data-testid*="nav_{pid}"]) button,
            [data-testid="stSidebar"] div:has(button[key="nav_{pid}"]) button {{
              background:rgba(255,255,255,0.12)!important;
              color:#fff!important;
              border-left:3px solid #2f6cc4!important;
            }}"""
    if ativo_css:
        st.markdown(f"<style>{ativo_css}</style>", unsafe_allow_html=True)

    for pid, plabel in paginas:
        if st.button(plabel, key=f"nav_{pid}", use_container_width=True):
            st.session_state["pagina"] = pid
            st.rerun()

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
def new_date_fmt(iso):
    if not iso: return "—"
    try: return datetime.fromisoformat(iso.replace("Z","+00:00")).replace(tzinfo=None).strftime("%d/%m/%Y")
    except: return "—"

def to_date(iso):
    if not iso: return None
    try: return datetime.fromisoformat(iso.replace("Z","+00:00")).replace(tzinfo=None).date()
    except: return None

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
    st.markdown(f"""<div class="group-card">
      <div class="group-hdr" style="background:{bg_hdr}">
        <span class="group-lbl" style="color:{cor_lbl}">{titulo}</span>
        <span class="group-badge" style="background:{bg_badge};color:{cor_badge}">{len(lista)} tarefas</span>
      </div></div>""", unsafe_allow_html=True)
    for t in lista:
        pessoa = chip_pessoa(t["responsavel"]) if show_pessoa else ""
        nota = st.session_state.get(f"notas_cache_{t['id']}", "")
        nota_html = f'<div style="font-size:11px;color:#9aa6b8;font-style:italic;margin-top:2px">📝 {nota}</div>' if nota else ""
        col_info, col_chip, col_btns = st.columns([7, 2, 1])
        with col_info:
            st.markdown(f"""<div style="padding:10px 0 4px">
              <div class="t-mun">{t["municipio"]}</div>
              <div style="display:flex;align-items:center;gap:7px;margin-top:3px">{pessoa}<span class="t-desc">{t["tarefa"]}</span></div>
              {nota_html}
            </div>""", unsafe_allow_html=True)
        with col_chip:
            st.markdown(f'<div style="padding:12px 0;display:flex;justify-content:flex-end">{chip_data(t["dias"], t["data"])}</div>', unsafe_allow_html=True)
        with col_btns:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📝", key=f"nota_{t['id']}", help="Nota"):
                    st.session_state[f"editando_{t['id']}"] = not st.session_state.get(f"editando_{t['id']}", False)
                    st.rerun()
            with c2:
                if st.button("✅", key=f"ok_{t['id']}", help="Concluída"):
                    r1 = requests.get(f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}", headers={"Authorization":f"Bearer {token}"})
                    etag = r1.headers.get("ETag","*")
                    requests.patch(f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}",
                        headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","If-Match":etag},
                        json={"percentComplete":100})
                    st.cache_data.clear(); st.rerun()
        # Campo de edição de nota
        if st.session_state.get(f"editando_{t['id']}"):
            nova_nota = st.text_input("✏️ Nota:", value=nota, key=f"input_{t['id']}",
                placeholder="Ex: Data alterada para 15/07", label_visibility="collapsed")
            cs, cc = st.columns([1,1])
            with cs:
                if st.button("💾 Salvar", key=f"salvar_{t['id']}", type="primary"):
                    r1 = requests.get(f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}/details",
                        headers={"Authorization":f"Bearer {token}"})
                    etag = r1.headers.get("ETag","*")
                    requests.patch(f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}/details",
                        headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","If-Match":etag},
                        json={"description": nova_nota})
                    st.session_state[f"notas_cache_{t['id']}"] = nova_nota
                    st.session_state[f"editando_{t['id']}"] = False
                    st.rerun()
            with cc:
                if st.button("✖", key=f"cancelar_{t['id']}"):
                    st.session_state[f"editando_{t['id']}"] = False
                    st.rerun()
        st.markdown('<div style="border-top:1px solid #eef1f6;margin:0 -1rem"></div>', unsafe_allow_html=True)

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
        import pandas as pd
        df = pd.read_excel(arquivo)
        df.columns = [str(c).strip() for c in df.columns]
        col_tarefa = next((c for c in df.columns if "tarefa" in c.lower() or "atividade" in c.lower()), df.columns[0])
        col_data   = next((c for c in df.columns if "data" in c.lower() or "date" in c.lower()), df.columns[1] if len(df.columns) > 1 else df.columns[0])

        with st.spinner("Cruzando com o Planner..."):
            tarefas_planner, buckets_v = buscar_tarefas(token)

        from datetime import timedelta
        planner_set = {}
        for t in tarefas_planner:
            if t["data"]:
                try:
                    dt = datetime.strptime(t["data"], "%d/%m/%Y").date()
                    planner_set.setdefault(t["tarefa"], []).append((dt, t["municipio"], t["responsavel"]))
                except: pass

        conflitos, sobrecargas, ok_count = [], {}, 0
        for _, row in df.iterrows():
            nome = str(row.get(col_tarefa, "")).strip()
            data_val = row.get(col_data)
            if not nome or not data_val: continue
            try:
                if isinstance(data_val, str):
                    for fmt in ["%d/%m/%Y","%Y-%m-%d","%d-%m-%Y"]:
                        try: dt = datetime.strptime(data_val.strip(), fmt).date(); break
                        except: dt = None
                else:
                    dt = pd.to_datetime(data_val).date()
            except: dt = None
            if not dt: continue

            match = planner_set.get(nome, [])
            conflitou = False
            for (dt_p, mun, resp) in match:
                if dt_p == dt:
                    conflitos.append({"tarefa": nome, "data": dt.strftime("%d/%m/%Y"), "conflito_com": mun, "responsavel": resp})
                    conflitou = True
            if not conflitou:
                ok_count += 1
                # Verifica sobrecarga por responsável
                resp_tarefa = ATRIBUICOES.get(nome)
                if resp_tarefa:
                    sobrecargas.setdefault((resp_tarefa, dt), []).append(nome)

        dias_sobrecarregados = {k: v for k, v in sobrecargas.items() if len(v) > 2}

        c1v, c2v = st.columns(2)
        c1v.metric("Conflitos encontrados", len(conflitos), delta=None)
        c2v.metric("Dias sobrecarregados", len(dias_sobrecarregados), delta=None)

        if conflitos:
            st.warning(f"⚠️ {len(conflitos)} tarefa(s) com conflito de data no Planner")
            df_conf = pd.DataFrame(conflitos)
            df_conf.columns = ["Tarefa", "Data", "Conflito com", "Responsável"]
            st.dataframe(df_conf, use_container_width=True, hide_index=True)
        if dias_sobrecarregados:
            st.warning(f"🔴 {len(dias_sobrecarregados)} dia(s) com sobrecarga por pessoa")
            for (resp, dt), nomes in dias_sobrecarregados.items():
                st.markdown(f"- **{resp}** em {dt.strftime('%d/%m/%Y')}: {len(nomes)} tarefas")
        if not conflitos and not dias_sobrecarregados:
            st.success("✅ Nenhum conflito ou sobrecarga encontrado!")

# ══════════ GERAR ══════════
elif pagina == "gerar":
    from cronograma_engine import calcular_cronograma

    st.markdown('<span style="font-size:19px;font-weight:800;color:#1f2a3d">🗓 Gerador de Cronograma Completo</span>', unsafe_allow_html=True)
    st.caption("Informe a data de publicação e as fases do concurso para calcular todas as datas automaticamente, respeitando dias úteis, feriados e recesso IBGP.")

    with st.container():
        nome_concurso = st.text_input("Nome do concurso (será o nome do bucket no Planner)", placeholder="Ex: MUNICÍPIO X - EDITAL Nº 01/2026 - CONCURSO PÚBLICO")
        tipo_certame  = st.radio("Tipo de certame", ["CONCURSO", "PSS", "GUARDA"], horizontal=True)

        col_dp, col_di = st.columns(2)
        with col_dp:
            data_pub = st.date_input("Data de publicação do edital", value=date.today())
        with col_di:
            dias_insc = st.number_input("Duração das inscrições (dias corridos)", min_value=1, max_value=60, value=10 if tipo_certame=="PSS" else 30)

        usar_manual = st.checkbox("Definir data de início das inscrições manualmente")
        data_manual = st.date_input("Data de início das inscrições", value=date.today()) if usar_manual else None

        ch_curso = 0
        if tipo_certame == "GUARDA":
            ch_curso = st.number_input("Carga horária do Curso de Formação (0 = sem curso)", min_value=0, max_value=2000, value=0, step=10)
            if ch_curso > 0:
                st.caption(f"📚 {ch_curso}h ÷ 10h/dia = **{-(-ch_curso//10)} dias úteis** de curso")

        st.markdown("**Fases do concurso**")
        col1g, col2g, col3g = st.columns(3)
        with col1g:
            f_obj  = st.checkbox("Prova Objetiva", value=True)
            f_ise  = st.checkbox("Isenção", value=True)
            f_ins  = st.checkbox("Inscrições", value=True)
            f_dis  = st.checkbox("Prova Discursiva")
            f_pra  = st.checkbox("Prova Prática")
        with col2g:
            f_taf  = st.checkbox("TAF / Capacidade Física")
            f_tit  = st.checkbox("Prova de Títulos")
            f_psi  = st.checkbox("Avaliação Psicológica")
            f_med  = st.checkbox("Avaliação Médica")
        with col3g:
            f_cli  = st.checkbox("Avaliação Clínica")
            f_het  = st.checkbox("Heteroidentificação")
            f_ent  = st.checkbox("Entrevista Devolutiva")
            f_comp = st.checkbox("Entrevista por Competências")
            f_sind = st.checkbox("Sindicância Social") if tipo_certame == "GUARDA" else False
            concom = st.checkbox("Concomitância Títulos + Prática/TAF") if f_tit and (f_pra or f_taf) else False

    if st.button("🗓 Calcular cronograma", type="primary"):
        cronograma = calcular_cronograma(
            tipo_certame=tipo_certame,
            data_publicacao=data_pub,
            tem_objetiva=f_obj, tem_inscricao=f_ins, tem_isencao=f_ise,
            tem_discursiva=f_dis, tem_pratica=f_pra, tem_taf=f_taf,
            tem_titulos=f_tit, tem_psicologica=f_psi, tem_medica=f_med,
            tem_clinica=f_cli, tem_hetero=f_het, tem_entrevista=f_ent,
            tem_competencias=f_comp, tem_sindicancia=f_sind,
            concomitancia_titulos_pratica=concom,
            data_inicio_inscricao=data_manual,
            dias_inscricao=int(dias_insc),
            carga_horaria_curso=int(ch_curso),
        )
        st.session_state["cronograma_gerado"] = cronograma
        st.session_state["nome_concurso_gerado"] = nome_concurso

    if "cronograma_gerado" in st.session_state:
        cron = st.session_state["cronograma_gerado"]
        st.success(f"✅ {len(cron)} atividades calculadas!")
        import pandas as pd
        df_cron = pd.DataFrame([{
            "Seq": r["seq"], "Atividade": r["atividade"],
            "Data Início": r["data_inicio"].strftime("%d/%m/%Y"),
            "Data Fim": r["data_fim"].strftime("%d/%m/%Y"),
        } for r in cron])
        st.dataframe(df_cron, use_container_width=True, hide_index=True)

        nome_g = st.session_state.get("nome_concurso_gerado","")
        if nome_g and st.button("🚀 Cadastrar no Planner", type="primary"):
            with st.spinner("Cadastrando..."):
                tarefas_v, buckets_g = buscar_tarefas(token)
                plano_id = None
                for grp in [requests.get("https://graph.microsoft.com/v1.0/me/memberOf", headers={"Authorization":f"Bearer {token}"}).json()]:
                    for g2 in grp.get("value",[]):
                        try:
                            plans = requests.get(f"https://graph.microsoft.com/v1.0/groups/{g2['id']}/planner/plans", headers={"Authorization":f"Bearer {token}"}).json()
                            for p in plans.get("value",[]):
                                if NOME_PLANO.upper() in p.get("title","").upper():
                                    plano_id = p["id"]; break
                        except: pass
                        if plano_id: break

                if plano_id:
                    bkts = requests.get(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets", headers={"Authorization":f"Bearer {token}"}).json()
                    bucket_map = {b["name"]:b["id"] for b in bkts.get("value",[])}
                    if nome_g not in bucket_map:
                        rb = requests.post("https://graph.microsoft.com/v1.0/planner/buckets",
                            headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
                            json={"name":nome_g,"planId":plano_id,"orderHint":" !"})
                        bucket_id = rb.json().get("id") if rb.status_code==201 else None
                    else:
                        bucket_id = bucket_map[nome_g]

                    if bucket_id:
                        ok2, err2 = 0, 0
                        prog = st.progress(0)
                        for i, t in enumerate(cron):
                            r2 = requests.post("https://graph.microsoft.com/v1.0/planner/tasks",
                                headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
                                json={"planId":plano_id,"bucketId":bucket_id,"title":t["atividade"],
                                      "dueDateTime":t["data_fim"].strftime("%Y-%m-%dT03:00:00Z"),
                                      "startDateTime":t["data_inicio"].strftime("%Y-%m-%dT03:00:00Z")})
                            if r2.status_code==201: ok2+=1
                            else: err2+=1
                            prog.progress((i+1)/len(cron))
                        st.cache_data.clear()
                        if ok2: st.success(f"✅ {ok2} tarefa(s) cadastrada(s)!")
                        if err2: st.warning(f"⚠️ {err2} erro(s).")
        elif not nome_g:
            st.info("Preencha o nome do concurso para habilitar o cadastro no Planner.")

# ══════════ REAJUSTAR ══════════
elif pagina == "reajustar":
    st.markdown('<span style="font-size:19px;font-weight:800;color:#1f2a3d">🔧 Reajustar Cronograma no Planner</span>', unsafe_allow_html=True)
    st.caption("Selecione um concurso e ajuste as datas das tarefas já cadastradas no Planner.")

    @st.cache_data(ttl=300, show_spinner=False)
    def buscar_plano_e_buckets(token):
        def g(url): return requests.get(url, headers={"Authorization":f"Bearer {token}"}).json()
        def g_all(url):
            res, nxt = [], url
            while nxt:
                d = requests.get(nxt, headers={"Authorization":f"Bearer {token}"}).json()
                res.extend(d.get("value",[])); nxt = d.get("@odata.nextLink")
            return res
        plano_id = None
        for grp in g_all("https://graph.microsoft.com/v1.0/me/memberOf"):
            gid = grp.get("id")
            if not gid: continue
            try:
                for p in g(f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans").get("value",[]):
                    if NOME_PLANO.upper() in p.get("title","").upper(): plano_id = p["id"]; break
            except: pass
            if plano_id: break
        if not plano_id: return None, {}
        bkts = g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets")
        return plano_id, {b["id"]:b["name"] for b in bkts.get("value",[])}

    with st.spinner("Carregando concursos..."):
        plano_id_r, buckets_r = buscar_plano_e_buckets(token)

    if not plano_id_r:
        st.error("Plano não encontrado.")
    else:
        opts = {v: k for k, v in sorted(buckets_r.items(), key=lambda x: x[1])}
        concurso_sel = st.selectbox("Selecione o concurso:", [""] + list(opts.keys()))

        if concurso_sel:
            bucket_id_r = opts[concurso_sel]
            with st.spinner("Carregando tarefas..."):
                def get_bucket_tasks(token, bucket_id):
                    res, nxt = [], f"https://graph.microsoft.com/v1.0/planner/buckets/{bucket_id}/tasks"
                    while nxt:
                        d = requests.get(nxt, headers={"Authorization":f"Bearer {token}"}).json()
                        res.extend(d.get("value",[])); nxt = d.get("@odata.nextLink")
                    return [t for t in res if t.get("percentComplete",0) != 100]

                abertas = sorted(get_bucket_tasks(token, bucket_id_r), key=lambda x: x.get("dueDateTime",""))

            if not abertas:
                st.info("Nenhuma tarefa em aberto neste concurso.")
            else:
                st.caption(f"**{len(abertas)} tarefas em aberto** — edite Nova Início e Nova Fim e clique Salvar.")
                import pandas as pd

                df_reaj = pd.DataFrame([{
                    "id": t["id"],
                    "Tarefa": t.get("title",""),
                    "Início Atual": new_date_fmt(t.get("startDateTime")),
                    "Fim Atual": new_date_fmt(t.get("dueDateTime")),
                    "Nova Início": to_date(t.get("startDateTime")),
                    "Nova Fim": to_date(t.get("dueDateTime")),
                    "start_iso": t.get("startDateTime",""),
                    "due_iso": t.get("dueDateTime",""),
                } for t in abertas])

                df_edit = st.data_editor(
                    df_reaj[["Tarefa","Início Atual","Fim Atual","Nova Início","Nova Fim"]],
                    column_config={
                        "Tarefa": st.column_config.TextColumn("Tarefa", disabled=True, width="large"),
                        "Início Atual": st.column_config.TextColumn("Início Atual", disabled=True, width="small"),
                        "Fim Atual": st.column_config.TextColumn("Fim Atual", disabled=True, width="small"),
                        "Nova Início": st.column_config.DateColumn("Nova Início ✏️", width="small", format="DD/MM/YYYY"),
                        "Nova Fim": st.column_config.DateColumn("Nova Fim ✏️", width="small", format="DD/MM/YYYY"),
                    },
                    hide_index=True, use_container_width=True, key="editor_reajuste"
                )

                alteradas = []
                for i, row in df_edit.iterrows():
                    orig_ini = df_reaj.iloc[i]["Nova Início"]
                    orig_fim = df_reaj.iloc[i]["Nova Fim"]
                    if row["Nova Início"] != orig_ini or row["Nova Fim"] != orig_fim:
                        alteradas.append({"idx":i,"id":df_reaj.iloc[i]["id"],
                            "nova_ini":row["Nova Início"],"nova_fim":row["Nova Fim"],
                            "orig_ini":orig_ini,"orig_fim":orig_fim,
                            "start_iso":df_reaj.iloc[i]["start_iso"],"due_iso":df_reaj.iloc[i]["due_iso"]})

                if alteradas:
                    st.caption(f"**{len(alteradas)} tarefa(s) com data alterada**")
                    cascata = st.checkbox("Recalcular em cascata (mesmo deslocamento para tarefas posteriores)")

                    if st.button("💾 Salvar alterações no Planner", type="primary"):
                        from cronograma_engine import is_util, proximo_util
                        from datetime import timedelta
                        to_save = list(alteradas)

                        if cascata and alteradas:
                            first = min(alteradas, key=lambda x: x["idx"])
                            if first["orig_fim"] and first["nova_fim"]:
                                delta = first["nova_fim"] - first["orig_fim"]
                                for i, t in enumerate(abertas):
                                    if i <= first["idx"]: continue
                                    if any(a["id"]==t["id"] for a in alteradas): continue
                                    if not t.get("dueDateTime"): continue
                                    dt_fim = datetime.fromisoformat(t["dueDateTime"].replace("Z","+00:00")).replace(tzinfo=None).date() + delta
                                    if not is_util(dt_fim): dt_fim = proximo_util(dt_fim)
                                    dt_ini = None
                                    if t.get("startDateTime"):
                                        dt_ini = datetime.fromisoformat(t["startDateTime"].replace("Z","+00:00")).replace(tzinfo=None).date() + delta
                                        if not is_util(dt_ini): dt_ini = proximo_util(dt_ini)
                                    to_save.append({"id":t["id"],"nova_fim":dt_fim,"nova_ini":dt_ini})

                        prog2 = st.progress(0)
                        ok3, err3 = 0, 0
                        for i, t in enumerate(to_save):
                            payload = {}
                            if t["nova_fim"]: payload["dueDateTime"] = t["nova_fim"].strftime("%Y-%m-%dT03:00:00Z")
                            if t["nova_ini"]: payload["startDateTime"] = t["nova_ini"].strftime("%Y-%m-%dT03:00:00Z")
                            if payload:
                                url_t = f"https://graph.microsoft.com/v1.0/planner/tasks/{t['id']}"
                                r3 = requests.get(url_t, headers={"Authorization":f"Bearer {token}"})
                                etag = r3.headers.get("ETag","*")
                                r4 = requests.patch(url_t, headers={"Authorization":f"Bearer {token}","Content-Type":"application/json","If-Match":etag}, json=payload)
                                if r4.status_code in [200,204]: ok3+=1
                                else: err3+=1
                            prog2.progress((i+1)/len(to_save))
                        st.cache_data.clear()
                        if ok3: st.success(f"✅ {ok3} tarefa(s) atualizada(s)!")
                        if err3: st.warning(f"⚠️ {err3} erro(s).")
                        st.rerun()
                else:
                    st.info("Edite as colunas 'Nova Início ✏️' e 'Nova Fim ✏️' para habilitar o ajuste.")
