# -*- coding: utf-8 -*-
"""
Motor genérico de classificação final de concursos.

Ideia geral:
  - Cada concurso tem uma lista ordenada de ETAPAS (objetiva, discursiva,
    títulos, heteroidentificação, prova prática, TAF, av. médica,
    av. psicológica, curso de formação...).
  - Cada etapa tem um TIPO de avaliação:
      "pontuacao"      -> soma de campos numéricos, com corte configurável
                           (nota mínima total e/ou não pode zerar item)
      "classificatoria"-> soma pontos, mas NUNCA elimina (ex: títulos)
      "binario"        -> lê uma coluna de resultado (ex: DEFERIDA/INDEFERIDA,
                           APTO/INAPTO) já pronta na planilha. Pode ELIMINAR
                           do concurso (ex: av. médica) ou apenas GATEAR uma
                           reserva de vaga (ex: heteroidentificação -> PNP).
  - Um candidato só é classificado no cargo se: (a) passou em todas as
    etapas eliminatórias que o cargo dele possui, e (b) está presente nos
    dados de todas essas etapas (ou seja, foi de fato convocado/avaliado
    nelas — a convocação em si, por nº de vagas x multiplicador, é uma
    decisão administrativa anterior, refletida simplesmente por quem
    aparece nas planilhas de cada etapa).
  - O TOTAL GERAL é a soma dos totais das etapas "pontuacao"/"classificatoria"
    que o cargo possui.
  - O desempate é uma lista ordenada de critérios, aplicada em cascata.
  - O ranking é calculado separadamente por "pool" (AMPLA, PCD, PNP,
    INDÍGENA, QUILOMBOLA), dentro de cada cargo.
"""
import unicodedata
from dataclasses import dataclass, field


def _norm(s):
    if s is None:
        return ""
    s = str(s).strip().upper()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s


def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


@dataclass
class Candidato:
    inscricao: int
    nome: str = ""
    nascimento: object = None
    cargo: str = ""
    pools: dict = field(default_factory=lambda: {"ampla": True})   # {"ampla":True, "pcd":bool, "pnp":bool, ...}
    etapas: dict = field(default_factory=dict)  # {"objetiva": {"campos":{...}, "total":x, "aprovado":bool}, ...}
    eliminado: bool = False
    motivo_eliminacao: str = ""

    @property
    def total_geral(self):
        t = 0.0
        for et in self.etapas.values():
            if et.get("conta_no_total", True) and is_num(et.get("total")):
                t += et["total"]
        return t


