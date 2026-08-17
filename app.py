import streamlit as st
import streamlit.components.v1 as components
from urllib.parse import urlencode
import requests, json, re, secrets, hashlib
from datetime import datetime, date

CLIENT_ID    = "cf858739-80c5-4bf0-bc5c-6f5b0cefb70d"
TENANT_ID    = "e1362ab7-0546-4f12-9f44-0867415479b9"
REDIRECT_URI = "https://ibgp-minhas-tarefas-jkdmypmipxemkvhh6c5vjv.streamlit.app/"
SCOPES       = "Tasks.ReadWrite Group.Read.All User.Read offline_access"
NOME_PLANO   = "PLANNER IBGP"

USUARIOS_PATH = "/mount/src/ibgp-minhas-tarefas/usuarios.json"

def carregar_usuarios():
    try:
        with open(USUARIOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)["usuarios"]
    except Exception:
        return []

def usuarios_para_nome_map(usuarios):
    m = {}
    for u in usuarios:
        if not u.get("ativo", True): continue
        for alias in u.get("aliases", []):
            m[alias.lower()] = u["nome_interno"]
    return m

def usuarios_com_perfil(usuarios, perfil):
    return [u["nome_interno"] for u in usuarios if u.get("ativo",True) and u.get("perfil")==perfil]

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_senha(senha, hash_salvo):
    return hashlib.sha256(senha.encode()).hexdigest() == hash_salvo

def gerar_codigo():
    return secrets.token_urlsafe(8)

def salvar_usuarios_github(usuarios, gh_token):
    import base64
    REPO = "manuela-sena/ibgp-minhas-tarefas"
    r_sha = requests.get(f"https://api.github.com/repos/{REPO}/contents/usuarios.json",
        headers={"Authorization": f"Bearer {gh_token}"})
    sha = r_sha.json().get("sha","")
    conteudo = json.dumps({"usuarios": usuarios}, ensure_ascii=False, indent=2)
    return requests.put(f"https://api.github.com/repos/{REPO}/contents/usuarios.json",
        headers={"Authorization": f"Bearer {gh_token}", "Content-Type":"application/json"},
        json={"message":"chore: atualização de usuários","content":base64.b64encode(conteudo.encode()).decode(),"sha":sha})

def buscar_usuario_local(nome_interno):
    for u in USUARIOS:
        if u.get("nome_interno") == nome_interno and u.get("auth_tipo") == "local":
            return u
    return None

USUARIOS      = carregar_usuarios()
NOME_MAP      = usuarios_para_nome_map(USUARIOS)
GESTORAS      = usuarios_com_perfil(USUARIOS, "gestora")
CRONOGRAMAS   = usuarios_com_perfil(USUARIOS, "cronograma")
OPERACIONAIS  = usuarios_com_perfil(USUARIOS, "operacional")

_atrib_raw = open("/mount/src/ibgp-minhas-tarefas/atribuicoes.js").read()
ATRIBUICOES = {k: v for k, v in re.findall(r'"([^"]+)":\s*"([^"]+)"', _atrib_raw)}

def carregar_ferias():
    try:
        with open("/mount/src/ibgp-minhas-tarefas/ferias.json", "r", encoding="utf-8") as f:
            return json.load(f).get("ferias", [])
    except Exception:
        return []

