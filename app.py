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
    "maria":"Maria Cristina","maria cristina":"Maria Cristina","maria cristina salomão":"Maria Cristina","cristina":"Maria Cristina",
}

_atrib_raw = open("/mount/src/ibgp-minhas-tarefas/atribuicoes.js").read()
ATRIBUICOES = {k: v for k, v in re.findall(r'"([^"]+)":\s*"([^"]+)"', _atrib_raw)}

st.set_page_config(page_title="IBGP · Minhas Tarefas", page_icon="✅", layout="wide")

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

is_gestora    = nome_interno == "Manuela"
is_cronograma = nome_interno in ("Fabiano", "Maria Cristina")
perfil = ("Gestora · Equipe IBGP" if is_gestora
          else ("Cronograma · IBGP" if is_cronograma else "Equipe IBGP"))

# ── CALCULAR CRONOGRAMA (acionado via query param) ────────────────────
CRON_RESULT_KEY = "cronograma_result"

if "calc_cron" in st.query_params:
    try:
        p = json.loads(st.query_params["calc_cron"])
        from cronograma_engine import calcular_cronograma
        data_pub = date.fromisoformat(p["data_pub"])
        result = calcular_cronograma(
            tipo_certame        = p.get("tipo","CONCURSO"),
            data_publicacao     = data_pub,
            tem_objetiva        = p.get("tem_objetiva", True),
            tem_inscricao       = p.get("tem_inscricao", True),
            tem_isencao         = p.get("tem_isencao", True),
            tem_discursiva      = p.get("tem_discursiva", False),
            tem_pratica         = p.get("tem_pratica", False),
            tem_taf             = p.get("tem_taf", False),
            tem_titulos         = p.get("tem_titulos", False),
            tem_psicologica     = p.get("tem_psicologica", False),
            tem_medica          = p.get("tem_medica", False),
            tem_clinica         = p.get("tem_clinica", False),
            tem_hetero          = p.get("tem_hetero", False),
            tem_entrevista      = p.get("tem_entrevista", False),
            tem_competencias    = p.get("tem_competencias", False),
            tem_sindicancia     = p.get("tem_sindicancia", False),
            concomitancia_titulos_pratica = p.get("concomitancia", False),
            data_inicio_inscricao = date.fromisoformat(p["data_ini_insc"]) if p.get("data_ini_insc") else None,
            dias_inscricao      = int(p.get("dias_insc", 30)),
            carga_horaria_curso = int(p.get("ch_curso", 0)),
        )
        # Serializar datas para JSON
        result_json = [{"seq":r["seq"],"atividade":r["atividade"],
                        "data_inicio":r["data_inicio"].strftime("%d/%m/%Y"),
                        "data_fim":r["data_fim"].strftime("%d/%m/%Y")} for r in result]
        st.session_state[CRON_RESULT_KEY] = result_json
        st.session_state["cron_nome"]     = p.get("nome","")
        st.session_state["cron_raw"]      = result  # para cadastro no Planner
    except Exception as e:
        st.session_state[CRON_RESULT_KEY] = {"erro": str(e)}
    st.query_params.clear()
    st.rerun()

# ── CADASTRAR NO PLANNER (acionado via query param) ──────────────────
if "cadastrar_planner" in st.query_params:
    try:
        p       = json.loads(st.query_params["cadastrar_planner"])
        nome_b  = p.get("nome","")
        tarefas_c = st.session_state.get("cron_raw", [])
        # Buscar plano
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
                for pl in g(f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans").get("value",[]):
                    if NOME_PLANO.upper() in pl.get("title","").upper():
                        plano_id = pl["id"]; break
            except: pass
            if plano_id: break
        if plano_id and nome_b and tarefas_c:
            bkts = requests.get(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets",
                                headers={"Authorization":f"Bearer {token}"}).json()
            bucket_map = {b["name"]:b["id"] for b in bkts.get("value",[])}
            if nome_b not in bucket_map:
                rb = requests.post("https://graph.microsoft.com/v1.0/planner/buckets",
                    headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
                    json={"name":nome_b,"planId":plano_id,"orderHint":" !"})
                bucket_id = rb.json().get("id") if rb.status_code==201 else None
            else:
                bucket_id = bucket_map[nome_b]
            ok2, err2 = 0, 0
            if bucket_id:
                for t in tarefas_c:
                    r2 = requests.post("https://graph.microsoft.com/v1.0/planner/tasks",
                        headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},
                        json={"planId":plano_id,"bucketId":bucket_id,"title":t["atividade"],
                              "dueDateTime":t["data_fim"].strftime("%Y-%m-%dT03:00:00Z"),
                              "startDateTime":t["data_inicio"].strftime("%Y-%m-%dT03:00:00Z")})
                    if r2.status_code==201: ok2+=1
                    else: err2+=1
            st.session_state["planner_ok"]  = ok2
            st.session_state["planner_err"] = err2
            st.cache_data.clear()
    except Exception as e:
        st.session_state["planner_ok"]  = 0
        st.session_state["planner_err"] = str(e)
    st.query_params.clear()
    st.rerun()

