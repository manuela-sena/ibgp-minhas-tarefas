"""
Motor de Cálculo de Cronograma IBGP
Suporta dois tipos de certame:
- CONCURSO/PSP: regras da aba CRONOGRAMA CONCURSO-PSP
- GUARDA: regras da aba CRONOGRAMA GUARDA
"""

from datetime import date, timedelta
from typing import Optional

# ─── FERIADOS NACIONAIS FIXOS ─────────────────────────────────────────────────
FERIADOS_FIXOS = [
    (1, 1),   # Confraternização Universal
    (21, 4),  # Tiradentes
    (1, 5),   # Dia do Trabalho
    (7, 9),   # Independência
    (12, 10), # Nossa Senhora Aparecida
    (2, 11),  # Finados
    (15, 11), # Proclamação da República
    (25, 12), # Natal
]

def pascoa(ano: int) -> date:
    a = ano % 19
    b = ano // 100
    c = ano % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)

def feriados_moveis(ano: int) -> list:
    p = pascoa(ano)
    return [
        p - timedelta(days=48),
        p - timedelta(days=47),
        p - timedelta(days=2),
        p,
        p + timedelta(days=60),
    ]

def is_feriado(d: date) -> bool:
    if (d.day, d.month) in FERIADOS_FIXOS:
        return True
    if d in feriados_moveis(d.year):
        return True
    return False

def is_recesso(d: date) -> bool:
    if d.month == 12 and d.day >= 20:
        return True
    if d.month == 1 and d.day <= 5:
        return True
    return False

