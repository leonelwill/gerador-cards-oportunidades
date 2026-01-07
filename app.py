import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Cards - Renda Fixa", layout="wide")

# --- INICIALIZAÇÃO DE ESTADO ---
if 'qtd_ativos' not in st.session_state:
    st.session_state.qtd_ativos = 1

# --- ESTILOS E CORES ---
CORES = {
    "fundo": "#11233c",        # Azul Midnight
    "azul_claro": "#9dbdeb",   # Azul Claro (Subtítulos)
    "texto_branco": "#FFFFFF", # Branco (Detalhes)
    "dourado": "#d4af37",      # Dourado Metálico (Taxas)
    "titulo_card": "#ffffff",  # Branco puro para o título principal
    "isento": "#40E0D0",       # Turquesa
    "linha": "#2c3e50"         # Cinza escuro discreto
}

# --- MAPAS DE EMOJIS E CATEGORIAS ---
MAPA_EMOJIS = {
    "CRA": "🚜", "LCA": "🚜",      # Agro
    "CRI": "🏢", "LCI": "🏢",      # Imobiliário
    "Debênture": "🏭",             # Infra/Empresa
    "Tesouro Direto": "🇧🇷",        # Governo
    "CDB": "🏦", "LC": "🏦", "RDB": "🏦", "Fundo de Renda Fixa": "📈"
}

ATIVOS_FGC = ["CDB", "LCI", "LCA", "LC", "RDB"]

# Lista de sugestões de Títulos
SUGESTOES_TITULO = [
    "Destaques da Semana",
    "Oportunidades Renda Fixa",
    "Carteira Recomendada",
    "Melhores Taxas Hoje",
    "Seleção do Assessor",
    "Giro de Mercado"
]

st.title("Gerador de Cards - Renda Fixa 🚀")

# --- 1. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuração Visual")
    plataforma = st.selectbox("Plataforma", ["WhatsApp", "Instagram"])
    
    # Lógica de Template
    formato = "Stories/Status"
    arquivo_template = "template.png"
    if plataforma == "Instagram":
        tipo_insta = st.radio("Formato Insta:", ["Stories (9:16)", "Feed (4:5)"])
        if tipo_insta == "Feed (4:5)":
            formato = "Feed"
            arquivo_template = "template-feed.png"

    st.markdown("---")
    st.write("📝 **Título do Card**")
    # Opção de selecionar ou escrever livremente
    modo_titulo = st.radio("Estilo do Título:", ["Selecionar da Lista", "Personalizado"])
    
    if modo_titulo == "Selecionar da Lista":
        titulo_card = st.selectbox("Escolha um título:", SUGESTOES_TITULO)
    else:
        titulo_card = st.text_input("Digite o título:", "Oportunidades Exclusivas")

    st.markdown("---")
    st.write("📂 **Ativos**")
    c1, c2 = st.columns(2)
    if c1.button("➕ Adicionar"):
        if st.session_state.qtd_ativos < 5:
            st.session_state.qtd_ativos += 1
            st.rerun()
    if c2.button("➖ Remover"):
        if st.session_state.qtd_ativos > 1:
            st.session_state.qtd_ativos -= 1
            st.rerun()

# --- 2. ENTRADA DE DADOS ---
st.subheader(f"Editando {st.session_state.qtd_ativos} Ativo(s)")

dados_ativos = []