# ── DOWNLOAD XLSX (acionado via query param) ──────────────────────────
if "download_xlsx" in st.query_params:
    try:
        import sys
        sys.path.insert(0, "/mount/src/ibgp-minhas-tarefas")
        from gerar_xlsx import gerar_xlsx_ibgp
        from datetime import datetime

        p = json.loads(st.query_params["download_xlsx"])
        nome = p.get("nome", "Cronograma")
        tipo = p.get("tipo", "CONCURSO")
        tarefas_x = p.get("tarefas", [])

        # Converter strings de data de volta para datetime
        parsed = []
        for t in tarefas_x:
            ini = datetime.strptime(t["data_inicio"], "%d/%m/%Y")
            fim = datetime.strptime(t["data_fim"],    "%d/%m/%Y")
            parsed.append({"seq": t["seq"], "atividade": t["atividade"],
                           "data_inicio": ini, "data_fim": fim})

        xlsx_bytes = gerar_xlsx_ibgp(nome, tipo, parsed)
        nome_arquivo = nome.replace("/","_").replace(" ","_")[:60] + "_cronograma.xlsx"

        st.query_params.clear()
        st.download_button(
            label="📥 Clique aqui para baixar o XLSX",
            data=xlsx_bytes,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.stop()
    except Exception as e:
        st.error(f"Erro ao gerar XLSX: {e}")
        st.query_params.clear()
        st.rerun()


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
    from datetime import timezone, timedelta
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
    if not plano_id: return [], [], {}, None
    buckets = {b["id"]:b["name"]
               for b in g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets").get("value",[])}
    tarefas, concluidas = [], []
    limite_48h = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=48)
    for t in g_all(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/tasks"):
        nome = (t.get("title") or "").strip()
        resp = ATRIBUICOES.get(nome)
        if not resp: continue
        due = t.get("dueDateTime") or ""
        item = {
            "id": t["id"],
            "municipio": buckets.get(t.get("bucketId",""),"—"),
            "tarefa": nome,
            "responsavel": resp,
            "due": due,
            "hasNota": bool(t.get("hasDescription", False)),
        }
        if t.get("percentComplete",0) == 100:
            # Só inclui concluídas das últimas 48h
            completed_at = t.get("completedDateTime","")
            if completed_at:
                try:
                    dt = datetime.fromisoformat(completed_at.replace("Z","+00:00"))
                    if dt >= limite_48h:
                        item["completedAt"] = completed_at
                        concluidas.append(item)
                except Exception: pass
        else:
            tarefas.append(item)
    # Ordenar concluídas da mais recente para a mais antiga
    concluidas.sort(key=lambda x: x.get("completedAt",""), reverse=True)
    return tarefas, concluidas[:30], buckets, plano_id

with st.spinner("Carregando tarefas..."):
    tarefas, concluidas, buckets, plano_id = buscar_tarefas(token)

# ── MONTAR DADOS_INICIAIS ─────────────────────────────────────────────
cron_result  = st.session_state.pop(CRON_RESULT_KEY, None)
cron_nome    = st.session_state.get("cron_nome","")
planner_ok   = st.session_state.pop("planner_ok", None)
planner_err  = st.session_state.pop("planner_err", None)

dados_iniciais = json.dumps({
    "tarefas"      : tarefas,
    "concluidas"   : concluidas,
    "buckets"      : buckets,
    "planoId"      : plano_id,
    "cronResult"   : cron_result,
    "cronNome"     : cron_nome,
    "plannerOk"    : planner_ok,
    "plannerErr"   : planner_err,
})

# ── LER E INJETAR TEMPLATE ────────────────────────────────────────────
with open("/mount/src/ibgp-minhas-tarefas/template.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("// PLACEHOLDER_TOKEN",
    f"const TOKEN = {json.dumps(token)};")
html = html.replace("// PLACEHOLDER_CONFIG",
    f"""const IS_GESTORA    = {'true' if is_gestora   else 'false'};
const IS_CRONOGRAMA = {'true' if is_cronograma else 'false'};
const NOME_USUARIO  = {json.dumps(nome_interno)};
const DADOS_INICIAIS = {dados_iniciais};""")
html = html.replace("// PLACEHOLDER_ATRIB",
    f"const ATRIBUICOES_JS = {json.dumps(ATRIBUICOES)};")

components.html(html, height=900, scrolling=False)
