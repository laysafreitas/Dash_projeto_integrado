import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output

df = pd.read_csv(r"C:/Users/Aluno/Documents/Trending_Movies_2026 (1).csv")

df['release_date'] = pd.to_datetime(df['release_date'])

categorias = ['Todas'] + sorted(df['original_language'].dropna().unique().tolist())

for coluna in ["vote_count", "vote_average", "popularity"]:
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

meses_labels = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]

ESTILO_CARD = {
    'border': '1px solid #dee2e6',
    'borderRadius': '8px',
    'padding': '12px',
    'backgroundColor': 'white',
    'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
}

ESTILO_KPI = {
    **ESTILO_CARD,
    'textAlign': 'center',
    'padding': '16px'
}

def kpi(titulo, id):
    return html.Div([
        html.P(titulo, style={'margin': 0, 'color': '#666', 'fontSize': '14px'}),
        html.H2(id=id, style={'margin': '4px 0 0 0', 'color': '#0b7285'})
    ], style=ESTILO_KPI)
    

app = Dash(__name__)

app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'margin': '20px', 'backgroundColor': '#f8f9fa', 'padding': '20px'},
    children=[
        html.H1("Dashboard de Filmes - Projeto Integrado", style={'textAlign': 'center', 'color': '#0b7285'}),
        html.P("Visualização consolidada de todos os gráficos em uma única página com filtros dinâmicos.",
               style={'textAlign': 'center', 'color': '#555', 'marginBottom': '20px'}),

        html.Div([
            html.Label("Filtrar por Categoria de idioma:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            
            dcc.Dropdown(
                id='filtro-categoria',   
                options=categorias,        
                value='Todas',             
                clearable=False,        
                style={'width': '300px'}  
            )
        ], style={'marginBottom': '20px'}),

        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gap': '16px', 'marginBottom': '20px'},
            children=[
                kpi("Total de popularidade", 'kpi-total'),    
                kpi("Nº de votos", 'kpi-votos'),    
                kpi("Media de votos", 'kpi-media'),      
            ]
        ),

        html.Div(
            style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '16px'},
            children=[
                html.Div(dcc.Graph(id='fig_dispersao'), style=ESTILO_CARD),    # ID do Gráfico de Linha
                html.Div(dcc.Graph(id='fig_barra_votecount'), style=ESTILO_CARD),    # ID do Gráfico de Barras
                html.Div(dcc.Graph(id='fig_barra_voteAvarege'),  style=ESTILO_CARD),    # ID do Gráfico de Área
                html.Div(dcc.Graph(id='fig_linha'),   style=ESTILO_CARD),    # ID do Boxplot
                html.Div(dcc.Graph(id='fig_histograma'), style=ESTILO_CARD),
                html.Div(dcc.Graph(id='fig_box'), style=ESTILO_CARD),
                html.Div(dcc.Graph(id='fig_heatmap'), style=ESTILO_CARD),
                html.Div(dcc.Graph(id='fig_linha_popu'), style=ESTILO_CARD)
            ]
        )
    ]
)

@app.callback(
    [
        # Saídas para os 3 Cartões de KPI (atualizam o texto interno 'children'):
        Output('kpi-total', 'children'),
        Output('kpi-votos', 'children'),
        Output('kpi-media', 'children'),
        
        # Saídas para os 6 Gráficos (atualizam o objeto gráfico 'figure'):
        Output('fig_dispersao', 'figure'),
        Output('fig_barra_votecount', 'figure'),
        Output('fig_barra_voteAvarege', 'figure'),
        Output('fig_linha', 'figure'),
        Output('fig_histograma', 'figure'),
        Output('fig_box', 'figure'),
        Output('fig_heatmap', 'figure'),
        Output('fig_linha_popu', 'figure')
    ],
    # Entrada: Captura a escolha selecionada no Dropdown
    [Input('filtro-categoria', 'value')]
)

