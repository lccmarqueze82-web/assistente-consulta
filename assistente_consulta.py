import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Assistente de Consulta", layout="wide")

st.title("🩺 Assistente de Consulta")

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
    caixa1 = st.text_area("CAIXA 1 - Informação Crua", height=250, key="caixa1")

with col2:
    caixa2 = st.text_area("CAIXA 2 - Prompt PEC1 Atualizado", height=250, key="caixa2")

with col3:
    caixa3 = st.text_area("CAIXA 3 - Sugestões e Discussão", height=250, key="caixa3")

caixa4 = st.text_input("CAIXA 4 - Chat com GPT", key="caixa4")

colA, colB, colC = st.columns([1, 1, 2])

with colA:
    if st.button("🧹 LIMPAR"):
        for key in ["caixa1","caixa2","caixa3","caixa4"]:
            st.session_state[key] = ""
        st.rerun()

with colB:
    if st.button("📋 COPIAR CAIXA 2"):
        st.write("Conteúdo da Caixa 2 copiado (copie manualmente abaixo):")
        st.code(st.session_state["caixa2"])

with colC:
    aplicar = st.button("⚙️ Aplicar Prompt PEC1")

def gpt_reply(role, text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()

if aplicar and caixa1:
    with st.spinner("Aplicando Prompt PEC1..."):
        st.session_state["caixa2"] = gpt_reply(
            "Aplique o Prompt PEC1 atualizado ao texto fornecido.",
            caixa1
        )
        st.success("✅ Prompt aplicado!")

if st.session_state.get("caixa2"):
    if st.button("💬 Gerar Sugestões (Caixa 3)"):
        with st.spinner("Analisando diagnóstico..."):
            st.session_state["caixa3"] = gpt_reply(
                "Sugira diagnósticos e condutas a partir do texto processado.",
                st.session_state["caixa2"]
            )
            st.success("✅ Sugestões geradas!")

if caixa4:
    if st.button("💭 Enviar Chat (Caixa 4)"):
        with st.spinner("Respondendo..."):
            resposta = gpt_reply("Chat livre com GPT.", caixa4)
            st.markdown(f"**GPT:** {resposta}")
