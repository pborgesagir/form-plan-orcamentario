import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from streamlit import text_input


# Display Title and Description
st.title("Formulário para Planejamento Orçamentário")

# Constants
UNIDADE_QUAL = [
    "CRER",
    "HDS",
    "HECAD",
    "HUGOL",
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
existing_data = conn.read(worksheet="Vendors", usecols=list(range(16)), ttl=15)
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
            elif existing_data["UNIDADE"].astype(str).str.contains(unidade).any():
                st.warning("Um custo com essa descrição para este mês já existe.")
            else:
                vendor_data = pd.DataFrame(
                    [
                        {
                            "UNIDADE": unidade,
                            "DESCRIÇÃO": descricao,
                            "CLASSIFICAÇÃO": classificacao,
                            "MÊS": meses,
                            "CUSTO": custo,
                            "OBSERVAÇÃO": observacao,
                        }
                    ]
                )
                updated_df = pd.concat([existing_data, vendor_data], ignore_index=True)
                conn.update(worksheet="Vendors", data=updated_df)
                st.success("Custo enviado com sucesso!")


elif action == "Editar Custo":
    st.markdown("Select a vendor and update their details.")

    vendor_to_update = st.selectbox(
        "Select a Vendor to Update", options=existing_data["UNIDADE"].tolist()
    )
    vendor_data = existing_data[existing_data["UNIDADE"] == vendor_to_update].iloc[
        0
    ]

    with st.form(key="update_form"):
        unidade = st.text_input(
            label="Company Name*", value=vendor_data["UNIDADE"]
        )
        descricao = st.selectbox(
            "Business Type*",
            options=UNIDADE_QUAL,
            index=UNIDADE_QUAL.index(vendor_data["DESCRIÇÃO"]),
        )
        CLASSIFICAÇÃO = st.multiselect(
            "CLASSIFICAÇÃO Offered",
            options=CLASSIFICAÇÃO,
            default=vendor_data["CLASSIFICAÇÃO"].split(", "),
        )
        years_in_business = st.slider(
            "Years in Business", 0, 50, int(vendor_data["JANEIRO"])
        )
        onboarding_date = st.date_input(
            label="Onboarding Date", value=pd.to_datetime(vendor_data["FEVEREIRO"])
        )
        observacao = st.text_area(
            label="Additional Notes", value=vendor_data["OBSERVAÇÃO"]
        )

        st.markdown("**required*")
        update_button = st.form_submit_button(label="Update Vendor Details")

        if update_button:
            if not unidade or not descricao:
                st.warning("Ensure all mandatory fields are filled.")
            else:
                # Removing old entry
                existing_data.drop(
                    existing_data[
                        existing_data["UNIDADE"] == vendor_to_update
                    ].index,
                    inplace=True,
                )
                # Creating updated data entry
                updated_vendor_data = pd.DataFrame(
                    [
                        {
                            "UNIDADE": unidade,
                            "DESCRIÇÃO": descricao,
                            "CLASSIFICAÇÃO": ", ".join(CLASSIFICAÇÃO),
                            "JANEIRO": years_in_business,
                            "FEVEREIRO": onboarding_date.strftime("%Y-%m-%d"),
                            "OBSERVAÇÃO": observacao,
                        }
                    ]
                )
                # Adding updated data to the dataframe
                updated_df = pd.concat(
                    [existing_data, updated_vendor_data], ignore_index=True
                )
                conn.update(worksheet="Vendors", data=updated_df)
                st.success("Vendor details successfully updated!")

# Ver tabela de Custo
elif action == "Ver tabela de Custo":
    st.dataframe(existing_data)

# Deletar Custo
elif action == "Deletar Custo":
    vendor_to_delete = st.selectbox(
        "Select a Vendor to Delete", options=existing_data["UNIDADE"].tolist()
    )

    if st.button("Delete"):
        existing_data.drop(
            existing_data[existing_data["UNIDADE"] == vendor_to_delete].index,
            inplace=True,
        )
        conn.update(worksheet="Vendors", data=existing_data)
        st.success("Vendor successfully deleted!")

