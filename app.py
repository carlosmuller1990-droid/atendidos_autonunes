import pandas as pd
import re
import streamlit as st

st.set_page_config(page_title="Higienização de Base", layout="centered")

st.title("🧹 Higienização de Planilhas")
st.markdown("""
### ⚠️ Atenção à ordem dos arquivos:
- **1️⃣ Primeiro arquivo:** base que será higienizada (estrutura preservada)
- **2️⃣ Segundo arquivo:** base com os números que devem ser removidos

👉 **Os nomes dos arquivos não importam. Apenas a ordem do upload.**
""")

# -------------------------------
# Função de limpeza de telefone
# -------------------------------
def limpar_telefone(valor):
    valor = re.sub(r"\D", "", str(valor))
    if len(valor) > 9:
        return valor[-9:]  # remove DDD
    return valor

# -------------------------------
# Uploads (ordem define a lógica)
# -------------------------------
arquivo_base = st.file_uploader(
    "📂 1️⃣ Envie a PLANILHA BASE (será higienizada)",
    type=["csv"]
)

arquivo_exclusao = st.file_uploader(
    "📂 2️⃣ Envie a PLANILHA DE EXCLUSÃO (espelho de números)",
    type=["csv"]
)

# -------------------------------
# Processamento
# -------------------------------
if arquivo_base and arquivo_exclusao:
    try:
        df_base = pd.read_csv(arquivo_base, sep=";", dtype=str, keep_default_na=False)
        df_exclusao = pd.read_csv(arquivo_exclusao, sep=";", dtype=str, keep_default_na=False)

        # Validação da coluna de telefone na base
        if "FONE1_NR" not in df_base.columns:
            st.error("❌ A planilha BASE precisa conter a coluna 'FONE1_NR'")
            st.stop()

        # Usa automaticamente a primeira coluna da planilha de exclusão
        coluna_exclusao = df_exclusao.columns[0]

        # Limpa telefones da planilha de exclusão
        df_exclusao["TEL_LIMPO"] = df_exclusao[coluna_exclusao].apply(limpar_telefone)
        telefones_excluir = set(df_exclusao["TEL_LIMPO"])

        # Limpa telefone da base apenas para comparação
        df_base["TEL_LIMPO"] = df_base["FONE1_NR"].apply(limpar_telefone)

        # Filtragem
        df_final = df_base[~df_base["TEL_LIMPO"].isin(telefones_excluir)].copy()

        # Remove coluna auxiliar
        df_final.drop(columns=["TEL_LIMPO"], inplace=True)

        # Estatísticas
        removidos = len(df_base) - len(df_final)

        st.success("✅ Higienização concluída!")
        st.write(f"📊 Linhas originais: {len(df_base)}")
        st.write(f"📊 Linhas removidas: {removidos}")
        st.write(f"📊 Linhas finais: {len(df_final)}")

        # Download
        csv_final = df_final.to_csv(sep=";", index=False).encode("utf-8")
        st.download_button(
            "⬇️ Baixar planilha higienizada",
            csv_final,
            file_name="base_higienizada.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Erro ao processar os arquivos: {e}")
