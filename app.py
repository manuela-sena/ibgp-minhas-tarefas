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
    # Capturar login local via query param
    if "login_u" in st.query_params and "login_p" in st.query_params:
        u_input = st.query_params["login_u"]
        p_input = st.query_params["login_p"]
        st.query_params.clear()
        usuario_encontrado = None
        for u in USUARIOS:
            if not u.get("ativo", True): continue
            if u.get("auth_tipo") != "local": continue
            nomes = [u.get("nome_interno","").lower()] + [a.lower() for a in u.get("aliases",[])]
            if u_input.strip().lower() in nomes:
                usuario_encontrado = u; break
        if usuario_encontrado:
            if usuario_encontrado.get("primeiro_acesso"):
                st.session_state["primeiro_acesso_user"] = usuario_encontrado["nome_interno"]
                if verificar_senha(p_input, usuario_encontrado.get("senha_hash","")):
                    st.session_state["convite_ok"] = True
                else:
                    st.session_state["login_erro"] = "Código de convite incorreto."
            elif verificar_senha(p_input, usuario_encontrado.get("senha_hash","")):
                st.session_state["local_user"] = usuario_encontrado["nome_interno"]
                st.rerun()
            else:
                st.session_state["login_erro"] = "Senha incorreta."
        else:
            st.session_state["login_erro"] = "Usuário não encontrado."
        st.rerun()

    if "nova_senha" in st.query_params and st.session_state.get("convite_ok"):
        nome_alvo = st.session_state.get("primeiro_acesso_user","")
        nova = st.query_params["nova_senha"]
        st.query_params.clear()
        if len(nova) < 6:
            st.session_state["login_erro"] = "Senha deve ter pelo menos 6 caracteres."
        else:
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

    erro          = st.session_state.pop("login_erro", "")
    primeiro_acesso = st.session_state.get("convite_ok", False)
    primeiro_nome   = st.session_state.get("primeiro_acesso_user", "")
    ms_url        = auth_url()
    erro_html     = f'<div class="erro">{erro}</div>' if erro else ""

    if primeiro_acesso:
        html_login = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#eef1f6;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.card{{background:#fff;border-radius:20px;padding:2.5rem 2rem;width:100%;max-width:400px;box-shadow:0 8px 40px rgba(16,30,54,0.12)}}
