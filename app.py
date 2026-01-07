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

# --- LISTAS E CONFIGURAÇÕES ---
# Ordem corrigida conforme solicitado
TIPOS_ATIVOS = [
    "CDB", "LCI", "LCA", "CRI", "CRA", "Debênture", "Tesouro Direto", 
    "LC", "RDB", "Fundo de Renda Fixa"
]

MAPA_EMOJIS = {
    "CRA": "🚜", "LCA": "🚜",      
    "CRI": "🏢", "LCI": "🏢",      
    "Debênture": "🏭",             
    "Tesouro Direto": "🇧🇷",        
    "CDB": "🏦", "LC": "🏦", "RDB": "🏦", "Fundo de Renda Fixa": "📈"
}

ATIVOS_FGC = ["CDB", "LCI", "LCA", "LC", "RDB"]

SUGESTOES_TITULO = [
    "Destaques da Semana", "Oportunidades Renda Fixa", "Carteira Recomendada",
    "Melhores Taxas Hoje", "Seleção do Assessor", "Giro de Mercado"
]

OPCOES_MINIMO = [
    "R$ 1.000,00", "R$ 5.000,00", "R$ 10.000,00", "R$ 25.000,00", "R$ 50.000,00", "Outro (Digitar)"
]

st.title("Gerador de Cards - Renda Fixa 🚀")