for i in range(st.session_state.qtd_ativos):
    with st.container():
        st.markdown(f"#### 📄 Ativo {i+1}")
        
        # Linha 1: Tipo, Emissor, Rating
        c_tipo, c_emissor, c_rating = st.columns([1.5, 2.5, 1])
        with c_tipo:
            tipo = st.selectbox("Tipo", list(MAPA_EMOJIS.keys()), key=f"tipo_{i}")
            subtipo = ""
            if tipo == "Tesouro Direto":
                subtipo = st.selectbox("Título", ["Selic", "IPCA+", "Prefixado", "Renda+"], key=f"sub_{i}")
        
        with c_emissor:
            label_emissor = "Emissor" if tipo != "Tesouro Direto" else "Governo"
            emissor = st.text_input(label_emissor, "Banco Master", key=f"emissor_{i}")
        
        with c_rating:
            # Força Maiúsculas
            rating_input = st.text_input("Rating", "AAA", key=f"rating_{i}")
            rating = rating_input.upper()

        # Linha 2: Rentabilidade (Indexador + Taxa)
        st.caption("Rentabilidade")
        c_index, c_taxa_val = st.columns([1.5, 2])
        with c_index:
            indexador = st.selectbox("Indexador", ["% do CDI", "IPCA +", "Prefixado", "CDI +"], key=f"idx_{i}")
        with c_taxa_val:
            val_taxa = st.text_input("Valor da Taxa (Só número)", "120", key=f"val_taxa_{i}")
        
        # Montagem da String da Taxa
        if indexador == "% do CDI":
            taxa_final = f"{val_taxa}% do CDI"
        elif indexador == "IPCA +":
            taxa_final = f"IPCA + {val_taxa}%"
        elif indexador == "Prefixado":
            taxa_final = f"{val_taxa}% a.a."
        elif indexador == "CDI +":
            taxa_final = f"CDI + {val_taxa}%"
        else:
            taxa_final = val_taxa

        # Linha 3: Prazo e Mínimo
        c_prazo_val, c_prazo_unid, c_min, c_juros = st.columns([1, 1, 1.5, 1.5])
        with c_prazo_val:
            prazo_val = st.text_input("Prazo (Valor)", "2", key=f"pz_v_{i}")
        with c_prazo_unid:
            prazo_unid = st.selectbox("Unidade", ["Anos", "Meses", "Dias", "Vencimento"], key=f"pz_u_{i}")
        
        # Montagem da String do Prazo
        if prazo_unid == "Vencimento":
            vencimento_final = prazo_val # Assume que o user digitou a data
        else:
            # Tratamento singular/plural simples
            if prazo_val == "1":
                unidade_formatada = prazo_unid[:-1] # Remove o 's'
            else:
                unidade_formatada = prazo_unid
            vencimento_final = f"{prazo_val} {unidade_formatada}"

        with c_min:
            invest_min = st.text_input("Mínimo (R$)", "1.000,00", key=f"min_{i}")
        with c_juros:
            pagamento_juros = st.selectbox("Juros", ["No Vencimento", "Mensais", "Semestrais"], key=f"juros_{i}")
            
        # Isenção e Checkboxes
        isento_ir = st.checkbox("Isento de IR?", key=f"isento_{i}")
        
        st.markdown("---")

        dados_ativos.append({
            "tipo": tipo,
            "subtipo": subtipo,
            "emissor": emissor,
            "rating": rating,
            "taxa": taxa_final,
            "vencimento": vencimento_final,
            "minimo": invest_min,
            "juros": pagamento_juros,
            "isento": isento_ir
        })