.logo{{width:52px;height:52px;object-fit:contain;display:block;margin:0 auto 1.2rem}}
h1{{font-size:1.1rem;font-weight:700;color:#1f2a3d;text-align:center;margin-bottom:.3rem}}
.sub{{color:#7a869c;font-size:.85rem;text-align:center;margin-bottom:1.8rem;line-height:1.5}}
.field{{margin-bottom:.9rem}}
label{{display:block;font-size:.8rem;font-weight:600;color:#41506b;margin-bottom:.4rem}}
input{{width:100%;padding:.65rem .9rem;border:1.5px solid #d7dde7;border-radius:10px;font-size:.9rem;color:#1f2a3d;outline:none}}
input:focus{{border-color:#1f4e8c;box-shadow:0 0 0 3px rgba(31,78,140,.1)}}
.btn{{width:100%;padding:.75rem;background:#1f4e8c;color:#fff;border:none;border-radius:10px;font-size:.95rem;font-weight:600;cursor:pointer;margin-top:.5rem}}
.btn:hover{{background:#1a4378}}
.erro{{background:#fdeceb;color:#c0322f;border-radius:8px;padding:.6rem .9rem;font-size:.82rem;margin-bottom:1rem;font-weight:500}}
</style></head><body>
<div class="card">
  <img class="logo" src="https://raw.githubusercontent.com/manuela-sena/ibgp-minhas-tarefas/main/logo.png">
  <h1>Primeiro acesso</h1>
  <p class="sub">Olá, <strong>{primeiro_nome}</strong>!<br>Defina sua senha para continuar.</p>
  {erro_html}
  <form onsubmit="definirSenha(event)">
    <div class="field"><label>Nova senha</label><input id="ns" type="password" placeholder="Mínimo 6 caracteres" required></div>
    <div class="field"><label>Confirmar senha</label><input id="cs" type="password" placeholder="Repita a senha" required></div>
    <button class="btn" type="submit">✅ Definir senha e entrar</button>
  </form>
</div>
<script>
function definirSenha(e){{
  e.preventDefault();
  var ns=document.getElementById('ns').value;
  var cs=document.getElementById('cs').value;
  if(ns!==cs){{alert('As senhas não coincidem.');return;}}
  window.top.location.href=window.top.location.origin+window.top.location.pathname+'?nova_senha='+encodeURIComponent(ns);
}}
</script></body></html>"""
    else:
        html_login = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#eef1f6;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
.card{{background:#fff;border-radius:20px;padding:2.5rem 2rem;width:100%;max-width:400px;box-shadow:0 8px 40px rgba(16,30,54,0.12)}}
.logo{{width:56px;height:56px;object-fit:contain;display:block;margin:0 auto 1.2rem}}
h1{{font-size:1.1rem;font-weight:700;color:#1f2a3d;text-align:center;margin-bottom:.3rem}}
.sub{{color:#7a869c;font-size:.85rem;text-align:center;margin-bottom:2rem}}
.btn-ms{{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:.8rem;background:#1f4e8c;color:#fff;border:none;border-radius:12px;font-size:.95rem;font-weight:600;cursor:pointer;text-decoration:none;margin-bottom:1.2rem}}
.btn-ms:hover{{background:#1a4378}}
.divider{{display:flex;align-items:center;gap:.8rem;margin-bottom:1.2rem}}
.divider::before,.divider::after{{content:'';flex:1;height:1px;background:#e2e7ef}}
.divider span{{color:#b0bac8;font-size:.8rem;white-space:nowrap}}
.field{{margin-bottom:.9rem}}
label{{display:block;font-size:.8rem;font-weight:600;color:#41506b;margin-bottom:.4rem}}
input{{width:100%;padding:.65rem .9rem;border:1.5px solid #d7dde7;border-radius:10px;font-size:.9rem;color:#1f2a3d;outline:none}}
input:focus{{border-color:#1f4e8c;box-shadow:0 0 0 3px rgba(31,78,140,.1)}}
.btn-local{{width:100%;padding:.72rem;background:#f4f6fa;color:#1f2a3d;border:1.5px solid #e2e7ef;border-radius:10px;font-size:.9rem;font-weight:600;cursor:pointer;margin-top:.3rem}}
.btn-local:hover{{background:#eaecf2}}
.erro{{background:#fdeceb;color:#c0322f;border-radius:8px;padding:.6rem .9rem;font-size:.82rem;margin-bottom:1rem;font-weight:500}}
</style></head><body>
<div class="card">
  <img class="logo" src="https://raw.githubusercontent.com/manuela-sena/ibgp-minhas-tarefas/main/logo.png">
  <h1>IBGP · Minhas Tarefas</h1>
  <p class="sub">Acesso restrito à equipe IBGP</p>
  <a class="btn-ms" href="{ms_url}">
    <svg width="20" height="20" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
      <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
      <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
      <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
    </svg>
    Entrar com Microsoft
  </a>
  <div class="divider"><span>ou acesso com senha</span></div>
  {erro_html}
  <form onsubmit="loginLocal(event)">
    <div class="field"><label>Usuário</label><input id="lu" type="text" placeholder="Seu usuário" autocomplete="username"></div>
    <div class="field"><label>Senha</label><input id="lp" type="password" placeholder="Sua senha" autocomplete="current-password"></div>
    <button class="btn-local" type="submit">Entrar com usuário e senha</button>
  </form>
</div>
<script>
function loginLocal(e){{
  e.preventDefault();
  var u=document.getElementById('lu').value.trim();
  var p=document.getElementById('lp').value;
  if(!u||!p){{alert('Preencha usuário e senha.');return;}}
  window.top.location.href=window.top.location.origin+window.top.location.pathname+'?login_u='+encodeURIComponent(u)+'&login_p='+encodeURIComponent(p);
}}
</script></body></html>"""

    components.html(html_login, height=600, scrolling=False)
    st.stop()

token = st.session_state.get("access_token", None)

# ── USUÁRIO ───────────────────────────────────────────────────────────
if logado_local:
    # Login local — nome vem direto da sessão
    nome_interno = st.session_state["local_user"]
    token = None  # Sem token Microsoft
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

# ── GERAR CÓDIGO DE CONVITE ───────────────────────────────────────────
if "gerar_convite" in st.query_params and is_gestora:
    try:
        nome_alvo = st.query_params["gerar_convite"]
        codigo    = gerar_codigo()
        GH_TOKEN  = st.secrets.get("GITHUB_TOKEN","")
        for u in USUARIOS:
            if u.get("nome_interno") == nome_alvo and u.get("auth_tipo") == "local":
                u["senha_hash"]     = hash_senha(codigo)
                u["primeiro_acesso"] = True
        salvar_usuarios_github(USUARIOS, GH_TOKEN)
        st.session_state["convite_gerado"] = {"nome": nome_alvo, "codigo": codigo}
    except Exception as e:
        st.session_state["convite_gerado"] = {"erro": str(e)}
    st.query_params.clear()
    st.rerun()

# ── SALVAR USUÁRIOS (acionado via query param, só gestoras) ──────────
if "salvar_usuarios" in st.query_params:
    if is_gestora:
        try:
            novos = json.loads(st.query_params["salvar_usuarios"])
            GH_TOKEN = st.secrets.get("GITHUB_TOKEN","")
            REPO = "manuela-sena/ibgp-minhas-tarefas"
            # Buscar SHA atual
            r_sha = requests.get(
                f"https://api.github.com/repos/{REPO}/contents/usuarios.json",
                headers={"Authorization": f"Bearer {GH_TOKEN}"}
            )
            sha = r_sha.json().get("sha","")
            conteudo = json.dumps({"usuarios": novos}, ensure_ascii=False, indent=2)
            import base64
            r_save = requests.put(
                f"https://api.github.com/repos/{REPO}/contents/usuarios.json",
                headers={"Authorization": f"Bearer {GH_TOKEN}", "Content-Type":"application/json"},
                json={"message":"feat: atualização de usuários via app","content": base64.b64encode(conteudo.encode()).decode(),"sha":sha}
            )
            if "commit" in r_save.json():
                st.session_state["usuarios_msg"] = "✅ Usuários salvos com sucesso!"
            else:
                st.session_state["usuarios_msg"] = f"⚠️ Erro: {r_save.json().get('message','?')}"
        except Exception as e:
            st.session_state["usuarios_msg"] = f"⚠️ Erro: {e}"
    st.query_params.clear()
    st.rerun()

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
def buscar_tarefas(token):
    # Usuário local sem token Microsoft — retorna vazio
    if not token: return [], [], {}, None
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
    if not plano_id: return [], [], {}, None
    buckets = {b["id"]:b["name"]
               for b in _g(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/buckets").get("value",[])}
    tarefas, concluidas = [], []
    limite_48h = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(hours=48)
    for t in _g_all(f"https://graph.microsoft.com/v1.0/planner/plans/{plano_id}/tasks"):
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
    tarefas, concluidas, buckets, plano_id = buscar_tarefas(token or "")

# ── MONTAR DADOS_INICIAIS ─────────────────────────────────────────────
cron_result  = st.session_state.pop(CRON_RESULT_KEY, None)
cron_nome    = st.session_state.get("cron_nome","")
planner_ok   = st.session_state.pop("planner_ok", None)
planner_err  = st.session_state.pop("planner_err", None)

usuarios_msg = st.session_state.pop("usuarios_msg", None)

convite_gerado = st.session_state.pop("convite_gerado", None)

dados_iniciais = json.dumps({
    "tarefas"      : tarefas,
    "concluidas"   : concluidas,
    "buckets"      : buckets,
    "planoId"      : plano_id,
    "cronResult"   : cron_result,
    "cronNome"     : cron_nome,
    "plannerOk"    : planner_ok,
    "plannerErr"   : planner_err,
    "usuarios"     : USUARIOS,
    "usuariosMsg"  : usuarios_msg,
    "conviteGerado": convite_gerado,
})

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

components.html(html, height=900, scrolling=False)