class MotorClassificacao:
    def __init__(self, config):
        self.config = config
        self.candidatos = {}  # inscricao -> Candidato

    # ---------- carregamento de dados ----------

    def get_or_create(self, inscricao, nome=None, nascimento=None, cargo=None):
        c = self.candidatos.get(inscricao)
        if c is None:
            c = Candidato(inscricao=inscricao, nome=nome or "", nascimento=nascimento, cargo=cargo or "")
            self.candidatos[inscricao] = c
        if nome:
            c.nome = nome
        if nascimento is not None:
            c.nascimento = nascimento
        if cargo:
            c.cargo = cargo
        return c

    def carregar_inscricoes(self, linhas_por_pool):
        """linhas_por_pool: {"pcd": [ {inscricao,nome,nascimento,cargo,resultado}, ...], "indigena": [...], ...}
        AMPLA é implícito (todo candidato concorre à ampla)."""
        for pool, linhas in linhas_por_pool.items():
            for l in linhas:
                c = self.get_or_create(l["inscricao"], l.get("nome"), l.get("nascimento"), l.get("cargo"))
                deferido = _norm(l.get("resultado")) == "DEFERIDA"
                c.pools[pool] = deferido

    def carregar_flags_pool(self, linhas, mapa_colunas):
        """Lê as colunas de convocação por vaga (ex: AMPLA/PCD/PN4/IND5/QUILO6,
        que a própria IBGP preenche manualmente com 'SIM'/vazio ao convocar)
        e usa isso DIRETO como pool do candidato — não deriva de 'deferido'
        da inscrição, pois a convocação é uma decisão administrativa própria.
        linhas: [{"inscricao":.., "cargo":.., "nome":.., "AMPLA":"SIM", "PCD":None, ...}]
        mapa_colunas: {"ampla":"AMPLA", "pcd":"PCD", "pnp":"PN4", "indigena":"IND5", "quilombola":"QUILO6"}
        """
        for l in linhas:
            c = self.get_or_create(l["inscricao"], l.get("nome"), l.get("nascimento"), l.get("cargo"))
            for pool, coluna in mapa_colunas.items():
                if coluna not in l:
                    continue  # coluna não fornecida para esta etapa: não sobrescreve
                valor = l.get(coluna)
                c.pools[pool] = _norm(valor) == "SIM"

    def carregar_etapa_pontuacao(self, nome_etapa, linhas, campos, corte=None, conta_no_total=True):
        """linhas: [{"inscricao":..,"cargo":..,"nome":..,"nascimento":..,"valores":{"CAMPO":n,...}, "total":n}]
        corte: {"nota_minima_total": X, "nao_zerar": True/False, "campos_nao_zerar": [...]} ou None (sem corte)."""
        for l in linhas:
            c = self.get_or_create(l["inscricao"], l.get("nome"), l.get("nascimento"), l.get("cargo"))
            valores = l.get("valores", {})
            total = l.get("total")
            aprovado = True
            motivo = ""
            if corte:
                if not is_num(total):
                    aprovado = False
                    motivo = f"{nome_etapa}: ausente/sem nota numérica ({total!r})"
                else:
                    minimo = corte.get("nota_minima_total")
                    if minimo is not None and total < minimo:
                        aprovado = False
                        motivo = f"{nome_etapa}: total {total} < mínimo {minimo}"
                    if aprovado and corte.get("nao_zerar"):
                        campos_check = corte.get("campos_nao_zerar", campos)
                        for campo in campos_check:
                            v = valores.get(campo)
                            if is_num(v) and v == 0:
                                aprovado = False
                                motivo = f"{nome_etapa}: zerou em {campo}"
                                break
            c.etapas[nome_etapa] = {
                "campos": valores, "total": total, "aprovado": aprovado,
                "conta_no_total": conta_no_total,
            }
            if not aprovado:
                c.eliminado = True
                c.motivo_eliminacao = c.motivo_eliminacao or motivo

    def carregar_etapa_binaria(self, nome_etapa, linhas, campo_valor_aprovado="DEFERIDA",
                                elimina_do_concurso=False, gate_pool=None):
        """linhas: [{"inscricao":..,"cargo":..,"resultado":..}]
        Se elimina_do_concurso=True -> reprovado aqui é eliminado de tudo (ex: av. médica).
        Se gate_pool for definido (ex: "pnp") -> só marca o pool como válido se resultado==aprovado;
        não elimina o candidato do concurso, só da reserva de vaga (cai pra ampla)."""
        for l in linhas:
            c = self.get_or_create(l["inscricao"], l.get("nome"), l.get("nascimento"), l.get("cargo"))
            ok = _norm(l.get("resultado")) == _norm(campo_valor_aprovado)
            c.etapas[nome_etapa] = {"resultado": l.get("resultado"), "aprovado": ok, "conta_no_total": False}
            if gate_pool:
                c.pools[gate_pool] = ok and c.pools.get(gate_pool, False)
            if elimina_do_concurso and not ok:
                c.eliminado = True
                c.motivo_eliminacao = c.motivo_eliminacao or f"{nome_etapa}: não apto/deferido"

    # ---------- desempate ----------

    def _chave_desempate(self, c, data_referencia):
        chave = []
        for crit in self.config.get("desempate", []):
            tipo = crit["tipo"]
            if tipo == "idoso_60":
                idade = self._idade(c.nascimento, data_referencia)
                chave.append(0 if (idade is not None and idade >= 60) else 1)
            elif tipo == "maior_nota":
                campo = crit["campo"]
                v = None
                for et in c.etapas.values():
                    if campo in et.get("campos", {}):
                        v = et["campos"][campo]
                        break
                chave.append(-(v if is_num(v) else -1e9))
            elif tipo == "jurado":
                chave.append(0 if c.pools.get("jurado") else 1)
            elif tipo == "idade_maior":
                # compara a data de nascimento diretamente (nascimento mais
                # antigo = mais velho = tem preferência) evitando empates
                # que a idade em anos arredondada esconderia
                if c.nascimento is not None:
                    chave.append(c.nascimento.toordinal() if hasattr(c.nascimento, "toordinal") else 0)
                else:
                    chave.append(float("inf"))
            else:
                chave.append(0)
        return chave

    @staticmethod
    def _idade(nascimento, data_referencia):
        if nascimento is None or data_referencia is None:
            return None
        try:
            anos = data_referencia.year - nascimento.year
            if (data_referencia.month, data_referencia.day) < (nascimento.month, nascimento.day):
                anos -= 1
            return anos
        except Exception:
            return None

    # ---------- classificação final ----------

    def classificar(self, data_referencia_desempate=None):
        aptos = [c for c in self.candidatos.values() if not c.eliminado]
        # ordena por total geral desc, depois critérios de desempate
        aptos.sort(key=lambda c: (-c.total_geral, self._chave_desempate(c, data_referencia_desempate)))

        pools_config = self.config.get("pools", ["ampla", "pcd", "pnp", "indigena", "quilombola"])
        pools_reserva = [p for p in pools_config if p != "ampla"]
        # ampla_exclusiva=True *padrão/comportamento observado em Betim): quem
        # está deferido em alguma reserva de vaga NÃO concorre na ampla, só
        # na sua reserva. Se False, todo mundo concorre na ampla também.
        ampla_exclusiva = self.config.get("ampla_exclusiva", False)
        por_cargo = {}
        for c in aptos:
            por_cargo.setdefault(c.cargo, []).append(c)

        ranking = {}  # cargo -> pool -> [candidatos em ordem]
        for cargo, lista in por_cargo.items():
            ranking[cargo] = {}
            for pool in pools_config:
                sub = [c for c in lista if c.pools.get(pool)]
                ranking[cargo][pool] = sub
        self.ranking = ranking
        return ranking