# --- 3. FUNÇÃO DE GERAÇÃO DE IMAGEM ---
def gerar_card_final(dados, template_path, formato_tipo, titulo_top):
    try:
        img = Image.open(template_path)
    except:
        w, h = (1080, 1920) if formato_tipo == "Stories/Status" else (1080, 1350)
        img = Image.new('RGB', (w, h), color=CORES['fundo'])

    draw = ImageDraw.Draw(img)
    W, H = img.size

    # Carregar Fontes
    try:
        font_main_title = ImageFont.truetype("Montserrat-Bold.ttf", 65) # Título Principal
        font_titulo = ImageFont.truetype("Montserrat-Bold.ttf", 50)     # Nome do Ativo
        font_destaque = ImageFont.truetype("Montserrat-Bold.ttf", 90)   # Taxa
        font_texto = ImageFont.truetype("Montserrat-Regular.ttf", 45)   # Detalhes
        font_pequena = ImageFont.truetype("Montserrat-Regular.ttf", 35) # Juros
        font_tag = ImageFont.truetype("Montserrat-Bold.ttf", 35)        # Isento
    except:
        font_main_title = font_titulo = font_destaque = font_texto = font_pequena = font_tag = ImageFont.load_default()

    # --- DESENHAR TÍTULO PRINCIPAL ---
    # Centralizado no topo (ajustar Y conforme seu template, assumindo Y=200 como área segura)
    y_titulo_principal = 220 
    draw.text((W/2, y_titulo_principal), titulo_top.upper(), font=font_main_title, fill=CORES['titulo_card'], anchor="mm")

    # Layout Dinâmico
    margem_topo = 400  # Aumentei para caber o título
    margem_fundo = 250
    area_util = H - margem_topo - margem_fundo
    
    qtd = len(dados)
    altura_slot = area_util / qtd
    padding_slot = 40

    for idx, item in enumerate(dados):
        y_inicial = margem_topo + (idx * altura_slot) + padding_slot
        
        # 1. Nome do Ativo (Tipo + Emissor)
        nome_exibicao = f"{item['tipo']} {item['subtipo']}" if item['subtipo'] else item['tipo']
        texto_titulo = f"{nome_exibicao} - {item['emissor']}"
        if item['rating']:
            texto_titulo += f" ({item['rating']})"
            
        draw.text((100, y_inicial), texto_titulo, font=font_titulo, fill=CORES['azul_claro'])
        
        # 2. Taxa (Dourado)
        draw.text((100, y_inicial + 70), item['taxa'], font=font_destaque, fill=CORES['dourado'])
        
        # 3. Detalhes (Prazo e Mínimo)
        detalhes_y = y_inicial + 190
        texto_detalhes = f"Prazo: {item['vencimento']}   |   Mín: R$ {item['minimo']}"
        draw.text((100, detalhes_y), texto_detalhes, font=font_texto, fill=CORES['texto_branco'])
        
        # 4. Juros e Isenção
        linha_2_y = detalhes_y + 60
        texto_juros = f"Juros: {item['juros']}"
        draw.text((100, linha_2_y), texto_juros, font=font_pequena, fill=CORES['azul_claro'])
        
        if item['isento']:
            w_juros = draw.textlength(texto_juros, font=font_pequena)
            draw.text((100 + w_juros + 40, linha_2_y), "ISENTO DE IR", font=font_tag, fill=CORES['isento'])

        # Linha divisória
        if idx < qtd - 1:
            linha_div_y = y_inicial + altura_slot - (padding_slot/2)
            draw.line([(150, linha_div_y), (W-150, linha_div_y)], fill=CORES['linha'], width=1)

    return img

# --- 4. GERADOR DE TEXTO WHATSAPP ---
def gerar_texto_whatsapp(dados):
    texto_final = ""
    
    for item in dados:
        # Pega o emoji baseado no tipo
        emoji_ativo = MAPA_EMOJIS.get(item['tipo'], "💰")
        
        nome_ativo = f"{item['tipo']}"
        if item['subtipo']: nome_ativo += f" ({item['subtipo']})"
        
        # LINHA UNIFICADA: Emoji Tipo Emissor (Rating)
        linha_titulo = f"{emoji_ativo} *{nome_ativo} {item['emissor']}*"
        if item['rating']: linha_titulo += f" ({item['rating']})"
        
        texto_final += f"{linha_titulo}\n"
        
        texto_final += f"📈 *Rentabilidade: {item['taxa']}*\n"
        texto_final += f"📅 Prazo: {item['vencimento']}"
        
        if item['isento']:
            texto_final += " (Isento de IR ✅)"
        texto_final += "\n"
        
        texto_final += f"💰 Mínimo: R$ {item['minimo']}\n"
        
        if item['juros'] != "No Vencimento":
            texto_final += f"🔄 Juros: {item['juros']}\n"
            
        # FGC Individual
        if item['tipo'] in ATIVOS_FGC:
            texto_final += "🔒 *Garantia FGC* (até R$ 250k)\n"
            
        texto_final += "-----------------------------------\n"
        
    return texto_final

# --- 5. BOTÃO DE GERAÇÃO ---
st.divider()

if st.button("✨ Gerar Card e Texto", type="primary"):
    imagem_final = gerar_card_final(dados_ativos, arquivo_template, formato, titulo_card)
    texto_zap = gerar_texto_whatsapp(dados_ativos)
    
    st.success("Conteúdo Gerado!")
    c_img, c_txt = st.columns([1, 1])
    
    with c_img:
        st.image(imagem_final, caption=f"Layout: {formato}", use_container_width=True)
        buf = io.BytesIO()
        imagem_final.save(buf, format="PNG")
        st.download_button("📥 Baixar Imagem", buf.getvalue(), "card.png", "image/png")
        
    with c_txt:
        st.subheader("Texto WhatsApp:")
        st.code(texto_zap, language=None)