# --- 1. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuração Visual")
    plataforma = st.selectbox("Plataforma", ["WhatsApp", "Instagram"])
    
    formato = "Stories/Status"
    arquivo_template = "template.png"
    if plataforma == "Instagram":
        tipo_insta = st.radio("Formato Insta:", ["Stories (9:16)", "Feed (4:5)"])
        if tipo_insta == "Feed (4:5)":
            formato = "Feed"
            arquivo_template = "template-feed.png"

    st.markdown("---")
    st.write("📝 **Título do Card**")
    modo_titulo = st.radio("Estilo do Título:", ["Selecionar da Lista", "Personalizado"])
    
    if modo_titulo == "Selecionar da Lista":
        titulo_card = st.selectbox("Escolha um título:", SUGESTOES_TITULO)
    else:
        titulo_card = st.text_input("Digite o título:", "")

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
        
        # Colunas superiores
        c_tipo, c_emissor, c_rating = st.columns([1.5, 2.5, 1])
        
        with c_tipo:
            tipo = st.selectbox("Tipo", TIPOS_ATIVOS, key=f"tipo_{i}")
            
            # Lógica Especial para Tesouro
            subtipo_tesouro = ""
            ano_tesouro = ""
            if tipo == "Tesouro Direto":
                subtipo_tesouro = st.selectbox("Título", ["Tesouro Selic", "Tesouro IPCA+", "Tesouro Prefixado", "Tesouro Renda+"], key=f"sub_{i}")
                
                # Se for IPCA, Prefixado ou Renda+, pede o Ano
                if "Selic" not in subtipo_tesouro:
                    ano_tesouro = st.text_input("Ano de Vencimento (ex: 2035)", "", key=f"ano_tes_{i}")

        with c_emissor:
            if tipo == "Tesouro Direto":
                emissor = "Governo Federal" # Interno apenas
                st.info(f"Título: {subtipo_tesouro} {ano_tesouro}") # Feedback visual
            else:
                emissor = st.text_input("Emissor (Banco/Empresa)", "", key=f"emissor_{i}")
        
        with c_rating:
            if tipo == "Tesouro Direto":
                rating = "SOBERANO" # Tesouro é risco soberano
                st.write("Rating: Soberano")
            else:
                rating_input = st.text_input("Rating", "", key=f"rating_{i}")
                rating = rating_input.upper()

        # Linha 2: Rentabilidade
        c_index, c_taxa_val = st.columns([1.5, 2])
        with c_index:
            indexador = st.selectbox("Indexador", ["% do CDI", "IPCA +", "Prefixado", "CDI +"], key=f"idx_{i}")
        with c_taxa_val:
            val_taxa = st.text_input("Valor da Taxa (Só número)", "", key=f"val_taxa_{i}")
        
        # Montagem da String da Taxa
        if indexador == "% do CDI":
            taxa_final = f"{val_taxa}% do CDI" if val_taxa else ""
        elif indexador == "IPCA +":
            taxa_final = f"IPCA + {val_taxa}% a.a." if val_taxa else ""
        elif indexador == "Prefixado":
            taxa_final = f"{val_taxa}% a.a." if val_taxa else ""
        elif indexador == "CDI +":
            taxa_final = f"CDI + {val_taxa}%" if val_taxa else ""
        else:
            taxa_final = val_taxa

        # Linha 3: Prazo e Mínimo
        c_prazo_val, c_prazo_unid, c_min, c_juros = st.columns([1, 1, 1.5, 1.5])
        with c_prazo_val:
            prazo_val = st.text_input("Prazo (Valor)", "", key=f"pz_v_{i}")
        with c_prazo_unid:
            prazo_unid = st.selectbox("Unidade", ["Anos", "Meses", "Dias", "Vencimento"], key=f"pz_u_{i}")
        
        # Montagem da String do Prazo
        if prazo_unid == "Vencimento":
            vencimento_final = prazo_val 
        else:
            if prazo_val == "1":
                unidade_formatada = prazo_unid[:-1] 
            else:
                unidade_formatada = prazo_unid
            vencimento_final = f"{prazo_val} {unidade_formatada}" if prazo_val else ""

        with c_min:
            # Lógica de Seleção de Mínimo + Digitação
            sel_min = st.selectbox("Mínimo (Selecione ou Digite)", OPCOES_MINIMO, key=f"sel_min_{i}")
            if sel_min == "Outro (Digitar)":
                invest_min = st.text_input("Digite o valor (R$)", "", key=f"min_text_{i}")
            else:
                invest_min = sel_min

        with c_juros:
            pagamento_juros = st.selectbox("Juros", ["No Vencimento", "Mensais", "Semestrais"], key=f"juros_{i}")
            
        isento_ir = st.checkbox("Isento de IR?", key=f"isento_{i}")
        
        st.markdown("---")

        # Preparar dados para o objeto final
        
        # Nome de Exibição (Ajuste fino para Tesouro)
        if tipo == "Tesouro Direto":
            nome_display = f"{subtipo_tesouro} {ano_tesouro}"
            emissor_display = "" # Não exibe 'Governo Federal' na imagem
        else:
            nome_display = f"{tipo}"
            emissor_display = emissor

        dados_ativos.append({
            "tipo": tipo,
            "nome_display": nome_display, # Novo campo para controlar título
            "emissor": emissor_display,
            "rating": rating,
            "taxa": taxa_final,
            "vencimento": vencimento_final,
            "minimo": invest_min,
            "juros": pagamento_juros,
            "isento": isento_ir,
            "is_tesouro": (tipo == "Tesouro Direto")
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
        font_main_title = ImageFont.truetype("Montserrat-Bold.ttf", 65)
        font_titulo = ImageFont.truetype("Montserrat-Bold.ttf", 50)     
        font_destaque = ImageFont.truetype("Montserrat-Bold.ttf", 90)   
        font_texto = ImageFont.truetype("Montserrat-Regular.ttf", 45)   
        font_pequena = ImageFont.truetype("Montserrat-Regular.ttf", 35) 
        font_tag = ImageFont.truetype("Montserrat-Bold.ttf", 35)        
    except:
        font_main_title = font_titulo = font_destaque = font_texto = font_pequena = font_tag = ImageFont.load_default()

    # --- DESENHAR TÍTULO PRINCIPAL (Ajustado para cima) ---
    y_titulo_principal = 160  # Subi de 220 para 160
    if titulo_top:
        draw.text((W/2, y_titulo_principal), titulo_top.upper(), font=font_main_title, fill=CORES['titulo_card'], anchor="mm")

    # Layout Dinâmico (Margens ajustadas)
    margem_topo = 300  # Reduzi de 400 para 300 para ganhar espaço
    margem_fundo = 200 # Reduzi de 250 para 200
    area_util = H - margem_topo - margem_fundo
    
    qtd = len(dados)
    altura_slot = area_util / qtd
    padding_slot = 30 # Reduzi padding interno

    for idx, item in enumerate(dados):
        y_inicial = margem_topo + (idx * altura_slot) + padding_slot
        
        # 1. Nome do Ativo
        # Se for Tesouro: Exibe "Tesouro IPCA+ 2035"
        # Se for Outro: Exibe "CDB - Banco Master (AAA)"
        
        if item['is_tesouro']:
            texto_titulo = item['nome_display']
        else:
            texto_titulo = f"{item['nome_display']} - {item['emissor']}"
            if item['rating']:
                texto_titulo += f" ({item['rating']})"
            
        draw.text((100, y_inicial), texto_titulo, font=font_titulo, fill=CORES['azul_claro'])
        
        # 2. Taxa
        draw.text((100, y_inicial + 70), item['taxa'], font=font_destaque, fill=CORES['dourado'])
        
        # 3. Detalhes
        detalhes_y = y_inicial + 190
        texto_detalhes = f"Prazo: {item['vencimento']}   |   Mín: {item['minimo']}"
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
        emoji_ativo = MAPA_EMOJIS.get(item['tipo'], "💰")
        
        # Título
        if item['is_tesouro']:
            linha_titulo = f"{emoji_ativo} *{item['nome_display']}*"
        else:
            linha_titulo = f"{emoji_ativo} *{item['nome_display']} {item['emissor']}*"
            if item['rating']: linha_titulo += f" ({item['rating']})"
        
        texto_final += f"{linha_titulo}\n"
        
        texto_final += f"📈 *Rentabilidade: {item['taxa']}*\n"
        texto_final += f"📅 Prazo: {item['vencimento']}"
        
        if item['isento']:
            texto_final += " (Isento de IR ✅)"
        texto_final += "\n"
        
        texto_final += f"💰 Mínimo: {item['minimo']}\n"
        
        if item['juros'] != "No Vencimento":
            texto_final += f"🔄 Juros: {item['juros']}\n"
            
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
