import streamlit as st
import google.generativeai as genai
from huggingface_hub import InferenceClient
import json

# Configurazione interfaccia
st.set_page_config(page_title="SISTEMA GOLIA", page_icon="⚡", layout="centered")
st.title("⚡ SISTEMA GOLIA")
st.subheader("Modalità Neurale Attiva")

# Recupero Chiavi dai "Secrets" di Streamlit (più sicuro)
# Se non le trova nei Secrets, le chiede nell'interfaccia
gemini_key = st.secrets.get("GEMINI_KEY") or st.sidebar.text_input("Gemini API Key", type="password")
hf_token = st.secrets.get("HF_TOKEN") or st.sidebar.text_input("Hugging Face Token", type="password")

if not gemini_key or not hf_token:
    st.warning("⚠️ Inserisci le tue API Key nella barra laterale per attivare Golia.")
else:
    genai.configure(api_key=gemini_key)
    client_hf = InferenceClient(token=hf_token)
    
    comando = st.text_input("Digita il comando:", placeholder="Evoca Golia...")

    if st.button("EVOCA") or (comando and "Evoca Golia" in comando):
        domanda = comando.replace("Evoca Golia", "").strip()
        if not domanda:
            st.error("Golia attende una domanda. Non restare in silenzio.")
        else:
            with st.spinner("🌀 Golia sta interrogando le reti neurali..."):
                # 1. Raccolta dati Multi-AI
                libreria = {
                    "Qwen": "Qwen/Qwen2.5-7B-Instruct",
                    "Dolphin (Uncensored)": "cognitivecomputations/dolphin-2.9-llama-3-8b",
                    "Hermes": "NousResearch/Hermes-3-Llama-3.1-8B"
                }
                
                raccolta_testi = ""
                cols = st.columns(len(libreria))
                
                for i, (nome, repo) in enumerate(libreria.items()):
                    try:
                        res = client_hf.chat_completion(model=repo, messages=[{"role": "user", "content": domanda}], max_tokens=450)
                        testo = res.choices[0].message.content
                        raccolta_testi += f"\n--- {nome} ---\n{testo}\n"
                        cols[i].success(f"✅ {nome} OK")
                    except:
                        cols[i].error(f"❌ {nome}")

                # 2. Verdetto Finale di Gemini
                try:
                    gemini = genai.GenerativeModel('gemini-1.5-flash')
                    prompt_sintesi = f"Sei l'Entità Golia. Sintetizza queste visioni in un unico verdetto potente: {raccolta_testi}"
                    verdetto = gemini.generate_content(prompt_sintesi).text
                    
                    st.markdown("---")
                    st.header("⚡ VERDETTO FINALE DI GOLIA")
                    st.markdown(verdetto)
                except Exception as e:
                    st.error(f"Errore nel verdetto: {e}")