def is_util(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    if is_feriado(d):
        return False
    if is_recesso(d):
        return False
    return True

def proximo_util(d: date) -> date:
    while not is_util(d):
        d += timedelta(days=1)
    return d

def proximo_util_apos(d: date) -> date:
    d += timedelta(days=1)
    return proximo_util(d)

def adicionar_dias_uteis(d: date, n: int) -> date:
    count = 0
    atual = d
    while count < n:
        atual += timedelta(days=1)
        if is_util(atual):
            count += 1
    return atual

def segundo_util_apos(d: date) -> date:
    return adicionar_dias_uteis(d, 2)

def proximo_dia_semana(d: date, dia: int, semanas_depois: int = 0) -> date:
    dias_ate = (dia - d.weekday()) % 7
    if dias_ate == 0:
        dias_ate = 7
    return d + timedelta(days=dias_ate + semanas_depois * 7)

def proximo_domingo(d: date) -> date:
    dias_ate = (6 - d.weekday()) % 7
    if dias_ate == 0:
        dias_ate = 7
    return d + timedelta(days=dias_ate)

def proxima_terca(d: date, semanas_depois: int = 0) -> date:
    resultado = proximo_dia_semana(d, 1, semanas_depois)
    if not is_util(resultado):
        resultado = proximo_util_apos(resultado)
    return resultado

def dias_uteis_antes(d: date, n: int) -> date:
    """Retorna a data n dias úteis ANTES de d."""
    count = 0
    atual = d
    while count < n:
        atual -= timedelta(days=1)
        if is_util(atual):
            count += 1
    return atual


# ─── MOTOR CONCURSO / PSP ─────────────────────────────────────────────────────

def calcular_concurso_psp(
    data_publicacao: date,
    tem_objetiva: bool = True,
    tem_inscricao: bool = True,
    tem_isencao: bool = True,
    tem_discursiva: bool = False,
    tem_pratica: bool = False,
    tem_taf: bool = False,
    tem_titulos: bool = False,
    tem_psicologica: bool = False,
    tem_medica: bool = False,
    tem_clinica: bool = False,
    tem_hetero: bool = False,
    tem_entrevista: bool = False,
    tem_competencias: bool = False,
    concomitancia_titulos_pratica: bool = False,
) -> list:
    tarefas = []
    seq = 1

    def add(atividade, inicio, fim=None):
        nonlocal seq
        tarefas.append({"seq": seq, "atividade": atividade,
                        "data_inicio": inicio, "data_fim": fim or inicio})
        seq += 1

    # 1. Publicação
    pub = proximo_util(data_publicacao)
    add("PUBLICAÇÃO DO EDITAL", pub)

    if tem_isencao:
        inicio_isencao = proximo_util(pub + timedelta(days=60))
        fim_isencao = adicionar_dias_uteis(inicio_isencao, 2)
        add("PERÍODO SOLICITAÇÃO DE ISENÇÃO", inicio_isencao, fim_isencao)

    if tem_inscricao:
        inicio_insc = inicio_isencao if tem_isencao else proximo_util(pub + timedelta(days=60))
        fim_insc_raw = inicio_insc + timedelta(days=29)
        fim_insc = proximo_util(fim_insc_raw) if not is_util(fim_insc_raw) else fim_insc_raw
        add("PERÍODO DE INSCRIÇÕES/PCD/SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS", inicio_insc, fim_insc)

    if tem_isencao:
        res_prel_isencao = adicionar_dias_uteis(fim_isencao, 5)
        add("RESULTADO PRELIMINAR DA SOLICITAÇÃO DE ISENÇÃO", res_prel_isencao)
        inicio_rec_isencao = proximo_util_apos(res_prel_isencao)
        fim_rec_isencao = adicionar_dias_uteis(inicio_rec_isencao, 2)
        add("ABERTURA DE RECURSO CONTRA RESULTADO PRELIMINAR DA SOLICITAÇÃO DE ISENÇÃO",
            inicio_rec_isencao, fim_rec_isencao)
        analise_isencao = adicionar_dias_uteis(fim_rec_isencao, 2)
        add("ANÁLISE DA BANCA DOS RECURSOS CONTRA SOLICITAÇÃO DE ISENÇÃO", analise_isencao)
        res_pos_isencao = proximo_util_apos(analise_isencao)
        add("RESULTADO PÓS-RECURSO DA SOLICITAÇÃO DE ISENÇÃO", res_pos_isencao)

    if tem_inscricao:
        boleto = proximo_util_apos(fim_insc)
        add("2ª VIA E PAGAMENTO DO BOLETO", boleto)
        res_prel_insc = adicionar_dias_uteis(fim_insc, 5)
        add("RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL", res_prel_insc)
        inicio_rec_insc = proximo_util_apos(res_prel_insc)
        fim_rec_insc = adicionar_dias_uteis(inicio_rec_insc, 2)
        add("ABERTURA DE RECURSO CONTRA RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL",
            inicio_rec_insc, fim_rec_insc)
        analise_insc = adicionar_dias_uteis(fim_rec_insc, 2)
        add("ANÁLISE DA BANCA DOS RECURSOS CONTRA RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL",
            analise_insc)
        res_pos_insc = proximo_util_apos(analise_insc)
        add("RESULTADO PÓS-RECURSO INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL", res_pos_insc)

        if tem_objetiva:
            cdi = proxima_terca(res_pos_insc, semanas_depois=1)
            add("COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI) - PUBLICAÇÃO DO LOCAL DE PROVA", cdi)
            prova_obj = proximo_domingo(cdi)
            nome_prova = "PROVA OBJETIVA E PROVA DISCURSIVA" if tem_discursiva else "PROVA OBJETIVA"
            add(nome_prova, prova_obj)
            add("GABARITO PRELIMINAR", prova_obj)
            inicio_rec_q = proximo_util_apos(prova_obj)
            fim_rec_q = adicionar_dias_uteis(inicio_rec_q, 2)
            add("ABERTURA DE RECURSO CONTRA QUESTÕES PROVA OBJETIVA", inicio_rec_q, fim_rec_q)
            analise_q = fim_rec_q + timedelta(days=15)
            add("ANÁLISE DA BANCA DOS RECURSOS CONTRA QUESTÕES PROVA OBJETIVA", analise_q)
            gabarito_pos = proximo_util_apos(analise_q)
            add("GABARITO PÓS-RECURSO", gabarito_pos)
            inicio_rec_gab = proximo_util_apos(gabarito_pos)
            fim_rec_gab = adicionar_dias_uteis(inicio_rec_gab, 2)
            add("ABERTURA DE RECURSO CONTRA GABARITO PÓS-RECURSO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES)",
                inicio_rec_gab, fim_rec_gab)
            analise_gab = adicionar_dias_uteis(fim_rec_gab, 4)
            add("ANÁLISE DA BANCA DOS RECURSOS CONTRA GABARITO PÓS-RECURSO", analise_gab)
            res_prel_total = proximo_util_apos(analise_gab)
            add("GABARITO PÓS-RECURSO - RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA",
                res_prel_total)
            if tem_discursiva:
                add("ENVIAR PROVAS DISCURSIVAS PARA CORREÇÃO", res_prel_total)
            inicio_rec_total = proximo_util_apos(res_prel_total)
            fim_rec_total = adicionar_dias_uteis(inicio_rec_total, 2)
            add("ABERTURA DE RECURSO CONTRA TOTALIZAÇÃO DA PROVA OBJETIVA", inicio_rec_total, fim_rec_total)
            analise_total = adicionar_dias_uteis(fim_rec_total, 3)
            add("ANÁLISE BANCA DOS RECURSOS CONTRA TOTALIZAÇÃO DA PROVA OBJETIVA", analise_total)
            res_pos_total = proximo_util_apos(analise_total)
            if tem_discursiva:
                add("RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA E RESULTADO PRELIMINAR DA PROVA DISCURSIVA",
                    res_pos_total)
                inicio_rec_disc = proximo_util_apos(res_pos_total)
                fim_rec_disc = adicionar_dias_uteis(inicio_rec_disc, 2)
                add("ABERTURA DE RECURSO CONTRA O RESULTADO DA PROVA DISCURSIVA", inicio_rec_disc, fim_rec_disc)
                analise_disc = adicionar_dias_uteis(fim_rec_disc, 3)
                add("PERÍODO DE ANÁLISE DOS RECURSOS DA PROVA DISCURSIVA", analise_disc)
                res_pos_disc = proximo_util_apos(analise_disc)
                add("RESULTADO PÓS-RECURSO DA PROVA DISCURSIVA", res_pos_disc)
                ref_fase_anterior = res_pos_disc
            else:
                add("RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA", res_pos_total)
                ref_fase_anterior = res_pos_total
        else:
            ref_fase_anterior = res_pos_insc

        # Prova Prática / TAF
        if tem_pratica or tem_taf:
            nome_pratica = "REALIZAÇÃO PROVA PRÁTICA" if tem_pratica else "REALIZAÇÃO DA PROVA DE CAPACIDADE FÍSICA"
            conv_pratica = proxima_terca(ref_fase_anterior)
            add(f"CONVOCAÇÃO PARA {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}", conv_pratica)
            sabado_pratica = proximo_dia_semana(conv_pratica, 5)
            domingo_pratica = sabado_pratica + timedelta(days=1)
            add(nome_pratica, sabado_pratica, domingo_pratica)
            res_prel_pratica = proximo_util(domingo_pratica + timedelta(days=7))
            add(f"RESULTADO PRELIMINAR {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}", res_prel_pratica)
            inicio_rec_pratica = proximo_util_apos(res_prel_pratica)
            fim_rec_pratica = adicionar_dias_uteis(inicio_rec_pratica, 2)
            add(f"ABERTURA DE RECURSO CONTRA O RESULTADO {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}",
                inicio_rec_pratica, fim_rec_pratica)
            analise_pratica = adicionar_dias_uteis(fim_rec_pratica, 3)
            add(f"PERÍODO DE ANÁLISE DOS RECURSOS DA {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}",
                analise_pratica)
            res_pos_pratica = proximo_util_apos(analise_pratica)
            add(f"RESULTADO PÓS-RECURSO DA {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}",
                res_pos_pratica)
            ref_fase_anterior = res_pos_pratica

        # Títulos
        if tem_titulos:
            ref_titulos = (res_pos_disc if tem_discursiva else res_pos_total) if concomitancia_titulos_pratica and (tem_pratica or tem_taf) and tem_objetiva else ref_fase_anterior
            add("CONVOCAÇÃO PARA PROVA DE TÍTULOS", ref_titulos)
            inicio_titulos = proximo_util_apos(ref_titulos)
            fim_titulos = adicionar_dias_uteis(inicio_titulos, 2)
            add("PERÍODO PARA ENVIO DOS TÍTULOS", inicio_titulos, fim_titulos)
            analise_titulos = adicionar_dias_uteis(fim_titulos, 5)
            add("PERÍODO PARA ANÁLISE DOS TÍTULOS", analise_titulos)
            res_prel_titulos = proximo_util_apos(analise_titulos)
            add("RESULTADO PRELIMINAR PROVA DE TÍTULOS", res_prel_titulos)
            inicio_rec_titulos = proximo_util_apos(res_prel_titulos)
            fim_rec_titulos = adicionar_dias_uteis(inicio_rec_titulos, 2)
            add("ABERTURA DE RECURSO CONTRA O RESULTADO PROVA DE TÍTULOS", inicio_rec_titulos, fim_rec_titulos)
            analise_rec_titulos = adicionar_dias_uteis(fim_rec_titulos, 3)
            add("PERÍODO DE ANÁLISE DOS RECURSOS DA PROVA DE TÍTULOS", analise_rec_titulos)
            res_pos_titulos = proximo_util_apos(analise_rec_titulos)
            add("RESULTADO PÓS-RECURSO DA PROVA DE TÍTULOS", res_pos_titulos)
            ref_fase_anterior = res_pos_titulos

        # Avaliação Psicológica
        if tem_psicologica:
            conv_psico = proxima_terca(ref_fase_anterior)
            add("CONVOCAÇÃO PARA AVALIAÇÃO PSICOLÓGICA", conv_psico)
            sabado_psico = proximo_dia_semana(conv_psico, 5)
            domingo_psico = sabado_psico + timedelta(days=1)
            add("REALIZAÇÃO DA AVALIAÇÃO PSICOLÓGICA", sabado_psico, domingo_psico)
            correcao_psico = adicionar_dias_uteis(domingo_psico, 3)
            add("CORREÇÃO DOS TESTES DA AVALIAÇÃO PSICOLÓGICA", correcao_psico)
            res_prel_psico = proximo_util_apos(correcao_psico)
            add("RESULTADO PRELIMINAR DA AVALIAÇÃO PSICOLÓGICA", res_prel_psico)
            if tem_entrevista:
                manifestacao = adicionar_dias_uteis(res_prel_psico, 1)
                add("MANIFESTAÇÃO DE INTERESSE DE RECEBER ENTREVISTA DEVOLUTIVA", manifestacao)
                entrevista = proximo_util_apos(manifestacao)
                add("REALIZAÇÃO DA ENTREVISTA DEVOLUTIVA", entrevista)
                inicio_rec_psico = adicionar_dias_uteis(entrevista, 3)
            else:
                inicio_rec_psico = proximo_util_apos(res_prel_psico)
            fim_rec_psico = adicionar_dias_uteis(inicio_rec_psico, 2)
            add("ABERTURA DE RECURSOS CONTRA AVALIAÇÃO PSICOLÓGICA", inicio_rec_psico, fim_rec_psico)
            analise_psico = adicionar_dias_uteis(fim_rec_psico, 3)
            add("ANÁLISE BANCA DOS RECURSOS DA AVALIAÇÃO PSICOLÓGICA", analise_psico)
            res_pos_psico = proximo_util_apos(analise_psico)
            add("RESULTADO PÓS-RECURSO DA AVALIAÇÃO PSICOLÓGICA", res_pos_psico)
            ref_fase_anterior = res_pos_psico


        # Entrevista por Competências
        if tem_competencias:
            conv_comp = proxima_terca(ref_fase_anterior)
            add("CONVOCAÇÃO PARA ENTREVISTA POR COMPETÊNCIAS", conv_comp)
            sabado_comp = proximo_dia_semana(conv_comp, 5)
            domingo_comp = sabado_comp + timedelta(days=1)
            add("REALIZAÇÃO ENTREVISTA POR COMPETÊNCIAS", sabado_comp, domingo_comp)
            res_prel_comp = adicionar_dias_uteis(domingo_comp, 2)
            add("RESULTADO PRELIMINAR DA ENTREVISTA POR COMPETÊNCIAS", res_prel_comp)
            inicio_rec_comp = proximo_util_apos(res_prel_comp)
            fim_rec_comp = adicionar_dias_uteis(inicio_rec_comp, 2)
            add("ABERTURA DE RECURSO CONTRA A ENTREVISTA POR COMPETÊNCIAS", inicio_rec_comp, fim_rec_comp)
            analise_comp = adicionar_dias_uteis(fim_rec_comp, 2)
            add("ANÁLISE BANCA DOS RECURSOS DA ENTREVISTA POR COMPETÊNCIAS", analise_comp)
            res_pos_comp = proximo_util_apos(analise_comp)
            add("RESULTADO PÓS-RECURSO DA ENTREVISTA POR COMPETÊNCIAS", res_pos_comp)
            ref_fase_anterior = res_pos_comp

        # Avaliação Médica
        if tem_medica:
            conv_med = proxima_terca(ref_fase_anterior)
            add("CONVOCAÇÃO PARA AVALIAÇÃO MÉDICA", conv_med)
            sabado_med = proximo_dia_semana(conv_med, 5)
            domingo_med = sabado_med + timedelta(days=1)
            add("REALIZAÇÃO DA AVALIAÇÃO MÉDICA", sabado_med, domingo_med)
            res_prel_med = adicionar_dias_uteis(domingo_med, 3)
            add("RESULTADO PRELIMINAR DA AVALIAÇÃO MÉDICA", res_prel_med)
            inicio_rec_med = proximo_util_apos(res_prel_med)
            fim_rec_med = adicionar_dias_uteis(inicio_rec_med, 2)
            add("ABERTURA DE RECURSOS CONTRA AVALIAÇÃO MÉDICA", inicio_rec_med, fim_rec_med)
            analise_med = adicionar_dias_uteis(fim_rec_med, 2)
            add("ANÁLISE DA BANCA DOS RECURSOS CONTRA AVALIAÇÃO MÉDICA", analise_med)
            res_pos_med = proximo_util_apos(analise_med)
            add("RESULTADO PÓS-RECURSO DA AVALIAÇÃO MÉDICA", res_pos_med)
            ref_fase_anterior = res_pos_med

        # Avaliação Clínica
        if tem_clinica:
            conv_clin = proxima_terca(ref_fase_anterior)
            add("CONVOCAÇÃO PARA AVALIAÇÃO CLÍNICA", conv_clin)
            sabado_clin = proximo_dia_semana(conv_clin, 5)
            domingo_clin = sabado_clin + timedelta(days=1)
            add("REALIZAÇÃO DA AVALIAÇÃO CLÍNICA", sabado_clin, domingo_clin)
            res_prel_clin = adicionar_dias_uteis(domingo_clin, 3)
            add("RESULTADO PRELIMINAR DA AVALIAÇÃO CLÍNICA", res_prel_clin)
            inicio_rec_clin = proximo_util_apos(res_prel_clin)
            fim_rec_clin = adicionar_dias_uteis(inicio_rec_clin, 2)
            add("ABERTURA DE RECURSOS CONTRA AVALIAÇÃO CLÍNICA", inicio_rec_clin, fim_rec_clin)
            analise_clin = adicionar_dias_uteis(fim_rec_clin, 2)
            add("ANÁLISE DA BANCA DOS RECURSOS CONTRA AVALIAÇÃO CLÍNICA", analise_clin)
            res_pos_clin = proximo_util_apos(analise_clin)
            add("RESULTADO PÓS-RECURSO DA AVALIAÇÃO CLÍNICA", res_pos_clin)
            ref_fase_anterior = res_pos_clin

        # Heteroidentificação
        if tem_hetero:
            conv_hetero = proximo_util_apos(ref_fase_anterior)
            add("CONVOCAÇÃO PROCEDIMENTO HETEROIDENTIFICAÇÃO", conv_hetero)
            inicio_foto = proximo_util_apos(conv_hetero)
            fim_foto = adicionar_dias_uteis(inicio_foto, 2)
            add("ENVIO FOTO/VÍDEO PARA PROCEDIMENTO HETEROIDENTIFICAÇÃO", inicio_foto, fim_foto)
            inicio_av_hetero = proximo_util_apos(fim_foto)
            fim_av_hetero = adicionar_dias_uteis(inicio_av_hetero, 2)
            add("PROCEDIMENTO HETEROIDENTIFICAÇÃO - AVALIAÇÃO DA BANCA", inicio_av_hetero, fim_av_hetero)
            res_prel_hetero = proximo_util_apos(fim_av_hetero)
            add("RESULTADO PRELIMINAR DO PROCEDIMENTO HETEROIDENTIFICAÇÃO", res_prel_hetero)
            inicio_rec_hetero = proximo_util_apos(res_prel_hetero)
            fim_rec_hetero = adicionar_dias_uteis(inicio_rec_hetero, 2)
            add("ABERTURA DE RECURSO CONTRA O RESULTADO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO",
                inicio_rec_hetero, fim_rec_hetero)
            analise_hetero = adicionar_dias_uteis(fim_rec_hetero, 2)
            add("ANÁLISE BANCA DOS RECURSOS DO PROCEDIMENTO HETEROIDENTIFICAÇÃO", analise_hetero)
            res_pos_hetero = proximo_util_apos(analise_hetero)
            add("RESULTADO PÓS-RECURSO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO", res_pos_hetero)
            ref_fase_anterior = res_pos_hetero

        # Classificação
        add("CLASSIFICAÇÃO PRELIMINAR", ref_fase_anterior)
        inicio_rec_class = proximo_util_apos(ref_fase_anterior)
        fim_rec_class = adicionar_dias_uteis(inicio_rec_class, 2)
        add("ABERTURA DE RECURSO CONTRA CLASSIFICAÇÃO PRELIMINAR", inicio_rec_class, fim_rec_class)
        analise_class = adicionar_dias_uteis(fim_rec_class, 2)
        add("ANÁLISE DOS RECURSOS CONTRA CLASSIFICAÇÃO PRELIMINAR", analise_class)
        class_final = proximo_util_apos(analise_class)
        add("CLASSIFICAÇÃO FINAL", class_final)
        add("HOMOLOGAÇÃO", class_final)

    return tarefas


# ─── MOTOR GUARDA ─────────────────────────────────────────────────────────────

def calcular_guarda(
    data_publicacao: date,
    tem_objetiva: bool = True,
    tem_inscricao: bool = True,
    tem_isencao: bool = True,
    tem_discursiva: bool = False,
    tem_pratica: bool = False,
    tem_taf: bool = False,
    tem_titulos: bool = False,
    tem_psicologica: bool = False,
    tem_medica: bool = False,
    tem_clinica: bool = False,
    tem_hetero: bool = False,
    tem_entrevista: bool = False,
    tem_competencias: bool = False,
    tem_sindicancia: bool = False,
    concomitancia_titulos_pratica: bool = False,
) -> list:
    tarefas = []
    seq = 1

    def add(atividade, inicio, fim=None):
        nonlocal seq
        tarefas.append({"seq": seq, "atividade": atividade,
                        "data_inicio": inicio, "data_fim": fim or inicio})
        seq += 1

    # 1. Publicação
    pub = proximo_util(data_publicacao)
    add("PUBLICAÇÃO DO EDITAL", pub)

    if tem_isencao:
        # Guarda: mesmo início que concurso — 60 dias corridos, 3 dias úteis
        inicio_isencao = proximo_util(pub + timedelta(days=60))
        fim_isencao = adicionar_dias_uteis(inicio_isencao, 2)
        add("PERÍODO SOLICITAÇÃO DE ISENÇÃO", inicio_isencao, fim_isencao)

    if tem_inscricao:
        inicio_insc = inicio_isencao if tem_isencao else proximo_util(pub + timedelta(days=60))
        fim_insc_raw = inicio_insc + timedelta(days=29)
        fim_insc = proximo_util(fim_insc_raw) if not is_util(fim_insc_raw) else fim_insc_raw
        add("PERÍODO DE INSCRIÇÕES/PCD/SOLICITAÇÃO COND. ESPECIAL/ENVIO LAUDOS", inicio_insc, fim_insc)

    if tem_isencao:
        res_prel_isencao = adicionar_dias_uteis(fim_isencao, 5)
        add("RESULTADO PRELIMINAR DA SOLICITAÇÃO DE ISENÇÃO", res_prel_isencao)
        inicio_rec_isencao = proximo_util_apos(res_prel_isencao)
        fim_rec_isencao = adicionar_dias_uteis(inicio_rec_isencao, 2)
        add("ABERTURA DE RECURSO CONTRA RESULTADO PRELIMINAR DA SOLICITAÇÃO DE ISENÇÃO",
            inicio_rec_isencao, fim_rec_isencao)
        # Guarda: análise = 1 dia útil
        analise_isencao = proximo_util_apos(fim_rec_isencao)
        add("ANÁLISE DA BANCA DOS RECURSOS CONTRA SOLICITAÇÃO DE ISENÇÃO", analise_isencao)
        # Guarda: resultado pós-recurso antes do fim das inscrições
        res_pos_isencao = proximo_util_apos(analise_isencao)
        add("RESULTADO PÓS-RECURSO DA SOLICITAÇÃO DE ISENÇÃO", res_pos_isencao)

    if tem_inscricao:
        boleto = proximo_util_apos(fim_insc)
        add("2ª VIA E PAGAMENTO DO BOLETO", boleto)
        res_prel_insc = adicionar_dias_uteis(fim_insc, 5)
        add("RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL", res_prel_insc)
        inicio_rec_insc = proximo_util_apos(res_prel_insc)
        fim_rec_insc = adicionar_dias_uteis(inicio_rec_insc, 2)
        add("ABERTURA DE RECURSO CONTRA RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL",
            inicio_rec_insc, fim_rec_insc)
        # Guarda: análise = 1 dia útil
        analise_insc = proximo_util_apos(fim_rec_insc)
        add("ANÁLISE DA BANCA DOS RECURSOS CONTRA RESULTADO PRELIMINAR INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL",
            analise_insc)
        # Guarda: resultado = 2º dia útil
        res_pos_insc = segundo_util_apos(analise_insc)
        add("RESULTADO PÓS-RECURSO INSCRIÇÕES/PCD/NEGROS/SOLIC CONDIÇÃO ESPECIAL", res_pos_insc)

        if tem_objetiva:
            # Guarda: prova ~30 dias corridos após fim inscrições, sempre domingo
            prova_obj_raw = fim_insc + timedelta(days=30)
            prova_obj = proximo_domingo(prova_obj_raw - timedelta(days=1))
            # CDI = 5 dias úteis antes da prova
            cdi = dias_uteis_antes(prova_obj, 5)
            add("COMPROVANTE DEFINITIVO DE INSCRIÇÃO (CDI) - PUBLICAÇÃO DO LOCAL DE PROVA", cdi)
            nome_prova = "PROVA OBJETIVA E PROVA DISCURSIVA" if tem_discursiva else "PROVA OBJETIVA"
            add(nome_prova, prova_obj)
            add("GABARITO PRELIMINAR", prova_obj)
            inicio_rec_q = proximo_util_apos(prova_obj)
            fim_rec_q = adicionar_dias_uteis(inicio_rec_q, 2)
            add("ABERTURA DE RECURSO CONTRA QUESTÕES PROVA OBJETIVA", inicio_rec_q, fim_rec_q)
            # Guarda: análise ~15 dias corridos
            analise_q = proximo_util_apos(fim_rec_q) 
            analise_q_fim = analise_q + timedelta(days=14)
            add("ANÁLISE DA BANCA DOS RECURSOS CONTRA QUESTÕES PROVA OBJETIVA", analise_q, analise_q_fim)
            gabarito_pos = proximo_util_apos(analise_q_fim)
            add("GABARITO PÓS-RECURSO", gabarito_pos)
            inicio_rec_gab = proximo_util_apos(gabarito_pos)
            fim_rec_gab = adicionar_dias_uteis(inicio_rec_gab, 2)
            add("ABERTURA DE RECURSO CONTRA GABARITO PÓS-RECURSO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES)",
                inicio_rec_gab, fim_rec_gab)
            # Guarda: análise gabarito = 3 dias úteis
            analise_gab = adicionar_dias_uteis(proximo_util_apos(fim_rec_gab), 2)
            add("ANÁLISE DOS RECURSOS CONTRA GABARITO PÓS-RECURSO", analise_gab)
            res_prel_total = proximo_util_apos(analise_gab)
            add("GABARITO PÓS-RECURSO - RETIFICADO (SE HOUVER ALTERAÇÃO/ANULAÇÃO DE QUESTÕES) E RESULTADO PRELIMINAR DA TOTALIZAÇÃO DA PROVA OBJETIVA",
                res_prel_total)
            if tem_discursiva:
                add("ENVIAR PROVAS DISCURSIVAS PARA CORREÇÃO", res_prel_total)
            inicio_rec_total = proximo_util_apos(res_prel_total)
            fim_rec_total = adicionar_dias_uteis(inicio_rec_total, 2)
            add("ABERTURA DE RECURSO CONTRA TOTALIZAÇÃO DA PROVA OBJETIVA", inicio_rec_total, fim_rec_total)
            # Guarda: análise totalização = 1 dia útil
            analise_total = proximo_util_apos(fim_rec_total)
            add("ANÁLISE BANCA DOS RECURSOS CONTRA TOTALIZAÇÃO DA PROVA OBJETIVA", analise_total)
            res_pos_total = proximo_util_apos(analise_total)
            if tem_discursiva:
                add("RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA E RESULTADO PRELIMINAR DA PROVA DISCURSIVA",
                    res_pos_total)
                inicio_rec_disc = proximo_util_apos(res_pos_total)
                fim_rec_disc = adicionar_dias_uteis(inicio_rec_disc, 2)
                add("ABERTURA DE RECURSO CONTRA O RESULTADO DA PROVA DISCURSIVA", inicio_rec_disc, fim_rec_disc)
                # Guarda: análise discursiva = 2 a 3 dias úteis
                analise_disc = adicionar_dias_uteis(proximo_util_apos(fim_rec_disc), 2)
                add("PERÍODO DE ANÁLISE DOS RECURSOS DA PROVA DISCURSIVA", analise_disc)
                res_pos_disc = proximo_util_apos(analise_disc)
                add("RESULTADO PÓS-RECURSO DA PROVA DISCURSIVA", res_pos_disc)
                ref_fase_anterior = res_pos_disc
            else:
                add("RESULTADO PÓS-RECURSO DA TOTALIZAÇÃO DA PROVA OBJETIVA", res_pos_total)
                ref_fase_anterior = res_pos_total
        else:
            ref_fase_anterior = res_pos_insc

        # Prova Prática / TAF — Guarda: convocação 5 dias úteis antes
        if tem_pratica or tem_taf:
            nome_pratica = "REALIZAÇÃO PROVA PRÁTICA" if tem_pratica else "REALIZAÇÃO DA PROVA DE CAPACIDADE FÍSICA"
            sabado_pratica = proximo_dia_semana(ref_fase_anterior, 5, semanas_depois=1)
            conv_pratica = dias_uteis_antes(sabado_pratica, 5)
            add(f"CONVOCAÇÃO PARA {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}", conv_pratica)
            domingo_pratica = sabado_pratica + timedelta(days=1)
            add(nome_pratica, sabado_pratica, domingo_pratica)
            res_prel_pratica = proximo_util(domingo_pratica + timedelta(days=7))
            add(f"RESULTADO PRELIMINAR {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}", res_prel_pratica)
            inicio_rec_pratica = proximo_util_apos(res_prel_pratica)
            fim_rec_pratica = adicionar_dias_uteis(inicio_rec_pratica, 2)
            add(f"ABERTURA DE RECURSO CONTRA O RESULTADO {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}",
                inicio_rec_pratica, fim_rec_pratica)
            # Guarda: análise = 2 a 3 dias úteis
            analise_pratica = adicionar_dias_uteis(proximo_util_apos(fim_rec_pratica), 2)
            add(f"PERÍODO DE ANÁLISE DOS RECURSOS DA {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}",
                analise_pratica)
            # Guarda: resultado = 2º dia útil
            res_pos_pratica = segundo_util_apos(analise_pratica)
            add(f"RESULTADO PÓS-RECURSO DA {'PROVA PRÁTICA' if tem_pratica else 'PROVA DE CAPACIDADE FÍSICA'}",
                res_pos_pratica)
            ref_fase_anterior = res_pos_pratica

        # Títulos — Guarda: convocação no mesmo dia do resultado pós-recurso anterior
        if tem_titulos:
            ref_titulos = (res_pos_disc if tem_discursiva else res_pos_total) if concomitancia_titulos_pratica and (tem_pratica or tem_taf) and tem_objetiva else ref_fase_anterior
            add("CONVOCAÇÃO PARA PROVA DE TÍTULOS", ref_titulos)
            inicio_titulos = proximo_util_apos(ref_titulos)
            fim_titulos = adicionar_dias_uteis(inicio_titulos, 2)
            add("PERÍODO PARA ENVIO DOS TÍTULOS", inicio_titulos, fim_titulos)
            analise_titulos = adicionar_dias_uteis(fim_titulos, 5)
            add("PERÍODO PARA ANÁLISE DOS TÍTULOS", analise_titulos)
            res_prel_titulos = proximo_util_apos(analise_titulos)
            add("RESULTADO PRELIMINAR PROVA DE TÍTULOS", res_prel_titulos)
            inicio_rec_titulos = proximo_util_apos(res_prel_titulos)
            fim_rec_titulos = adicionar_dias_uteis(inicio_rec_titulos, 2)
            add("ABERTURA DE RECURSO CONTRA O RESULTADO PROVA DE TÍTULOS", inicio_rec_titulos, fim_rec_titulos)
            # Guarda: análise = 1 dia útil
            analise_rec_titulos = proximo_util_apos(fim_rec_titulos)
            add("ANÁLISE BANCA DOS RECURSOS CONTRA PROVA DE TÍTULOS", analise_rec_titulos)
            # Guarda: resultado = 2º dia útil
            res_pos_titulos = segundo_util_apos(analise_rec_titulos)
            add("RESULTADO PÓS-RECURSO DA PROVA DE TÍTULOS", res_pos_titulos)
            ref_fase_anterior = res_pos_titulos

        # Sindicância Social — exclusiva da Guarda
        if tem_sindicancia:
            add("CONVOCAÇÃO PARA A ENTREGA DA DOCUMENTAÇÃO PARA SINDICÂNCIA SOCIAL", ref_fase_anterior)
            inicio_entrega = proximo_util_apos(ref_fase_anterior)
            fim_entrega = adicionar_dias_uteis(inicio_entrega, 2)
            add("PERÍODO DE ENTREGA DA DOCUMENTAÇÃO PARA SINDICÂNCIA SOCIAL", inicio_entrega, fim_entrega)
            # Guarda: análise = ~30 dias corridos
            fim_analise_sind = proximo_util(fim_entrega + timedelta(days=30))
            add("ANÁLISE PELA COMISSÃO DA DOCUMENTAÇÃO DE SINDICÂNCIA SOCIAL", proximo_util_apos(fim_entrega), fim_analise_sind)
            res_prel_sind = proximo_util_apos(fim_analise_sind)
            add("RESULTADO PRELIMINAR DA SINDICÂNCIA SOCIAL", res_prel_sind)
            inicio_rec_sind = proximo_util_apos(res_prel_sind)
            fim_rec_sind = adicionar_dias_uteis(inicio_rec_sind, 2)
            add("ABERTURA DE RECURSOS CONTRA RESULTADO DA SINDICÂNCIA SOCIAL", inicio_rec_sind, fim_rec_sind)
            analise_sind = adicionar_dias_uteis(proximo_util_apos(fim_rec_sind), 2)
            add("ANÁLISE BANCA DOS RECURSOS CONTRA SINDICÂNCIA SOCIAL", analise_sind)
            res_pos_sind = proximo_util_apos(analise_sind)
            add("RESULTADO PÓS-RECURSO CONTRA SINDICÂNCIA SOCIAL", res_pos_sind)
            ref_fase_anterior = res_pos_sind

        # Avaliação Psicológica — Guarda: convocação 5 dias úteis antes
        if tem_psicologica:
            sabado_psico = proximo_dia_semana(ref_fase_anterior, 5, semanas_depois=1)
            conv_psico = dias_uteis_antes(sabado_psico, 5)
            add("CONVOCAÇÃO PARA AVALIAÇÃO PSICOLÓGICA", conv_psico)
            domingo_psico = sabado_psico + timedelta(days=1)
            add("REALIZAÇÃO DA AVALIAÇÃO PSICOLÓGICA", sabado_psico, domingo_psico)
            correcao_psico = adicionar_dias_uteis(domingo_psico, 3)
            add("CORREÇÃO DOS TESTES DA AVALIAÇÃO PSICOLÓGICA", correcao_psico)
            res_prel_psico = proximo_util_apos(correcao_psico)
            add("RESULTADO PRELIMINAR DA AVALIAÇÃO PSICOLÓGICA", res_prel_psico)
            if tem_entrevista:
                manifestacao = adicionar_dias_uteis(res_prel_psico, 1)
                add("MANIFESTAÇÃO DE INTERESSE DE RECEBER ENTREVISTA DEVOLUTIVA", manifestacao)
                entrevista_d = proximo_util_apos(manifestacao)
                add("REALIZAÇÃO DA ENTREVISTA DEVOLUTIVA", entrevista_d)
                inicio_rec_psico = adicionar_dias_uteis(entrevista_d, 3)
            else:
                inicio_rec_psico = proximo_util_apos(res_prel_psico)
            fim_rec_psico = adicionar_dias_uteis(inicio_rec_psico, 2)
            add("ABERTURA DE RECURSOS CONTRA AVALIAÇÃO PSICOLÓGICA", inicio_rec_psico, fim_rec_psico)
            # Guarda: análise = 2 a 3 dias úteis
            analise_psico = adicionar_dias_uteis(proximo_util_apos(fim_rec_psico), 2)
            add("ANÁLISE BANCA DOS RECURSOS DA AVALIAÇÃO PSICOLÓGICA", analise_psico)
            res_pos_psico = proximo_util_apos(analise_psico)
            add("RESULTADO PÓS-RECURSO DA AVALIAÇÃO PSICOLÓGICA", res_pos_psico)
            ref_fase_anterior = res_pos_psico

        # Entrevista por Competências
        if tem_competencias:
            conv_comp = proxima_terca(ref_fase_anterior)
            add("CONVOCAÇÃO PARA ENTREVISTA POR COMPETÊNCIAS", conv_comp)
            sabado_comp = proximo_dia_semana(conv_comp, 5)
            domingo_comp = sabado_comp + timedelta(days=1)
            add("REALIZAÇÃO ENTREVISTA POR COMPETÊNCIAS", sabado_comp, domingo_comp)
            res_prel_comp = adicionar_dias_uteis(domingo_comp, 2)
            add("RESULTADO PRELIMINAR DA ENTREVISTA POR COMPETÊNCIAS", res_prel_comp)
            inicio_rec_comp = proximo_util_apos(res_prel_comp)
            fim_rec_comp = adicionar_dias_uteis(inicio_rec_comp, 2)
            add("ABERTURA DE RECURSO CONTRA A ENTREVISTA POR COMPETÊNCIAS", inicio_rec_comp, fim_rec_comp)
            analise_comp = adicionar_dias_uteis(proximo_util_apos(fim_rec_comp), 2)
            add("ANÁLISE BANCA DOS RECURSOS DA ENTREVISTA POR COMPETÊNCIAS", analise_comp)
            res_pos_comp = proximo_util_apos(analise_comp)
            add("RESULTADO PÓS-RECURSO DA ENTREVISTA POR COMPETÊNCIAS", res_pos_comp)
            ref_fase_anterior = res_pos_comp

        # Avaliação Médica — Guarda: convocação 5 dias úteis antes
        if tem_medica:
            sabado_med = proximo_dia_semana(ref_fase_anterior, 5, semanas_depois=1)
            conv_med = dias_uteis_antes(sabado_med, 5)
            add("CONVOCAÇÃO PARA AVALIAÇÃO MÉDICA", conv_med)
            domingo_med = sabado_med + timedelta(days=1)
            add("REALIZAÇÃO DA AVALIAÇÃO MÉDICA", sabado_med, domingo_med)
            res_prel_med = adicionar_dias_uteis(domingo_med, 3)
            add("RESULTADO PRELIMINAR DA AVALIAÇÃO MÉDICA", res_prel_med)
            inicio_rec_med = proximo_util_apos(res_prel_med)
            fim_rec_med = adicionar_dias_uteis(inicio_rec_med, 2)
            add("ABERTURA DE RECURSOS CONTRA AVALIAÇÃO MÉDICA", inicio_rec_med, fim_rec_med)
            analise_med = adicionar_dias_uteis(proximo_util_apos(fim_rec_med), 2)
            add("ANÁLISE DA BANCA DOS RECURSOS CONTRA AVALIAÇÃO MÉDICA", analise_med)
            res_pos_med = proximo_util_apos(analise_med)
            add("RESULTADO PÓS-RECURSO DA AVALIAÇÃO MÉDICA", res_pos_med)
            ref_fase_anterior = res_pos_med

        # Heteroidentificação
        if tem_hetero:
            conv_hetero = proximo_util_apos(ref_fase_anterior)
            add("CONVOCAÇÃO PROCEDIMENTO HETEROIDENTIFICAÇÃO", conv_hetero)
            inicio_foto = proximo_util_apos(conv_hetero)
            fim_foto = adicionar_dias_uteis(inicio_foto, 2)
            add("ENVIO FOTO/VÍDEO PARA PROCEDIMENTO HETEROIDENTIFICAÇÃO", inicio_foto, fim_foto)
            inicio_av_hetero = proximo_util_apos(fim_foto)
            fim_av_hetero = adicionar_dias_uteis(inicio_av_hetero, 2)
            add("PROCEDIMENTO HETEROIDENTIFICAÇÃO - AVALIAÇÃO DA BANCA", inicio_av_hetero, fim_av_hetero)
            res_prel_hetero = proximo_util_apos(fim_av_hetero)
            add("RESULTADO PRELIMINAR DO PROCEDIMENTO HETEROIDENTIFICAÇÃO", res_prel_hetero)
            inicio_rec_hetero = proximo_util_apos(res_prel_hetero)
            fim_rec_hetero = adicionar_dias_uteis(inicio_rec_hetero, 2)
            add("ABERTURA DE RECURSO CONTRA O RESULTADO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO",
                inicio_rec_hetero, fim_rec_hetero)
            analise_hetero = adicionar_dias_uteis(proximo_util_apos(fim_rec_hetero), 1)
            add("ANÁLISE BANCA DOS RECURSOS DO PROCEDIMENTO HETEROIDENTIFICAÇÃO", analise_hetero)
            res_pos_hetero = proximo_util_apos(analise_hetero)
            add("RESULTADO PÓS-RECURSO DO PROCEDIMENTO HETEROIDENTIFICAÇÃO", res_pos_hetero)
            ref_fase_anterior = res_pos_hetero

        # Classificação
        add("CLASSIFICAÇÃO PRELIMINAR", ref_fase_anterior)
        inicio_rec_class = proximo_util_apos(ref_fase_anterior)
        fim_rec_class = adicionar_dias_uteis(inicio_rec_class, 2)
        add("ABERTURA DE RECURSO CONTRA CLASSIFICAÇÃO PRELIMINAR", inicio_rec_class, fim_rec_class)
        analise_class = adicionar_dias_uteis(fim_rec_class, 2)
        add("ANÁLISE DOS RECURSOS CONTRA CLASSIFICAÇÃO PRELIMINAR", analise_class)
        class_final = proximo_util_apos(analise_class)
        add("CLASSIFICAÇÃO FINAL", class_final)
        add("HOMOLOGAÇÃO", class_final)

    return tarefas


# ─── FUNÇÃO PÚBLICA ───────────────────────────────────────────────────────────

def calcular_cronograma(tipo_certame: str = "CONCURSO/PSP", **kwargs) -> list:
    """
    Calcula cronograma baseado no tipo de certame.
    tipo_certame: 'CONCURSO/PSP' ou 'GUARDA'
    """
    if tipo_certame == "GUARDA":
        return calcular_guarda(**kwargs)
    else:
        kwargs.pop("tem_sindicancia", None)
        return calcular_concurso_psp(**kwargs)


# ─── RECÁLCULO EM CASCATA ────────────────────────────────────────────────────

def recalcular_a_partir(
    cronograma_original: list,
    seq_conflito: int,
    nova_data_fim: date,
    tipo_certame: str = "CONCURSO/PSP",
    **kwargs_motor
) -> list:
    """
    Recalcula o cronograma a partir da tarefa com conflito,
    mantendo as tarefas anteriores intactas e recalculando
    toda a cadeia seguinte respeitando as regras.
    """
    # Separa tarefas antes e a partir do conflito
    antes = [t for t in cronograma_original if t["seq"] < seq_conflito]
    conflito_row = next(t for t in cronograma_original if t["seq"] == seq_conflito)

    # Calcula o deslocamento em dias
    deslocamento = nova_data_fim - conflito_row["data_fim"]

    # Recalcula cronograma completo com nova data de publicação ajustada
    # Estratégia: desloca a data de publicação pelo mesmo offset
    data_pub_original = cronograma_original[0]["data_fim"]
    nova_data_pub = data_pub_original + deslocamento

    # Gera novo cronograma completo
    novo_cron = calcular_cronograma(tipo_certame=tipo_certame, data_publicacao=nova_data_pub, **kwargs_motor)

    # Mantém as datas anteriores ao conflito do cronograma original
    # e usa as novas datas a partir do conflito
    resultado = []
    for t_orig in antes:
        resultado.append(t_orig)

    # Para as tarefas a partir do conflito, usa o novo cronograma
    # alinhando pela posição na sequência
    offset_seq = seq_conflito - 1
    for t_novo in novo_cron:
        seq_correspondente = t_novo["seq"] + offset_seq
        if seq_correspondente >= seq_conflito:
            resultado.append({
                "seq": seq_correspondente,
                "atividade": t_novo["atividade"],
                "data_inicio": t_novo["data_inicio"],
                "data_fim": t_novo["data_fim"],
            })

    return resultado


def encontrar_primeira_data_livre(
    data_base: date,
    datas_ocupadas: set,
    tipo_certame: str = "CONCURSO/PSP",
    nome_atividade: str = "",
) -> date:
    """
    Encontra a próxima data válida para uma atividade,
    respeitando regras de dia útil, recesso e conflitos.
    Algumas atividades têm restrições de dia da semana.
    """
    candidata = data_base + timedelta(days=1)
    tentativas = 0

    # Verifica se a atividade tem restrição de dia da semana
    nome_upper = nome_atividade.upper()
    requer_domingo = any(k in nome_upper for k in ["PROVA OBJETIVA", "PROVA DISCURSIVA", "REALIZAÇÃO DA AVALIAÇÃO", "REALIZAÇÃO PROVA"])
    requer_terca = any(k in nome_upper for k in ["CONVOCAÇÃO PARA", "CDI", "COMPROVANTE DEFINITIVO"])

    while tentativas < 30:
        if requer_domingo:
            # Avança até o próximo domingo
            while candidata.weekday() != 6:
                candidata += timedelta(days=1)
        elif requer_terca:
            # Avança até a próxima terça útil
            while not (candidata.weekday() == 1 and is_util(candidata)):
                candidata += timedelta(days=1)
        else:
            if not is_util(candidata):
                candidata = proximo_util(candidata)

        if candidata not in datas_ocupadas:
            return candidata

        candidata += timedelta(days=1)
        tentativas += 1

    return candidata
