import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# Configuração da página
st.set_page_config(page_title="Gerador de Cards CDB", layout="centered")

st.title("Gerador de Cards para WhatsApp")

# --- 1. ENTRADA DE DADOS ---
st.subheader("Dados da Oportunidade")
col1, col2 = st.columns(2)
with col1:
    banco = st.text_input("Nome do Banco", "Banco Master")
    taxa = st.text_input("Taxa", "130% do CDI")
with col2:
    prazo = st.text_input("Prazo", "2 Anos")
    invest_min = st.text_input("Investimento Mínimo", "R$ 1.000,00")

# --- 2. FUNÇÃO DE GERAÇÃO ---
def gerar_card(banco, taxa, prazo, minimo):
    # Tenta carregar seu template (se não tiver, cria um fundo preto para teste)
    try:
        # O ideal é ter um arquivo 'template.png' na pasta do projeto
        img = Image.open("template.png") 
    except:
        # Cria um fundo cinza escuro se não achar o template
        img = Image.new('RGB', (1080, 1920), color = (30, 30, 30))
    
    draw = ImageDraw.Draw(img)
    
    # Configurar Fontes (Tenta carregar uma fonte bonita, senão usa padrão)
    try:
        # Coloque o arquivo .ttf da sua fonte na pasta
        font_titulo = ImageFont.truetype("Arial.ttf", 100)
        font_texto = ImageFont.truetype("Arial.ttf", 60)
    except:
        font_titulo = ImageFont.load_default()
        font_texto = ImageFont.load_default()

    # --- DESENHAR NA IMAGEM (Ajuste os valores X, Y conforme seu template) ---
    
    # Cor Dourada (RGB)
    cor_destaque = (255, 215, 0)
    cor_texto = (255, 255, 255)

    # Exemplo de posicionamento
    draw.text((100, 400), "OPORTUNIDADE:", font=font_texto, fill=cor_texto)
    draw.text((100, 500), banco, font=font_titulo, fill=cor_destaque)
    
    draw.text((100, 700), "TAXA:", font=font_texto, fill=cor_texto)
    draw.text((100, 800), taxa, font=font_titulo, fill=cor_destaque)
    
    draw.text((100, 1000), f"Prazo: {prazo}", font=font_texto, fill=cor_texto)
    draw.text((100, 1100), f"Mínimo: {minimo}", font=font_texto, fill=cor_texto)

    return img

# --- 3. EXIBIÇÃO E DOWNLOAD ---
if st.button("Gerar Imagem"):
    imagem_final = gerar_card(banco, taxa, prazo, invest_min)
    
    # Mostra na tela
    st.image(imagem_final, caption="Pré-visualização", use_container_width=True)
    
    # Botão de Download
    buf = io.BytesIO()
    imagem_final.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Baixar Imagem para WhatsApp",
        data=byte_im,
        file_name="card_cdb.png",
        mime="image/png"
    )
