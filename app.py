import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Cards - Renda Fixa", layout="wide")

# --- INICIALIZAÇÃO DE ESTADO (SESSION STATE) ---
# Isso permite adicionar/remover ativos dinamicamente
if 'qtd_ativos' not in st.session_state:
    st.session_state.qtd_ativos = 1

# --- ESTILOS E CORES ---
CORES = {
    "fundo": "#11233c",        # Azul Midnight (Solicitado)
    "azul_claro": "#9dbdeb",   # Azul Claro para títulos
    "texto_branco": "#FFFFFF", # Branco para detalhes
    "dourado": "#d4af37",      # Dourado Metálico (Mais elegante que amarelo)
    "isento": "#40E0D0",       # Turquesa (Contraste moderno com azul escuro)
    "linha": "#2c3e50"         # Cor discreta para linhas divisórias
}

TIPOS_ATIVOS = [
    "CDB", "LCI", "LCA", "CRI", "CRA", "Debênture", "Tesouro Direto", 
    "LC", "RDB", "Fundo de Renda Fixa"
]

ATIVOS_FGC = ["CDB", "LCI", "LCA", "LC", "RDB"]

st.title("Gerador de Cards - Renda Fixa 🚀")

# --- 1. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuração")
    plataforma = st.selectbox("Onde vai postar?", ["WhatsApp", "Instagram"])
    
    formato = "Stories/Status"
    arquivo_template = "template.png"
    
    if plataforma == "Instagram":
        tipo_insta = st.radio("Formato:", ["Stories (9:16)", "Feed (4:5)"])
        if tipo_insta == "Feed (4:5)":
            formato = "Feed"
            arquivo_template = "template-feed.png"

    st.markdown("---")
    st.write("📂 **Controle de Ativos**")
    
    col_add, col_rem = st.columns(2)
    with col_add:
        if st.button("➕ Adicionar"):
            if st.session_state.qtd_ativos < 6: # Limite suave para não quebrar layout
                st.session_state.qtd_ativos += 1
                st.rerun()
    with col_rem:
        if st.button("➖ Remover"):
            if st.session_state.qtd_ativos > 1:
                st.session_state.qtd_ativos -= 1
                st.rerun()

# --- 2. ENTRADA DE DADOS ---
st.subheader(f"Editando {st.session_state.qtd_ativos} Ativo(s)")

dados_ativos = []

# Loop dinâmico baseado no session_state
for i in range(st.session_state.qtd_ativos):
    with st.container():
        st.markdown(f"**Ativo {i+1}**")
        col_a, col_b, col_c, col_d = st.columns([1.5, 2, 1.5, 1])
        
        with col_a:
            tipo = st.selectbox("Tipo", TIPOS_ATIVOS, key=f"tipo_{i}")
            subtipo = ""
            if tipo == "Tesouro Direto":
                subtipo = st.selectbox("Título", ["Selic", "IPCA+", "Prefixado", "Renda+"], key=f"sub_{i}")
        
        with col_b:
            label_emissor = "Emissor" if tipo != "Tesouro Direto" else "Governo"
            emissor = st.text_input(label_emissor, "Banco Master", key=f"emissor_{i}")
            
        with col_c:
            taxa = st.text_input("Rentabilidade", "120% do CDI", key=f"taxa_{i}")
        
        with col_d:
            rating = st.text_input("Rating", "AAA", key=f"rating_{i}")

        col_e, col_f, col_g, col_h = st.columns(4)
        with col_e:
            vencimento = st.text_input("Vencimento", "2 Anos", key=f"venc_{i}")
        with col_f:
            invest_min = st.text_input("Mínimo", "R$ 1.000", key=f"min_{i}")
        with col_g:
            pagamento_juros = st.selectbox("Juros", ["No Vencimento", "Mensais", "Semestrais"], key=f"juros_{i}")
        with col_h:
            st.write("") # Espaçamento
            st.write("") 
            isento_ir = st.checkbox("Isento IR", key=f"isento_{i}")
            
        st.markdown("---") # Linha separadora visual no formulário

        dados_ativos.append({
            "tipo": tipo,
            "subtipo": subtipo,
            "emissor": emissor,
            "rating": rating,
            "taxa": taxa,
            "vencimento": vencimento,
            "minimo": invest_min,
            "juros": pagamento_juros,
            "isento": isento_ir
        })