def carregar_conclusoes_individuais():
    # Tarefas com múltiplos responsáveis (ex: "Natália, Amílcar") precisam de
    # conclusão independente por pessoa, já que o Planner só guarda 1 status
    # de conclusão por tarefa. Esse arquivo registra {task_id: {pessoa: dataISO}}.
    try:
        with open("/mount/src/ibgp-minhas-tarefas/conclusoes_individuais.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

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

def obter_token_servico():
    """Usa um refresh_token de uma conta Microsoft (salvo em st.secrets como
    SERVICE_REFRESH_TOKEN) para obter um access_token válido. Permite que contas
    de login local (sem Microsoft), como as de perfil operacional, também
    consigam ler as tarefas do Planner."""
    rt = st.secrets.get("SERVICE_REFRESH_TOKEN")
    if not rt:
        return None
    try:
        r = requests.post(
            f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
            data={"client_id":CLIENT_ID,"client_secret":st.secrets["CLIENT_SECRET"],
                  "grant_type":"refresh_token","refresh_token":rt,"scope":SCOPES})
        return r.json().get("access_token")
    except Exception:
        return None

params = st.query_params
code   = params.get("code")

# ── Processar callback Microsoft ──────────────────────────────────────
if code and "access_token" not in st.session_state and "local_user" not in st.session_state:
    with st.spinner("Autenticando..."):
        td = trocar_codigo(code)
    if "access_token" in td:
        st.session_state["access_token"]  = td["access_token"]
        st.session_state["refresh_token"] = td.get("refresh_token")
        st.query_params.clear()
        st.rerun()
    else:
        st.error(f"Erro: {td.get('error_description','')}")
    st.stop()

# ── Verificar se está logado (Microsoft ou local) ─────────────────────
logado_microsoft = "access_token" in st.session_state
logado_local     = "local_user" in st.session_state

if not logado_microsoft and not logado_local:
    erro          = st.session_state.pop("login_erro", "")
    primeiro_acesso = st.session_state.get("convite_ok", False)
    primeiro_nome   = st.session_state.get("primeiro_acesso_user", "")

    # CSS para esconder chrome do Streamlit e estilizar o login
    st.markdown("""
<style>
header[data-testid="stHeader"]{display:none}
footer{display:none}
#MainMenu{display:none}
[data-testid="stAppViewContainer"]{background:#eef1f6}
.block-container{padding:2rem 1rem!important;max-width:440px!important;margin:0 auto}
[data-testid="stForm"]{background:#fff;border-radius:20px!important;padding:2rem!important;box-shadow:0 8px 40px rgba(16,30,54,0.12)!important;border:none!important}
.stTextInput input{border-radius:10px!important;border:1.5px solid #d7dde7!important;font-size:.9rem!important}
.stTextInput input:focus{border-color:#1f4e8c!important;box-shadow:0 0 0 3px rgba(31,78,140,.1)!important}
.stButton button{border-radius:10px!important;font-weight:600!important;width:100%!important}
.stLinkButton a{border-radius:12px!important;font-weight:600!important;width:100%!important;background:#1f4e8c!important;color:#fff!important;border:none!important}
div[data-testid="stFormSubmitButton"] button{background:#f4f6fa!important;color:#1f2a3d!important;border:1.5px solid #e2e7ef!important}
div[data-testid="stFormSubmitButton"] button:hover{background:#eaecf2!important}
.divider{display:flex;align-items:center;gap:.8rem;margin:1rem 0}
.divider::before,.divider::after{content:'';flex:1;height:1px;background:#e2e7ef}
.divider span{color:#b0bac8;font-size:.8rem;white-space:nowrap}
</style>""", unsafe_allow_html=True)

    # Logo e título
    st.markdown(f"""
<div style="text-align:center;padding:2rem 0 1rem">
  <img src="https://raw.githubusercontent.com/manuela-sena/ibgp-minhas-tarefas/main/logo.png"
       style="width:56px;height:56px;object-fit:contain;margin-bottom:1rem;display:block;margin-left:auto;margin-right:auto">
  <h2 style="font-size:1.15rem;font-weight:700;color:#1f2a3d;margin-bottom:.3rem">IBGP · Minhas Tarefas</h2>
  <p style="color:#7a869c;font-size:.85rem">Acesso restrito à equipe IBGP</p>
</div>""", unsafe_allow_html=True)

    if erro:
        st.error(erro)

    if primeiro_acesso:
        st.info(f"Olá, **{primeiro_nome}**! É seu primeiro acesso. Defina uma senha.")
        with st.form("form_nova_senha"):
            nova = st.text_input("Nova senha", type="password", placeholder="Mínimo 6 caracteres")
            conf = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha")
            if st.form_submit_button("✅ Definir senha e entrar", type="primary", use_container_width=True):
                if nova != conf:
                    st.session_state["login_erro"] = "As senhas não coincidem."
                elif len(nova) < 6:
                    st.session_state["login_erro"] = "Senha deve ter pelo menos 6 caracteres."
                else:
                    nome_alvo = st.session_state.get("primeiro_acesso_user","")
                    GH_TOKEN = st.secrets.get("GITHUB_TOKEN","")
                    for u2 in USUARIOS:
                        if u2.get("nome_interno") == nome_alvo:
                            u2["senha_hash"] = hash_senha(nova)
                            u2["primeiro_acesso"] = False
                    salvar_usuarios_github(USUARIOS, GH_TOKEN)
                    st.session_state["local_user"] = nome_alvo
                    st.session_state.pop("convite_ok", None)
                    st.session_state.pop("primeiro_acesso_user", None)
                    st.rerun()
    else:
        # Botão Microsoft
        st.link_button("  Entrar com Microsoft", auth_url(), use_container_width=True)
        st.markdown('<div class="divider"><span>ou acesso com senha</span></div>', unsafe_allow_html=True)

        with st.form("form_login_local"):
            u_in = st.text_input("Usuário", placeholder="Seu usuário")
            p_in = st.text_input("Senha", type="password", placeholder="Sua senha")
            if st.form_submit_button("Entrar com usuário e senha", use_container_width=True):
                usuario_encontrado = None
                for u in USUARIOS:
                    if not u.get("ativo", True): continue
                    if u.get("auth_tipo") != "local": continue
                    nomes = [u.get("nome_interno","").lower()] + [a.lower() for a in u.get("aliases",[])]
                    if u_in.strip().lower() in nomes:
                        usuario_encontrado = u; break
                if not usuario_encontrado:
                    st.session_state["login_erro"] = "Usuário não encontrado."
                elif usuario_encontrado.get("primeiro_acesso"):
                    if verificar_senha(p_in, usuario_encontrado.get("senha_hash","")):
                        st.session_state["primeiro_acesso_user"] = usuario_encontrado["nome_interno"]
                        st.session_state["convite_ok"] = True
                    else:
                        st.session_state["login_erro"] = "Código de convite incorreto."
                elif verificar_senha(p_in, usuario_encontrado.get("senha_hash","")):
                    st.session_state["local_user"] = usuario_encontrado["nome_interno"]
                else:
                    st.session_state["login_erro"] = "Senha incorreta."
                st.rerun()

    st.stop()

token = st.session_state.get("access_token", None)

# ── USUÁRIO ───────────────────────────────────────────────────────────
if logado_local:
    # Login local — nome vem direto da sessão
    nome_interno = st.session_state["local_user"]
    token = obter_token_servico()  # Token de serviço (via refresh token salvo em secrets)
else:
    # Login Microsoft
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

is_gestora    = nome_interno in GESTORAS
is_cronograma = nome_interno in CRONOGRAMAS
is_operacional = nome_interno in OPERACIONAIS
perfil = ("Gestora · Equipe IBGP" if is_gestora
          else ("Cronograma · IBGP" if is_cronograma
          else ("Operacional · IBGP" if is_operacional else "Equipe IBGP")))

# ── SALVAR FÉRIAS ─────────────────────────────────────────────────────
if "salvar_ferias" in st.query_params and is_gestora:
    try:
        novas_ferias = json.loads(st.query_params["salvar_ferias"])
        GH_TOKEN = st.secrets.get("GITHUB_TOKEN","")
        import base64 as _b64
        REPO = "manuela-sena/ibgp-minhas-tarefas"
        r_sha = requests.get(f"https://api.github.com/repos/{REPO}/contents/ferias.json",
            headers={"Authorization": f"Bearer {GH_TOKEN}"})
        sha_f = r_sha.json().get("sha","") if r_sha.status_code==200 else ""
        conteudo = json.dumps({"ferias": novas_ferias}, ensure_ascii=False, indent=2)
        payload = {"message":"chore: atualizar férias","content":_b64.b64encode(conteudo.encode()).decode()}
        if sha_f: payload["sha"] = sha_f
        requests.put(f"https://api.github.com/repos/{REPO}/contents/ferias.json",
            headers={"Authorization": f"Bearer {GH_TOKEN}", "Content-Type":"application/json"},
            json=payload)
        st.session_state["ferias_msg"] = "✅ Férias salvas com sucesso!"
    except Exception as e:
        st.session_state["ferias_msg"] = f"⚠️ Erro: {e}"
    st.query_params.clear()
    st.rerun()


def g(url, tok=None):
    t = tok or token
    if not t: return {}
    r = requests.get(url, headers={"Authorization":f"Bearer {t}"})
    r.raise_for_status(); return r.json()

def g_all(url, tok=None):
    t = tok or token
    if not t: return []
    res, nxt = [], url
    while nxt:
        d = requests.get(nxt, headers={"Authorization":f"Bearer {t}"}).json()
        res.extend(d.get("value",[])); nxt = d.get("@odata.nextLink")
    return res

@st.cache_data(ttl=180, show_spinner=False)
def buscar_tarefas(token, ferias_json="[]", conclusoes_json="{}"):
    # Usuário local sem token Microsoft — retorna vazio
    if not token: return [], [], [], {}, None
    _ferias_registradas = json.loads(ferias_json)
    _conclusoes_individuais = json.loads(conclusoes_json)
    from datetime import timezone, timedelta
    def _g(url): return g(url, token)
    def _g_all(url): return g_all(url, token)
    plano_id = None
    for grp in _g_all("https://graph.microsoft.com/v1.0/me/memberOf"):
        gid = grp.get("id")
        if not gid: continue
        try:
            for p in _g(f"https://graph.microsoft.com/v1.0/groups/{gid}/planner/plans").get("value",[]):
                if NOME_PLANO.upper() in p.get("title","").upper():
                    plano_id = p["id"]; break
        except Exception: pass
        if plano_id: break
    if not plano_id: return [], [], [], {}, None
    buckets = {b["id"]:b["name"]
               for b in _g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets").get("value",[])}
    tarefas, concluidas, concluidas_todas = [], [], []
    limite_48h = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=48)
    for t in _g_all(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/tasks"):
        nome = (t.get("title") or "").strip()
        resp_raw = ATRIBUICOES.get(nome)
        if not resp_raw: continue
        # Suporta múltiplos responsáveis na mesma tarefa: "Fulano, Beltrano"
        responsaveis = [r.strip() for r in resp_raw.split(",") if r.strip()]
        eh_multi = len(responsaveis) > 1
        due = t.get("dueDateTime") or ""
        due_date = due[:10] if due else ""

        for idx, resp_original in enumerate(responsaveis):
            # Verificar se há férias que cobrem esta tarefa
            resp = resp_original
            hoje = date.today().isoformat()
            for f in _ferias_registradas:
                if not f.get("ativo", True): continue
                if f.get("de","") != resp_original: continue
                if hoje > f.get("fim","0000"): continue  # já terminou
                # Tarefa vence no período das férias
                if due_date and f.get("inicio","") <= due_date <= f.get("fim","9999"):
                    resp = f.get("para", resp_original)
                    break

            # rowKey identifica esta linha de forma única — em tarefas com um
            # único responsável é igual ao id do Planner (comportamento antigo
            # preservado); em tarefas duais, cada pessoa tem sua própria linha
            row_key = f"{t['id']}__{idx}" if eh_multi else t["id"]

            # Em tarefas duais, a conclusão de cada pessoa é independente e
            # não usa o percentComplete do Planner (que é compartilhado)
            individual_completed_at = None
            if eh_multi:
                individual_completed_at = _conclusoes_individuais.get(t["id"], {}).get(resp_original)
            efetivamente_concluida = (t.get("percentComplete",0) == 100) or (individual_completed_at is not None)

            item = {
                "id": t["id"],
                "rowKey": row_key,
                "multiResp": eh_multi,
                "municipio": buckets.get(t.get("bucketId",""),"—"),
                "tarefa": nome,
                "responsavel": resp,
                "due": due,
                "hasNota": bool(t.get("hasDescription", False)),
            }
            if efetivamente_concluida:
                completed_at = individual_completed_at or t.get("completedDateTime","")
                item_concl = {**item, "completedAt": completed_at, "concluida": True}
                # Histórico completo (usado na Agenda, sem limite de tempo)
                concluidas_todas.append(item_concl)
                # Só inclui no painel de sessão as concluídas das últimas 48h
                if completed_at:
                    try:
                        dt = datetime.fromisoformat(completed_at.replace("Z","+00:00"))
                        if dt >= limite_48h:
                            concluidas.append(item_concl)
                    except Exception: pass
            else:
                tarefas.append(item)
    # Ordenar concluídas da mais recente para a mais antiga
    concluidas.sort(key=lambda x: x.get("completedAt",""), reverse=True)
    concluidas_todas.sort(key=lambda x: x.get("completedAt",""), reverse=True)
    return tarefas, concluidas[:30], concluidas_todas, buckets, plano_id

with st.spinner("Carregando tarefas..."):
    _ferias_json = json.dumps(carregar_ferias())
    _conclusoes_json = json.dumps(carregar_conclusoes_individuais())
    tarefas, concluidas, concluidas_todas, buckets, plano_id = buscar_tarefas(token or "", _ferias_json, _conclusoes_json)

# ── MONTAR DADOS_INICIAIS ─────────────────────────────────────────────
cron_result  = st.session_state.pop("cron_result", None)
cron_nome    = st.session_state.get("cron_nome","")
planner_ok   = st.session_state.pop("planner_ok", None)
planner_err  = st.session_state.pop("planner_err", None)

usuarios_msg = st.session_state.pop("usuarios_msg", None)

convite_gerado = st.session_state.pop("convite_gerado", None)

ferias_msg    = st.session_state.pop("ferias_msg", None)

dados_iniciais = json.dumps({
    "tarefas"      : tarefas,
    "concluidas"   : concluidas,
    "concluidasTodas" : concluidas_todas,
    "buckets"      : buckets,
    "planoId"      : plano_id,
    "cronResult"   : cron_result,
    "cronNome"     : cron_nome,
    "plannerOk"    : planner_ok,
    "plannerErr"   : planner_err,
    "usuarios"     : USUARIOS,
    "usuariosMsg"  : usuarios_msg,
    "conviteGerado": convite_gerado,
    "ghToken"      : st.secrets.get("GITHUB_TOKEN","") if is_gestora else "",
    "appUrl"       : REDIRECT_URI.rstrip('/'),
    "ferias"       : carregar_ferias(),
    "feriasMsg"    : ferias_msg,
})

# ── NAVEGAÇÃO INTERNA (via sendPrompt do template) ───────────────────
_nav = st.query_params.get("nav","")
if _nav == "resultados":
    st.session_state["pagina"] = "resultados"
    st.query_params.clear()
    st.rerun()
if _nav == "homologacao":
    st.session_state["pagina"] = "homologacao"
    st.query_params.clear()
    st.rerun()

# ── PÁGINA DE RESULTADOS ──────────────────────────────────────────────
if st.session_state.get("pagina") == "resultados":
    import sys
    sys.path.insert(0, "/mount/src/ibgp-minhas-tarefas")
    from processar_inscricoes import processar

    st.markdown("""
<style>
header[data-testid="stHeader"]{display:none}
[data-testid="stAppViewContainer"]{background:#eef1f6}
.block-container{padding:1.5rem 2rem!important}
</style>""", unsafe_allow_html=True)

    col_back, col_title = st.columns([1,8])
    with col_back:
        if st.button("← Voltar"):
            st.session_state.pop("pagina", None)
            st.rerun()
    with col_title:
        st.markdown("## 📋 Resultados · Inscrições")

    st.markdown("---")
    arquivo = st.file_uploader("Selecione o relatório geral (.xlsx)", type=["xlsx"])

    if arquivo:
        # Detectar processos disponíveis
        import pandas as pd
        df_prev = pd.read_excel(arquivo, header=1, dtype=str, nrows=5000)
        df_prev.columns = [c.strip() for c in df_prev.columns]
        col_proc = next((c for c in df_prev.columns if any(x in c.upper() for x in ['CONCURSO','EDITAL','PROCESSO'])), None)
        arquivo.seek(0)

        processo_sel = None
        if col_proc:
            processos = sorted(df_prev[col_proc].dropna().str.strip().unique().tolist())
            processo_sel = st.selectbox("Selecione o processo", [''] + processos, format_func=lambda x: 'Selecione...' if x=='' else x)
            if not processo_sel:
                st.warning("Selecione um processo para continuar.")
                st.stop()

        st.markdown("### Cargos com mesma prova *(opcional)*")
        n_conjuntos = st.number_input("Quantos conjuntos?", min_value=0, max_value=20, value=0, step=1)
        conjuntos = []
        for i in range(int(n_conjuntos)):
            val = st.text_input(f"Conjunto {i+1} — códigos separados por vírgula", key=f"conj_{i}", placeholder="Ex: 314, 315")
            if val.strip():
                cods = [c.strip() for c in val.split(',') if c.strip()]
                if len(cods) >= 2:
                    conjuntos.append(cods)

        if st.button("⚙️ Processar", type="primary"):
            with st.spinner("Processando..."):
                try:
                    dados = arquivo.read()
                    buf_res, buf_aloc, resumo = processar(
                        dados,
                        conjuntos_mesma_prova=conjuntos if conjuntos else None,
                        processo=processo_sel or None
                    )
                    st.success(f"✅ {resumo['total']} inscrições processadas!")

                    cols = st.columns(7)
                    for col, (k,l) in zip(cols, [
                        ('total','Total'),('pagos','Pagos'),('deferidos','Deferidos'),
                        ('pendentes','Pendentes'),('indeferidos','Indeferidos'),
                        ('cancelados','Cancelados'),('total_alocacao','Alocação')
                    ]):
                        col.metric(l, resumo[k])

                    st.markdown(f"**Abas geradas:** {', '.join(resumo['abas_resultado'])}")

                    nome_base = (processo_sel or 'RESULTADO').replace('/','_').replace(' ','_')[:50]
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            "📥 Resultado das Inscrições",
                            data=buf_res,
                            file_name=f"RESULTADO_{nome_base}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.caption("Abas: AMPLA, PCD, PNP, COND.ESPECIAL")
                    with c2:
                        st.download_button(
                            "📥 Planilha de Alocação",
                            data=buf_aloc,
                            file_name=f"ALOCACAO_{nome_base}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.caption("Abas: ALOCAÇÃO" + (" + CANCELADOS CONJUNTO" if conjuntos else ""))
                except Exception as e:
                    st.error(f"Erro: {e}")
                    import traceback; st.code(traceback.format_exc())
    st.stop()

# ── PÁGINA DE HOMOLOGAÇÃO ─────────────────────────────────────────────
if st.session_state.get("pagina") == "homologacao":
    import sys
    sys.path.insert(0, "/mount/src/ibgp-minhas-tarefas")
    from gerar_homologacao import processar_homologacao

    st.markdown("""
<style>
header[data-testid="stHeader"]{display:none}
[data-testid="stAppViewContainer"]{background:#eef1f6}
.block-container{padding:1.5rem 2rem!important}
</style>""", unsafe_allow_html=True)

    col_back, col_title = st.columns([1,8])
    with col_back:
        if st.button("← Voltar"):
            st.session_state.pop("pagina", None)
            st.rerun()
    with col_title:
        st.markdown("## 📋 Resultados · Homologação")

    st.markdown("---")
    st.markdown("Faça o upload dos dois arquivos para gerar a planilha de homologação automaticamente.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**1. Planilha de Classificação Final**")
        arquivo_cf = st.file_uploader("Classificação Final (.xlsx)", type=["xlsx"], key="cf_upload")
    with col2:
        st.markdown("**2. Planilha de Dados Gerais dos Candidatos**")
        arquivo_dados = st.file_uploader("Dados dos Candidatos (.xlsx)", type=["xlsx"], key="dados_upload")

    if arquivo_cf and arquivo_dados:
        st.info("✅ Ambos os arquivos carregados. Clique em **Gerar Homologação** para processar.")
        if st.button("⚙️ Gerar Homologação", type="primary"):
            with st.spinner("Processando... isso pode levar alguns segundos."):
                try:
                    bytes_cf    = arquivo_cf.read()
                    bytes_dados = arquivo_dados.read()
                    resultado   = processar_homologacao(bytes_dados, bytes_cf)

                    # Verificar abas geradas
                    import pandas as pd, io
                    xl_check = pd.read_excel(io.BytesIO(resultado), sheet_name=None)
                    resumo_abas = {aba: len(df) for aba, df in xl_check.items()}

                    st.success("✅ Planilha de homologação gerada!")
                    cols = st.columns(len(resumo_abas))
                    for i, (aba, qtd) in enumerate(resumo_abas.items()):
                        cols[i].metric(aba, f"{qtd} candidatos")

                    nome_base = arquivo_cf.name.replace('.xlsx','').replace('CLASSIFICAÇÃO_FINAL','').replace('_BETIM','').strip('_- ')
                    st.download_button(
                        "📥 Baixar Planilha de Homologação",
                        data=resultado,
                        file_name=f"HOMOLOGACAO_{nome_base}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
                    import traceback; st.code(traceback.format_exc())
    st.stop()


# v2026.07.09-inscricoes
# ── LER E INJETAR TEMPLATE ────────────────────────────────────────────
with open("/mount/src/ibgp-minhas-tarefas/template.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("// PLACEHOLDER_TOKEN",
    f"const TOKEN = {json.dumps(token or '')};")
html = html.replace("// PLACEHOLDER_CONFIG",
    f"""const IS_GESTORA    = {'true' if is_gestora   else 'false'};
const IS_CRONOGRAMA = {'true' if is_cronograma else 'false'};
const IS_OPERACIONAL = {'true' if is_operacional else 'false'};
const NOME_USUARIO  = {json.dumps(nome_interno)};
const DADOS_INICIAIS = {dados_iniciais};""")
html = html.replace("// PLACEHOLDER_ATRIB",
    f"const ATRIBUICOES_JS = {json.dumps(ATRIBUICOES)};")

# ── BOTÕES DE NAVEGAÇÃO PARA RESULTADOS (fora do iframe) ─────────────
st.markdown("<style>[data-testid='stChatInput'],[data-testid='stBottom']{display:none!important}</style>", unsafe_allow_html=True)

if logado_microsoft and is_gestora:
    with st.expander("🔑 Token de serviço para contas locais (avançado)"):
        rt_atual = st.session_state.get("refresh_token")
        if rt_atual:
            st.caption("Copie o valor abaixo e salve em **Manage app → Settings → Secrets** como:")
            st.code(f'SERVICE_REFRESH_TOKEN = "{rt_atual}"', language="toml")
            st.caption("Isso permite que contas de login local (como a do Jordan) também vejam as tarefas do Planner. Sem isso configurado, elas continuam sem tarefas. Se parar de funcionar depois de um tempo, basta gerar um novo aqui e atualizar o secret.")
        else:
            st.caption("Nenhum refresh token disponível nesta sessão — saia e entre novamente com Microsoft para gerar um novo.")

components.html(html, height=900, scrolling=False)
