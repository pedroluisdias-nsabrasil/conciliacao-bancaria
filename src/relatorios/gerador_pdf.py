"""
src/relatorios/gerador_pdf.py - PARTE 1: Estrutura Base

Gera relatórios profissionais em PDF com reportlab e matplotlib.
"""

from decimal import Decimal
from datetime import date, datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
)
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # Backend sem interface gráfica

logger = logging.getLogger(__name__)


class GeradorPDF:
    """
    Gera relatórios PDF profissionais para conciliação bancária.

    Características:
    - Layout profissional A4
    - Gráficos matplotlib (pizza, barras)
    - Tabelas formatadas
    - Quebras de página automáticas
    - Cabeçalho e rodapé
    - Cores semânticas
    """

    def __init__(self):
        """Inicializa o gerador."""
        self.styles = getSampleStyleSheet()
        self._configurar_estilos()

    def _configurar_estilos(self) -> None:
        """Configura estilos customizados."""
        # Título principal
        self.styles.add(
            ParagraphStyle(
                name="TituloPrincipal",
                parent=self.styles["Heading1"],
                fontSize=20,
                textColor=colors.HexColor("#4472C4"),
                spaceAfter=30,
                alignment=1,  # Center
            )
        )

        # Subtítulo
        self.styles.add(
            ParagraphStyle(
                name="Subtitulo",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#4472C4"),
                spaceBefore=20,
                spaceAfter=10,
            )
        )

    def gerar(
        self,
        matches: List,
        lancamentos_nao_conciliados: List,
        estatisticas: Dict,
        arquivo_saida: str,
    ) -> str:
        """
        Gera relatório PDF completo.

        Args:
            matches: Lista de Match objects
            lancamentos_nao_conciliados: Lista de Lancamento não conciliados
            estatisticas: Dict com estatísticas da conciliação
            arquivo_saida: Caminho do arquivo de saída

        Returns:
            Caminho do arquivo gerado

        Example:
            >>> gerador = GeradorPDF()
            >>> arquivo = gerador.gerar(
            ...     matches=matches,
            ...     lancamentos_nao_conciliados=nao_conc,
            ...     estatisticas=stats,
            ...     arquivo_saida="relatorio.pdf"
            ... )
        """
        try:
            # Garantir diretório existe
            Path(arquivo_saida).parent.mkdir(parents=True, exist_ok=True)

            # Criar documento
            doc = SimpleDocTemplate(
                arquivo_saida,
                pagesize=A4,
                rightMargin=2.5 * cm,
                leftMargin=2.5 * cm,
                topMargin=2.5 * cm,
                bottomMargin=2.5 * cm,
            )

            # Elementos do relatório
            elementos = []

            # 1. Cabeçalho
            elementos.extend(self._criar_cabecalho())

            # 2. Resumo executivo
            elementos.extend(self._criar_resumo(estatisticas))
            elementos.append(Spacer(1, 0.5 * cm))

            # 3. Gráficos
            elementos.extend(self._criar_graficos(estatisticas, matches))
            elementos.append(PageBreak())

            # 4. Tabela de matches
            if matches:
                elementos.extend(self._criar_secao_matches(matches))
                elementos.append(Spacer(1, 1 * cm))

            # 5. Tabela de não conciliados
            if lancamentos_nao_conciliados:
                elementos.extend(
                    self._criar_secao_nao_conciliados(lancamentos_nao_conciliados)
                )

            # Gerar PDF
            doc.build(elementos)

            logger.info(f"Relatório PDF gerado: {arquivo_saida}")
            return arquivo_saida

        except Exception as e:
            logger.error(f"Erro ao gerar PDF: {e}")
            raise

    def _criar_cabecalho(self) -> List:
        """Cria cabeçalho do relatório."""
        elementos = []

        # Título
        titulo = Paragraph(
            "Relatório de Conciliação Bancária", self.styles["TituloPrincipal"]
        )
        elementos.append(titulo)

        # Data
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        data_para = Paragraph(f"<i>Gerado em: {data_atual}</i>", self.styles["Normal"])
        elementos.append(data_para)
        elementos.append(Spacer(1, 1 * cm))

        return elementos

    def _criar_resumo(self, stats: Dict) -> List:
        """Cria resumo executivo com KPIs."""
        elementos = []

        # Título da seção
        titulo = Paragraph("Resumo Executivo", self.styles["Subtitulo"])
        elementos.append(titulo)

        # Tabela de KPIs
        dados = [
            ["Métrica", "Valor"],
            ["Total de Lançamentos", str(stats.get("total_lancamentos", 0))],
            ["Auto-aprovados", str(stats.get("auto_aprovados", 0))],
            ["Para Revisar", str(stats.get("revisar", 0))],
            ["Não Conciliados", str(stats.get("nao_conciliados", 0))],
            ["Taxa de Conciliação", f"{stats.get('taxa_conciliacao', 0):.1f}%"],
            ["Tempo de Execução", f"{stats.get('tempo_execucao', 0):.2f}s"],
        ]

        tabela = Table(dados, colWidths=[10 * cm, 5 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    # Header
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    # Body
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [colors.white, colors.lightgrey],
                    ),
                ]
            )
        )

        elementos.append(tabela)

        return elementos

    def _criar_graficos(self, stats: Dict, matches: List) -> List:
        """Cria gráficos matplotlib."""
        elementos = []

        # Gráfico de pizza
        try:
            img_pizza = self._gerar_grafico_pizza(stats)
            elementos.append(Spacer(1, 0.5 * cm))
            elementos.append(img_pizza)
        except Exception as e:
            logger.warning(f"Erro ao gerar gráfico de pizza: {e}")

        return elementos

    def _gerar_grafico_pizza(self, stats: Dict) -> Image:
        """Gera gráfico de pizza da taxa de conciliação."""
        fig, ax = plt.subplots(figsize=(8, 6))

        # Dados
        labels = ["Auto-aprovados", "Para Revisar", "Não Conciliados"]
        sizes = [
            stats.get("auto_aprovados", 0),
            stats.get("revisar", 0),
            stats.get("nao_conciliados", 0),
        ]
        colors_pizza = ["#92D050", "#FFC000", "#FF0000"]
        explode = (0.1, 0, 0)  # Destacar auto-aprovados

        # Criar gráfico
        ax.pie(
            sizes,
            explode=explode,
            labels=labels,
            colors=colors_pizza,
            autopct="%1.1f%%",
            shadow=True,
            startangle=90,
        )
        ax.axis("equal")
        plt.title("Distribuição por Status", fontsize=14, fontweight="bold")

        # Salvar em memória
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        img_buffer.seek(0)

        # Converter para Image reportlab
        img = Image(img_buffer, width=12 * cm, height=9 * cm)

        return img

    def _criar_secao_matches(self, matches: List) -> List:
        """Cria seção de matches conciliados."""
        elementos = []

        # Título
        titulo = Paragraph("Lançamentos Conciliados", self.styles["Subtitulo"])
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.3 * cm))

        # Limitar quantidade (max 50 linhas)
        max_linhas = 50
        matches_mostrar = matches[:max_linhas]

        # Cabeçalho
        dados = [["Data", "Valor", "Descrição", "Confiança"]]

        # Adicionar matches
        for match in matches_mostrar:
            lanc = match.lancamento
            conf_pct = match.confianca * 100

            # Cor baseada na confiança
            if match.confianca >= 0.90:
                cor = colors.HexColor("#92D050")  # Verde
            elif match.confianca >= 0.60:
                cor = colors.HexColor("#FFC000")  # Amarelo
            else:
                cor = colors.HexColor("#FF0000")  # Vermelho

            dados.append(
                [
                    lanc.data.strftime("%d/%m/%Y"),
                    f"R$ {lanc.valor:,.2f}",
                    lanc.descricao[:40],
                    f"{conf_pct:.0f}%",
                ]
            )

        # Criar tabela
        tabela = Table(dados, colWidths=[2.5 * cm, 3 * cm, 8 * cm, 2.5 * cm])

        # Estilo base
        estilo = [
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            # Body
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]

        tabela.setStyle(TableStyle(estilo))
        elementos.append(tabela)

        # Nota se limitou
        if len(matches) > max_linhas:
            nota = Paragraph(
                f"<i>Mostrando {max_linhas} de {len(matches)} matches. "
                f"Veja o relatório Excel completo.</i>",
                self.styles["Normal"],
            )
            elementos.append(Spacer(1, 0.3 * cm))
            elementos.append(nota)

        return elementos

    def _criar_secao_nao_conciliados(self, lancamentos: List) -> List:
        """Cria seção de lançamentos não conciliados."""
        elementos = []

        # Título
        titulo = Paragraph("Lançamentos Não Conciliados", self.styles["Subtitulo"])
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.3 * cm))

        # Limitar
        max_linhas = 50
        lanc_mostrar = lancamentos[:max_linhas]

        # Cabeçalho
        dados = [["Data", "Valor", "Descrição"]]

        # Adicionar lançamentos
        for lanc in lanc_mostrar:
            dados.append(
                [
                    lanc.data.strftime("%d/%m/%Y"),
                    f"R$ {lanc.valor:,.2f}",
                    lanc.descricao[:50],
                ]
            )

        # Criar tabela
        tabela = Table(dados, colWidths=[3 * cm, 3 * cm, 10 * cm])
        tabela.setStyle(
            TableStyle(
                [
                    # Header
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    # Body - FUNDO VERMELHO
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#FFC7CE")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )

        elementos.append(tabela)

        # Nota
        if len(lancamentos) > max_linhas:
            nota = Paragraph(
                f"<i>Mostrando {max_linhas} de {len(lancamentos)} lançamentos não conciliados.</i>",
                self.styles["Normal"],
            )
            elementos.append(Spacer(1, 0.3 * cm))
            elementos.append(nota)

        return elementos