# --- 3. FUNÇÃO DE GERAÇÃO DE IMAGEM ---
def gerar_card_final(dados, template_path, formato_tipo):
    # Tenta carregar template, senão cria fundo com a cor solicitada #11233c
    try:
        img = Image.open(template_path)
    except:
        w, h = (1080, 1920) if formato_tipo == "Stories/Status" else (1080, 1350)
        img = Image.new('RGB', (w, h), color=CORES['fundo'])

    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Fontes
    try:
        font_titulo = ImageFont.truetype("Montserrat-Bold.ttf", 50)
        font_destaque = ImageFont.truetype("Montserrat-Bold.ttf", 90)
        font_texto = ImageFont.truetype("Montserrat-Regular.ttf", 45)
        font_pequena = ImageFont.truetype("Montserrat-Regular.ttf", 35)
        font_tag = ImageFont.truetype("Montserrat-Bold.ttf", 35) # Fonte para o tag ISENTO
    except:
        font_titulo = font_destaque = font_texto = font_pequena = font_tag = ImageFont.load_default()

    # Layout Dinâmico
    margem_topo = 380 
    margem_fundo = 250
    area_util = H - margem_topo - margem_fundo
    
    qtd = len(dados)
    altura_slot = area_util / qtd
    padding_slot = 40

    for idx, item in enumerate(dados):
        y_inicial = margem_topo + (idx * altura_slot) + padding_slot
        
        # 1. Título (Tipo + Emissor)
        nome_exibicao = f"{item['tipo']} {item['subtipo']}" if item['subtipo'] else item['tipo']
        texto_titulo = f"{nome_exibicao} - {item['emissor']}"
        if item['rating']:
            texto_titulo += f" ({item['rating']})"
            
        draw.text((100, y_inicial), texto_titulo, font=font_titulo, fill=CORES['azul_claro'])
        
        # 2. Taxa (Dourado Metálico)
        draw.text((100, y_inicial + 70), item['taxa'], font=font_destaque, fill=CORES['dourado'])
        
        # 3. Linha de Detalhes 1 (Prazo e Mínimo) - SEM EMOJIS NA IMAGEM
        detalhes_y = y_inicial + 190
        texto_detalhes = f"Prazo: {item['vencimento']}   |   Mín: {item['minimo']}"
        draw.text((100, detalhes_y), texto_detalhes, font=font_texto, fill=CORES['texto_branco'])
        
        # 4. Linha de Detalhes 2 (Juros + Isenção)
        linha_2_y = detalhes_y + 60
        texto_juros = f"Juros: {item['juros']}"
        draw.text((100, linha_2_y), texto_juros, font=font_pequena, fill=CORES['azul_claro'])
        
        # Lógica de Exibição do "ISENTO DE IR" (Ao lado dos juros)
        if item['isento']:
            # Calcula onde termina o texto dos juros para colocar o Isento ao lado
            w_juros = draw.textlength(texto_juros, font=font_pequena)
            
            # Desenha "ISENTO IR" em Turquesa/Ciano
            draw.text((100 + w_juros + 40, linha_2_y), "ISENTO DE IR", font=font_tag, fill=CORES['isento'])

        # Divisória visual entre ativos
        if idx < qtd - 1:
            linha_div_y = y_inicial + altura_slot - (padding_slot/2)
            draw.line([(150, linha_div_y), (W-150, linha_div_y)], fill=CORES['linha'], width=1)

    return img

# --- 4. GERADOR DE TEXTO WHATSAPP (COM EMOJIS E FGC CORRETO) ---
def gerar_texto_whatsapp(dados):
    texto_final = ""
    
    for item in dados:
        nome_ativo = f"{item['tipo']}"
        if item['subtipo']: nome_ativo += f" ({item['subtipo']})"
        
        texto_final += f"🏦 *{nome_ativo}*\n"
        texto_final += f"📍 {item['emissor']}"
        if item['rating']: texto_final += f" ({item['rating']})"
        texto_final += "\n"
        
        texto_final += f"📈 *Rentabilidade: {item['taxa']}*\n"
        
        texto_final += f"📅 Prazo: {item['vencimento']}\n"
        texto_final += f"💰 Mínimo: {item['minimo']}\n"
        
        if item['juros'] != "No Vencimento":
            texto_final += f"🔄 Juros: {item['juros']}\n"
            
        if item['isento']:
            texto_final += "✅ *Isento de Imposto de Renda*\n"
            
        # Lógica FGC Individual
        if item['tipo'] in ATIVOS_FGC:
            texto_final += "🔒 *Garantia FGC* (até R$ 250k)\n"
            
        texto_final += "-----------------------------------\n"
        
    return texto_final

# --- 5. BOTÃO DE GERAÇÃO ---
st.divider()

if st.button("✨ Gerar Card e Texto", type="primary"):
    # Gerar
    imagem_final = gerar_card_final(dados_ativos, arquivo_template, formato)
    texto_zap = gerar_texto_whatsapp(dados_ativos)
    
    st.success("Gerado!")
    col_img, col_txt = st.columns([1, 1])
    
    with col_img:
        st.image(imagem_final, caption=f"Layout: {formato}", use_container_width=True)
        buf = io.BytesIO()
        imagem_final.save(buf, format="PNG")
        st.download_button("📥 Baixar Imagem", buf.getvalue(), "card.png", "image/png")
        
    with col_txt:
        st.subheader("Texto para Copiar:")
        st.code(texto_zap, language=None)