# Função chamada dinamicamente pelo Dash. Recebe a categoria escolhida no filtro, processa o fatiamento (slice) dos dados e recria todos os KPIs e figuras Plotly.
def atualizar_dashboard(categoria):

  if categoria == "Todas":
    dff = df.copy()
  else:
     dff = df[df["original_language"] == categoria].copy()

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

  total_votos = dff["vote_count"].sum()
  quantidade_filmes = len(dff)
  media_popularidade = dff["popularity"].mean()

  if pd.isna(media_popularidade):
    media_popularidade = 0

    # --------------------------------------------------------
    # GRÁFICO 1: DISPERSÃO
    # Avaliação x popularidade
    # --------------------------------------------------------

  dados_dispersao = dff.dropna(
    subset=["vote_average", "popularity"]
    )

  dados_dispersao = dados_dispersao[
    (dados_dispersao["popularity"] > 0)
    ]

  fig_dispersao = px.scatter(
    dados_dispersao,
    x="vote_average",
    y="popularity",
    color="original_language",
    size="popularity",
    title="Dispersão: avaliação versus popularidade",
    labels={
        "vote_average": "Avaliação média",
        "popularity": "Popularidade",
        "original_language": "Idioma original"
    }
  )

    # --------------------------------------------------------
    # GRÁFICO 2: MAIOR NÚMERO DE VOTOS POR IDIOMA
    # --------------------------------------------------------

  dados_votos = (
        dff.dropna(subset=["original_language", "vote_count"])
        .groupby("original_language", as_index=False)["vote_count"]
        .max()
        .sort_values("vote_count", ascending=False)
    )

  fig_barra_votecount = px.bar(
     dados_votos,
     x="original_language",
     y="vote_count",
     color_discrete_sequence=["lightskyblue"],
     title="Maior número de votos por idioma",
     labels={
        "original_language": "Idioma original",
        "vote_count": "Número máximo de votos"
        }
    )

  fig_barra_votecount.update_traces(
    marker_line_color="#2C3E50",
    marker_line_width=1.5
    )

    # --------------------------------------------------------
    # GRÁFICO 3: MENOR AVALIAÇÃO POR IDIOMA
    # --------------------------------------------------------

  dados_avaliacao = (dff.dropna(subset=["original_language", "vote_average"]).groupby("original_language", as_index=False)["vote_average"].min().sort_values("vote_average"))

  fig_barra_voteAvarege = px.bar(
    dados_avaliacao,
    x="original_language",
    y="vote_average",
    color_discrete_sequence=["blue"],
    title="Menor avaliação por idioma",
    labels={
        "original_language": "Idioma original",
        "vote_average": "Menor avaliação"
    }
)

  fig_barra_voteAvarege.update_traces(
     marker_line_color="#2C3E50",
     marker_line_width=1.5
    )

    # --------------------------------------------------------
    # GRÁFICO 4: LINHA
    # Popularidade média por ano
    # --------------------------------------------------------

  dados_linha = dff.dropna(subset=["release_date", "popularity"] ).copy()
    
  dados_linha["ano"] = dados_linha["release_date"].dt.year

  dados_linha = (dados_linha.groupby("ano", as_index=False)["popularity"].mean().sort_values("ano"))

  fig_linha = px.line(
    dados_linha,
    x="ano",
    y="popularity",
    markers=True,
    title="Popularidade média por ano de lançamento",
    labels={
        "ano": "Ano",
        "popularity": "Popularidade média"
        }
    )

    # --------------------------------------------------------
    # GRÁFICO 5: HISTOGRAMA
    # Distribuição das avaliações
    # --------------------------------------------------------

  fig_histograma = px.histogram(
    dff.dropna(subset=["vote_average"]),
    x="vote_average",
    range_x=[0, 10],
    nbins=5,
    title="Distribuição das avaliações dos filmes",
    labels={
        "vote_average": "Avaliação dos filmes",
        "count": "Quantidade de filmes"
    },
    color_discrete_sequence=["#3498db"]
)

  fig_histograma.update_traces(
    xbins=dict(start=0, end=10, size=2),
    marker_line_color="#2c3e50",
    marker_line_width=1.5,
    opacity=0.85
  )

    # --------------------------------------------------------
    # GRÁFICO 6: BOXPLOT
    # Distribuição de votos por mês
    # --------------------------------------------------------

  dados_box = dff.dropna(subset=["release_date", "vote_count"]).copy()

  dados_box["release_month"] = (dados_box["release_date"].dt.month)

  dados_box["mes"] = dados_box["release_month"].map(dict(enumerate(meses_labels, start=1)))

  fig_box = px.box(
    dados_box,
    x="mes",
    y="vote_count",
    category_orders={"mes": meses_labels},
    title="Distribuição de votos por mês de lançamento",
    labels={
        "mes": "Mês de lançamento",
        "vote_count": "Quantidade de votos"
    },
    points=False,
    color_discrete_sequence=["cornflowerblue"]
    )

  fig_box.update_layout(
    xaxis_title="Mês",
    yaxis_title="Quantidade de votos",
    template="plotly_white"
)

    # --------------------------------------------------------
    # GRÁFICO 7: HEATMAP
    # Correlação entre variáveis numéricas
    # --------------------------------------------------------

  colunas_corr = [
    "vote_average",
    "vote_count",
    "popularity"]

  matriz_corr = dff[colunas_corr].corr()

  fig_heatmap = px.imshow(
    matriz_corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    aspect="auto",
    title="Mapa de calor de correlação entre variáveis",
    labels={
        "x": "Variáveis",
        "y": "Variáveis",
         "color": "Correlação"
    }
)

  fig_heatmap.update_traces(
    xgap=1,
    ygap=1
)

  fig_heatmap.update_layout(
    template="plotly_white"
)

    # --------------------------------------------------------
    # GRÁFICO 8: LINHA
    # Popularidade mensal dos filmes lançados em 2026
    # --------------------------------------------------------

  df_2026 = dff[(dff["release_date"] >= "2026-01-01") &(dff["release_date"] < "2027-01-01")].copy()
    
  df_mensal = (
    df_2026.dropna(subset=["release_date", "popularity"]).set_index("release_date").resample("M")["popularity"].sum().reset_index())
  
  fig_linha_popu = px.line(
    df_mensal,
    x="release_date",
    y="popularity",
    title="Evolução mensal da popularidade dos filmes lançados em 2026",
    labels={
        "release_date": "Mês",
        "popularity": "Popularidade total"
    },
    markers=True
  )

  fig_linha_popu.update_traces(
    line=dict(color="royalblue", width=2.5),
    marker=dict(
        color="lightskyblue",
        size=8,
        line=dict(color="royalblue", width=1)
    )
)

  fig_linha_popu.update_layout(
    template="plotly_white",
    xaxis=dict(
        tickformat="%b",
        dtick="M1",
        range=["2026-01-01", "2026-12-31"],
        title="Mês"
    ),
    yaxis_title="Popularidade total"
)

    # --------------------------------------------------------
    # RETORNO: 3 KPIs + 8 GRÁFICOS = 11 VALORES
    # A ordem deve ser a mesma dos Outputs do callback.
    # --------------------------------------------------------

  return (
    f"{total_votos:,.0f}",
    f"{quantidade_filmes:,}",
    f"{media_popularidade:.2f}",
    fig_dispersao,
    fig_barra_votecount,
    fig_barra_voteAvarege,
    fig_linha,
    fig_histograma,
    fig_box,
    fig_heatmap,
    fig_linha_popu
)

# ============================================================
# 5. EXECUÇÃO DO SERVIDOR
# ============================================================

if __name__ == "__main__":
 app.run(port=8055, debug=False)