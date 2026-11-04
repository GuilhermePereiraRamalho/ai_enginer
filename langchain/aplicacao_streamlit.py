from decouple import config
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import streamlit as st


api_key = config("OPENAI_API_KEY")
openai = ChatOpenAI(
    api_key=api_key,
    model='gpt-4o-mini',
    temperature=0,
    store=False
)

template = '''
    Você é um analista financeiro.
    Escreva um relatório financeiro detalhado para a empresa "{empresa}"
    para o periodo {periodo}.

    O relatório deve ser escrito em {idioma} e incluir a seguinte análise:
    {analise}

    Certifique-se de fornecer insights e conclusōes para esta seçāo.
    Formate o relatório utilizando Markdown.
'''

prompt_template = PromptTemplate.from_template(template=template)

empresas = [
    'ACME corp',
    'Globex Corporation',
    'Soylent Corp',
    'Initech',
    'Umbrella Corporation'
]
trimestres = ['Q1', 'Q2', 'Q3', 'Q4']
anos = [2021, 2022, 2023, 2024]
idiomas = [
    'Português',
    'Inglês',
    'Espanhol',
    'Italiano',
    'Alemāo'
]
analises = [
    'Análise de balanço patrimonial',
    'Análise de fluxo de caixa',
    'Análise de Tendencias',
    'Análise de receita e lucro',
    'Análise de posiçāo de mercado',
]

st.title('Gerador de Relatório Financeiro')

empresa = st.sidebar.selectbox('Selecione a empresa: ', empresas)
trimestre = st.sidebar.selectbox('Selecione o trimestre: ', trimestres)
ano = st.sidebar.selectbox('Selecione o ano: ', anos)
periodo = f"{trimestre} {ano}"
idioma = st.sidebar.selectbox('Selecione o idioma: ', idiomas)
analise = st.sidebar.selectbox('Selecione a análise: ', analises)

if st.sidebar.button('Gerar Relatório'):
    prompt = prompt_template.format(
        empresa=empresa,
        periodo=periodo,
        idioma=idioma,
        analise=analise
    )
    response = openai.invoke(prompt)

    st.subheader('Relatório Gerado:')
    st.write(response.content)
