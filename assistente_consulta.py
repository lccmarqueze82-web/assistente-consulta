import streamlit as st
from openai import OpenAI, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

st.set_page_config(page_title="Assistente de Consulta", layout="wide")

st.title("🩺 Assistente de Consulta")

# Inicializa o cliente OpenAI
# O erro RateLimitError é importado aqui para ser usado com tenacity
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.markdown("""
O assistente trabalha em 4 etapas:
1️⃣ **Caixa 1** – Informação crua  
2️⃣ **Caixa 2** – Aplica Prompt PEC1 atualizado  
3️⃣ **Caixa 3** – Sugestões e condutas  
4️⃣ **Caixa 4** – Chat livre com GPT  
---
""")

col1, col2, col3 = st.columns(3)

with col1:
    # Garante que as chaves de sessão existam
    if "caixa1" not in st.session_state: st.session_state["caixa1"] = ""
    caixa1 = st.text_area("CAIXA 1 - Informação Crua", height=250, key="caixa1")

with col2:
    if "caixa2" not in st.session_state: st.session_state["caixa2"] = ""
    caixa2 = st.text_area("CAIXA 2 - Prompt PEC1 Atualizado", height=250, key="caixa2")

with col3:
    if "caixa3" not in st.session_state: st.session_state["caixa3"] = ""
    caixa3 = st.text_area("CAIXA 3 - Sugestões e Discussão", height=250, key="caixa3")

if "caixa4" not in st.session_state: st.session_state["caixa4"] = ""
caixa4 = st.text_input("CAIXA 4 - Chat com GPT", key="caixa4")

colA, colB, colC = st.columns([1, 1, 2])

with colA:
    if st.button("🧹 LIMPAR"):
        for key in ["caixa1","caixa2","caixa3","caixa4"]:
            st.session_state[key] = ""
        st.rerun()

with colB:
    # Usando uma chave de estado para controlar a exibição do conteúdo copiado
    if st.button("📋 COPIAR CAIXA 2"):
        st.session_state["show_copy_box"] = True

if st.session_state.get("show_copy_box"):
    st.write("Conteúdo da Caixa 2 copiado (copie manualmente abaixo):")
    st.code(st.session_state["caixa2"])
    # Resetar a flag após a exibição para que não fique visível permanentemente
    # st.session_state["show_copy_box"] = False # Comentado para o Streamlit não remover a caixa imediatamente

with colC:
    aplicar = st.button("⚙️ Aplicar Prompt PEC1")


# ----------------------------------------------------------------------
# FUNÇÃO CORRIGIDA COM RETRY
# Aplica o decorador @retry para re-tentar a chamada em caso de RateLimitError
@retry(
    wait=wait_exponential(min=1, max=60), # Espera exponencialmente entre 1s e 60s
    stop=stop_after_attempt(5),           # Tenta no máximo 5 vezes
    retry=retry_if_exception_type(RateLimitError), # Re-tenta SOMENTE se for RateLimitError
    reraise=True # Re-lança o erro se todas as tentativas falharem
)
def gpt_reply(role, text):
    """
    Função para fazer a chamada à API da OpenAI com tratamento de RateLimitError.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()

# ----------------------------------------------------------------------

if aplicar and caixa1:
    # Adicionar um tratamento de erro mais geral caso todas as retentativas falhem
    try:
        with st.spinner("Aplicando Prompt PEC1..."):
            st.session_state["caixa2"] = gpt_reply(
                "Aplique o Prompt PEC1 atualizado ao texto fornecido.",
                caixa1
            )
            st.success("✅ Prompt aplicado!")
    except Exception as e:
        st.error(f"❌ Erro ao comunicar com a API. Tente novamente: {e}")

if st.session_state.get("caixa2"):
    if st.button("💬 Gerar Sugestões (Caixa 3)"):
        try:
            with st.spinner("Analisando diagnóstico..."):
                st.session_state["caixa3"] = gpt_reply(
                    "Sugira diagnósticos e condutas a partir do texto processado.",
                    st.session_state["caixa2"]
                )
                st.success("✅ Sugestões geradas!")
        except Exception as e:
            st.error(f"❌ Erro ao gerar sugestões. Tente novamente: {e}")

if caixa4:
    if st.button("💭 Enviar Chat (Caixa 4)"):
        try:
            with st.spinner("Respondendo..."):
                resposta = gpt_reply("Chat livre com GPT. Sua resposta deve ser concisa.", caixa4)
                st.markdown(f"**GPT:** {resposta}")
            # Limpa a caixa4 após o envio
            st.session_state["caixa4"] = ""
            st.rerun() # Dispara um rerun para limpar a caixa de input
        except Exception as e:
            st.error(f"❌ Erro ao enviar chat. Tente novamente: {e}")
