import pandas as pd
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

STATUS_ATIVOS = {'pago', 'deferida'}

def thin():
    return Border(
        top=__import__('openpyxl.styles',fromlist=['Side']).Side(border_style='thin'),
        bottom=__import__('openpyxl.styles',fromlist=['Side']).Side(border_style='thin'),
        left=__import__('openpyxl.styles',fromlist=['Side']).Side(border_style='thin'),
        right=__import__('openpyxl.styles',fromlist=['Side']).Side(border_style='thin'),
    )

def processar(arquivo_bytes, conjuntos_mesma_prova=None):
    """
    conjuntos_mesma_prova: lista de listas de códigos de cargo
        ex: [['314','315'], ['310','311']]
    Retorna: (df_resultado, df_alocacao, resumo)
    """
    # Ler arquivo — header na linha 2 (index 1)
    df = pd.read_excel(io.BytesIO(arquivo_bytes), header=1, dtype=str)
    df.columns = [c.strip() for c in df.columns]

    # Normalizar campos chave
    df['CPF']    = df['CPF'].str.strip().str.replace(r'\D','',regex=True)
    df['CÓDIGO'] = df['CÓDIGO'].str.strip()
    df['STATUS'] = df['STATUS'].str.strip()

    # Converter DATA INSCRIÇÃO para datetime
    def parse_dt(v):
        if pd.isna(v): return pd.NaT
        try:
            f = float(v)
            from datetime import datetime, timedelta
            return datetime(1899,12,30) + timedelta(days=f)
        except:
            return pd.to_datetime(v, errors='coerce')

    df['_DT'] = df['DATA INSCRIÇÃO'].apply(parse_dt)

    # Coluna de status normalizado para comparação
    df['_STATUS_NORM'] = df['STATUS'].str.lower().str.strip()

    # Índice original para manter ordem
    df = df.reset_index(drop=True)
    cancelar_idx = set()

    def cancelar_duplicatas(grupo):
        """
        Dentro de um grupo (mesmo CPF + mesmo conjunto de cargos),
        entre os Pagos/Deferidos, mantém o mais recente e cancela os demais.
        """
        ativos = grupo[grupo['_STATUS_NORM'].isin(STATUS_ATIVOS)].copy()
        if len(ativos) <= 1:
            return
        # Ordenar por data — mais recente por último
        ativos = ativos.sort_values('_DT', ascending=True, na_position='first')
        # Cancelar todos menos o último (mais recente)
        cancelar_idx.update(ativos.index[:-1].tolist())

    # ── REGRA 1: duplicata no mesmo cargo ─────────────────────────────
    for (cpf, cod), grp in df.groupby(['CPF','CÓDIGO'], dropna=False):
        cancelar_duplicatas(grp)

    # ── REGRA 2: conjuntos de cargos com mesma prova ──────────────────
    if conjuntos_mesma_prova:
        for conjunto in conjuntos_mesma_prova:
            conjunto_norm = [str(c).strip() for c in conjunto]
            mask = df['CÓDIGO'].isin(conjunto_norm)
            sub = df[mask]
            for cpf, grp in sub.groupby('CPF', dropna=False):
                cancelar_duplicatas(grp)

    # Aplicar cancelamentos
    df.loc[list(cancelar_idx), 'STATUS'] = 'Cancelada'
    df['_STATUS_NORM'] = df['STATUS'].str.lower().str.strip()

    # ── PLANILHA DE RESULTADO: todos os candidatos ────────────────────
    colunas_result = [c for c in df.columns if not c.startswith('_')]
    df_resultado = df[colunas_result].copy()

    # ── PLANILHA DE ALOCAÇÃO: somente Pagos e Deferidos ───────────────
    df_aloc = df[df['_STATUS_NORM'].isin(STATUS_ATIVOS)].copy()

    # Para conjuntos de mesma prova: garantir que candidato aparece só uma vez
    # (já foi garantido pelo cancelamento, mas fazemos double-check)
    df_alocacao = df_aloc[colunas_result].copy()

    # Resumo
    resumo = {
        'total': len(df),
        'pagos': (df['_STATUS_NORM']=='pago').sum(),
        'deferidos': (df['_STATUS_NORM']=='deferida').sum(),
        'pendentes': (df['_STATUS_NORM']=='pendente').sum(),
        'indeferidos': (df['_STATUS_NORM']=='indeferida').sum(),
        'cancelados': (df['_STATUS_NORM']=='cancelada').sum(),
        'total_alocacao': len(df_alocacao),
    }

    return df_resultado, df_alocacao, resumo


def df_para_xlsx(df, titulo):
    """Gera bytes de xlsx formatado"""
    from openpyxl.styles import Side
    def borda():
        s = Side(border_style='thin', color='000000')
        return Border(top=s, bottom=s, left=s, right=s)

    wb = Workbook()
    ws = wb.active
    ws.title = titulo[:31]

    # Cabeçalho
    CORES_STATUS = {
        'Pago':       'C6EFCE',  # verde
        'Deferida':   'C6EFCE',  # verde
        'Pendente':   'FFEB9C',  # amarelo
        'Indeferida': 'FFC7CE',  # vermelho claro
        'Cancelada':  'D9D9D9',  # cinza
    }

    cols = list(df.columns)
    for ci, col in enumerate(cols, 1):
        c = ws.cell(row=1, column=ci, value=col)
        c.font = Font(bold=True, name='Calibri', size=10, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='1F4E8C')
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.border = borda()
        ws.column_dimensions[get_column_letter(ci)].width = max(12, min(len(col)*1.2, 40))
    ws.row_dimensions[1].height = 30

    # Status col index
    try: status_ci = cols.index('STATUS') + 1
    except: status_ci = None

    for ri, row in enumerate(df.itertuples(index=False), 2):
        for ci, val in enumerate(row, 1):
            c = ws.cell(row=ri, column=ci, value=str(val) if val is not None else '')
            c.font = Font(name='Calibri', size=9)
            c.alignment = Alignment(vertical='center')
            c.border = borda()
        # Cor por status
        if status_ci:
            status_val = str(row[status_ci-1]).strip()
            cor = CORES_STATUS.get(status_val)
            if cor:
                for ci in range(1, len(cols)+1):
                    ws.cell(row=ri, column=ci).fill = PatternFill('solid', fgColor=cor)

    # Filtro automático
    ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(df)+1}"
    ws.freeze_panes = 'A2'

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
