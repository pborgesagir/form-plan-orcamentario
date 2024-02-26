import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit import text_input




st.set_page_config(
    page_title='Formulário para Planejamento Orçamentário',
    page_icon='📝'
)

# Display Title and Description
st.title("Formulário de Planejamento e Execução Orçamentária")



# Constants
UNIDADE_QUAL = [
    "CRER",
    "HDS",
    "HECAD",
    "HUGOL",
]


EXECUCAO_QUAL = [
    "PLANEJADO",
    "EXECUTADO",
]

CLASSIFICACAO_QUAL = [
    "Água",
    "Central de gases",
    "Climatização artificial e aquecimento solar",
    "Contrato engenharia clínica",
    "Contrato manutenção predial",
    "Contrato projetos",
    "Elevadores",
    "Energia elétrica",
    "Grupo gerador",
    "Inspeções e qualificações",
    "Locação de equipamentos",
    "Manutenção equipamentos de imagem",
    "Manutenção pontual fora orçamento",
    "Manutenções diversas",
    "Nobreaks",
    "Outros",
]
MESES_DO_ANO = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]





# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(worksheet="Respostas", usecols=list(range(8)), ttl=7)
existing_data = existing_data.dropna(how="all")

action = st.selectbox(
    "Escolha a ação que deseja",
    [
        "Entrada de Custo",
        "Editar Custo",
        "Ver tabela de Custo",
        "Deletar Custo",
    ],
)

if action == "Entrada de Custo":
    st.markdown("Dê entrada de gastos que desejar.")
    with st.form(key="vendor_form"):
        unidade = st.selectbox(
            "Unidade*", options=UNIDADE_QUAL, index=None
        )
        execucao = st.selectbox(
            "Execução orçamentária*", options=EXECUCAO_QUAL, index=None
        )
        descricao = text_input(label="Descrição*")
        classificacao = st.selectbox(
            "Classificação*", options=CLASSIFICACAO_QUAL, index=None
        )
        meses = st.selectbox(
            "Mês*", options=MESES_DO_ANO, index=None
        )
        custo = st.text_input(label="Valor do custo*")
        observacao = st.text_area(label="Observações")

        st.markdown("**Campo obrigatório*")
        submit_button = st.form_submit_button(label="Enviar Custo")

        if submit_button:
            if not unidade or not descricao or not classificacao or not meses or not custo:
                st.warning("Verifique se todos os campos obrigatórios foram preenchidos.")
            elif ((existing_data["UNIDADE"].astype(str) == unidade) & 
                (existing_data["DESCRIÇÃO"].astype(str) == descricao) & 
                (existing_data["EXECUÇÃO ORÇAMENTÁRIA"].astype(str) == execucao) &
                (existing_data["MÊS"].astype(str) == meses)).any():
                st.warning("Um custo com essa descrição para este mês já existe.")

            else:
                vendor_data = pd.DataFrame(
                    [
                        {
                            "UNIDADE": unidade,
                            "EXECUÇÃO ORÇAMENTÁRIA": execucao,
                            "DESCRIÇÃO": descricao,
                            "CLASSIFICAÇÃO": classificacao,
                            "MÊS": meses,
                            "CUSTO": custo,
                            "OBSERVAÇÃO": observacao,
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)
                conn.update(worksheet="Respostas", data=updated_df)
                st.success("Custo enviado com sucesso!")


# ...
# ...

elif action == "Editar Custo":
    st.markdown("Selecione um custo e edite o que for necessário.")

    vendor_to_update = st.selectbox(
        "Selecione um custo para editar", options=existing_data["ID"].tolist()
    )
    vendor_data = existing_data[existing_data["ID"] == vendor_to_update].iloc[0]

    with st.form(key="update_form"):
        unidade = st.selectbox(
            "Unidade*",
            options=UNIDADE_QUAL,
            index=UNIDADE_QUAL.index(vendor_data["UNIDADE"])
        )
        execucao = st.selectbox(
            "Execução orçamentária*",
            options=EXECUCAO_QUAL,
            index=EXECUCAO_QUAL.index(vendor_data["EXECUÇÃO ORÇAMENTÁRIA"])
        )
        descricao = st.text_input(
            label="Descrição*", value=vendor_data["DESCRIÇÃO"]
        )
        classificacao = st.selectbox(
            "Classificação*",
            options=CLASSIFICACAO_QUAL,
            index=CLASSIFICACAO_QUAL.index(vendor_data["CLASSIFICAÇÃO"])
        )

        
        meses = st.selectbox(
            "Mês*",
            options=MESES_DO_ANO,
            index=MESES_DO_ANO.index(vendor_data["MÊS"])
        )
        custo = st.text_input(
            label="Valor do Custo*", value=vendor_data["CUSTO"]
        )
        # Check if "OBSERVAÇÃO" column is present in vendor_data
        observacao_default = vendor_data.get("OBSERVAÇÃO", "")
        observacao = st.text_area(
            label="Observação", value=observacao_default
        )
        

        # ... (other input fields)

        st.markdown("**required*")
        update_button = st.form_submit_button(label="Atualizar entrada de custo")

        if update_button:
            if not unidade or not descricao or not classificacao or not observacao:
                st.warning("Preencha todos os campos obrigatórios.")
            else:
                # Removing old entry
                existing_data.drop(
                    existing_data[
                        existing_data["ID"] == vendor_to_update
                    ].index,
                    inplace=True,
                )
                # Creating updated data entry
                updated_vendor_data = pd.DataFrame(
                    [
                        {
                            "UNIDADE": unidade,
                            "EXECUÇÃO ORÇAMENTÁRIA": execucao,
                            "DESCRIÇÃO": descricao,
                            "CLASSIFICAÇÃO": classificacao,
                            "MÊS": meses,
                            "CUSTO": custo,
                            "OBSERVAÇÃO": observacao,
                        }
                    ]
                )
                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [existing_data, updated_vendor_data], ignore_index=True
                )
                conn.update(worksheet="Respostas", data=updated_df)
                st.success("Vendor details successfully updated!")




# Ver tabela de Custo
elif action == "Ver tabela de Custo":
    st.dataframe(existing_data)

# Deletar Custo
elif action == "Deletar Custo":
    vendor_to_delete = st.selectbox(
        "Selecione um custo para deletar", options=existing_data["ID"].tolist()
    )

    if st.button("Delete"):
        existing_data.drop(
            existing_data[existing_data["ID"] == vendor_to_delete].index,
            inplace=True,
        )
        conn.update(worksheet="Respostas", data=existing_data)
        st.success("Custo deletado com sucesso!")

