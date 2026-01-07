import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Cards - Renda Fixa", layout="wide")

# --- ESTILOS E CONSTANTES ---
CORES = {
    "fundo": "#131a30",
    "azul_medio": "#253164",
    "azul_claro": "#9dbdeb",
    "texto_branco": "#FFFFFF",
    "dourado": "#FFD700",
    "verde_isento": "#00FF7F"
}

# Lista de Ativos
TIPOS_ATIVOS = [
    "CDB", "LCI", "LCA", "CRI", "CRA", "Debênture", "Tesouro Direto", 
    "LC", "RDB", "Fundo de Renda Fixa"
]

# Ativos com Garantia FGC
ATIVOS_FGC = ["CDB", "LCI", "LCA", "LC", "RDB"]

st.title("Gerador de Cards - Renda Fixa 🚀")

# --- 1. BARRA LATERAL (CONFIGURAÇÕES GERAIS) ---
with st.sidebar:
    st.header("⚙️ Configuração do Card")
    
    # Seleção de Plataforma
    plataforma = st.selectbox("Onde vai postar?", ["WhatsApp", "Instagram"])
    
    formato = "Stories/Status" # Padrão
    arquivo_template = "template.png"
    
    if plataforma == "Instagram":
        tipo_insta = st.radio("Formato:", ["Stories (9:16)", "Feed (4:5)"])
        if tipo_insta == "Feed (4:5)":
            formato = "Feed"
            arquivo_template = "template-feed.png"
    
    # Quantidade de Ativos no Card
    qtd_ativos = st.slider("Quantidade de Ativos no Card", 1, 4, 1)

# --- 2. ENTRADA DE DADOS (DINÂMICA) ---
st.subheader(f"Dados dos Ativos ({qtd_ativos} selecionados)")

dados_ativos = []

# Loop para criar formulários para cada ativo
for i in range(qtd_ativos):
    with st.expander(f"Ativo #{i+1}", expanded=True):
        col_tipo, col_emissor, col_taxa = st.columns(3)
        
        with col_tipo:
            tipo = st.selectbox(f"Tipo do Ativo {i+1}", TIPOS_ATIVOS, key=f"tipo_{i}")
            subtipo = ""
            if tipo == "Tesouro Direto":
                subtipo = st.selectbox(f"Título {i+1}", ["Tesouro Selic", "Tesouro IPCA+", "Tesouro Prefixado", "Renda+"], key=f"sub_{i}")
        
        with col_emissor:
            emissor_label = "Emissor (Banco/Empresa)" if tipo != "Tesouro Direto" else "Governo Federal"
            emissor = st.text_input(emissor_label, "Banco Master", key=f"emissor_{i}")
            rating = st.text_input(f"Rating {i+1} (Opcional)", "AAA", key=f"rating_{i}")
            
        with col_taxa:
            taxa = st.text_input(f"Rentabilidade {i+1}", "120% do CDI", key=f"taxa_{i}")
            
        col_prazo, col_min, col_juros = st.columns(3)
        with col_prazo:
            vencimento = st.text_input(f"Vencimento/Prazo {i+1}", "2 Anos", key=f"venc_{i}")
        with col_min:
            invest_min = st.text_input(f"Aporte Mínimo {i+1}", "R$ 1.000,00", key=f"min_{i}")
        with col_juros:
            pagamento_juros = st.selectbox(f"Pagamento de Juros {i+1}", ["No Vencimento", "Mensal", "Semestral"], key=f"juros_{i}")
            
        isento_ir = st.checkbox(f"Isento de IR? {i+1}", key=f"isento_{i}")
        
        # Salva os dados num dicionário
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

# --- 3. FUNÇÃO DE GERAÇÃO DE IMAGEM (A MÁGICA) ---
def gerar_card_multiplo(dados, template_path, formato_tipo):
    try:
        img = Image.open(template_path)
    except:
        # Fallback se não achar a imagem: cria fundo cinza
        w, h = (1080, 1920) if formato_tipo == "Stories/Status" else (1080, 1350)
        img = Image.new('RGB', (w, h), color=(30, 30, 30))

    draw = ImageDraw.Draw(img)
    W, H = img.size

    # --- CARREGAR FONTES MONTSERRAT ---
    try:
        # Ajuste Fino: BOLD para o que precisa chamar atenção, REGULAR para leitura
        # Certifique-se que os arquivos chamam exatamente "Montserrat-Bold.ttf" e "Montserrat-Regular.ttf"
        font_titulo = ImageFont.truetype("Montserrat-Bold.ttf", 55) 
        font_destaque = ImageFont.truetype("Montserrat-Bold.ttf", 95) # Aumentei um pouco para impacto
        font_texto = ImageFont.truetype("Montserrat-Regular.ttf", 45)
        font_pequena = ImageFont.truetype("Montserrat-Regular.ttf", 35)
    except Exception as e:
        # Se der erro (arquivo não encontrado), avisa no terminal e usa padrão
        print(f"Erro ao carregar fontes: {e}")
        font_titulo = font_destaque = font_texto = font_pequena = ImageFont.load_default()

    # --- CÁLCULO DE POSICIONAMENTO DINÂMICO ---
    # Definir "Área Útil" onde os cards vão entrar
    # Margem superior (pular cabeçalho do template) e inferior (pular rodapé)
    margem_topo = 350 
    margem_fundo = 250
    area_util = H - margem_topo - margem_fundo
    
    qtd = len(dados)
    # Altura de cada "slot" de ativo
    altura_slot = area_util / qtd
    padding_slot = 40 # Espaço entre ativos (um pouco maior para respirar)

    for idx, item in enumerate(dados):
        # Coordenada Y inicial deste ativo
        y_inicial = margem_topo + (idx * altura_slot) + padding_slot
        
        # Título do Ativo (Ex: CDB - Banco Master) - Usa BOLD
        nome_exibicao = f"{item['tipo']} {item['subtipo']}" if item['subtipo'] else item['tipo']
        texto_titulo = f"{nome_exibicao} - {item['emissor']}"
        if item['rating']:
            texto_titulo += f" ({item['rating']})"
            
        draw.text((100, y_inicial), texto_titulo, font=font_titulo, fill=CORES['azul_claro'])
        
        # Destaque de Isenção (Regular para não brigar com o título)
        if item['isento']:
            # Calcula largura do titulo para posicionar a estrela ao lado
            w_text = draw.textlength(texto_titulo, font=font_titulo)
            draw.text((100 + w_text + 20, y_inicial + 10), "★ ISENTO IR", font=font_pequena, fill=CORES['verde_isento'])

        # Taxa (Grande destaque) - Usa BOLD
        draw.text((100, y_inicial + 80), item['taxa'], font=font_destaque, fill=CORES['dourado'])
        
        # Detalhes (Prazo, Minimo, Juros) - Usa REGULAR
        detalhes_y = y_inicial + 200
        texto_detalhes = f"📅 Prazo: {item['vencimento']}   |   💰 Mín: {item['minimo']}"
        draw.text((100, detalhes_y), texto_detalhes, font=font_texto, fill=CORES['texto_branco'])
        
        if item['juros'] != "No Vencimento":
            draw.text((100, detalhes_y + 60), f"🔄 Juros: {item['juros']}", font=font_pequena, fill=CORES['azul_claro'])

        # Linha divisória (se não for o último)
        if idx < qtd - 1:
            # Desenha linha fina para separar
            linha_y = y_inicial + altura_slot - (padding_slot / 2)
            draw.line([(150, linha_y), (W-150, linha_y)], fill=CORES['azul_medio'], width=2)

    return img

# --- 4. GERADOR DE TEXTO WHATSAPP ---
def gerar_texto_whatsapp(dados):
    texto_final = ""
    tem_garantia = False
    
    for item in dados:
        nome_ativo = f"{item['tipo']}"
        if item['subtipo']: nome_ativo += f" ({item['subtipo']})"
        
        texto_final += f"🏦 *Oportunidade de Renda Fixa - {nome_ativo}*\n"
        texto_final += f"📍 {item['emissor']}"
        if item['rating']: texto_final += f" ({item['rating']})"
        texto_final += "\n"
        
        texto_final += f"📈 *Rentabilidade:* {item['taxa']}\n"
        
        desc_isento = " (Isento de IR) ✅" if item['isento'] else ""
        texto_final += f"📅 Vencimento: {item['vencimento']}{desc_isento}\n"
        texto_final += f"💰 Aporte Mínimo: {item['minimo']}\n"
        
        if item['juros'] != "No Vencimento":
            texto_final += f"🔄 Pagamento de Juros: {item['juros']}\n"
            
        texto_final += "-----------------------------------\n"
        
        if item['tipo'] in ATIVOS_FGC:
            tem_garantia = True

    if tem_garantia:
        texto_final += "\n🔐 *Garantia:* Coberto pelo FGC (até R$ 250.000,00 por CPF/Instituição)."
        
    return texto_final

# --- 5. AÇÃO FINAL ---
st.divider()
col_btn, col_res = st.columns([1, 2])

with col_btn:
    gerar = st.button("✨ Gerar Card e Texto", type="primary")

if gerar:
    # 1. Gerar Imagem
    imagem_final = gerar_card_multiplo(dados_ativos, arquivo_template, formato)
    
    # 2. Gerar Texto
    texto_zap = gerar_texto_whatsapp(dados_ativos)
    
    # --- EXIBIÇÃO ---
    st.success("Conteúdo Gerado com Sucesso!")
    
    col_img, col_txt = st.columns(2)
    
    with col_img:
        st.image(imagem_final, caption=f"Formato: {formato}", use_container_width=True)
        
        # Botão Download Imagem
        buf = io.BytesIO()
        imagem_final.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="📥 Baixar Imagem",
            data=byte_im,
            file_name="card_renda_fixa.png",
            mime="image/png"
        )
        
    with col_txt:
        if plataforma == "WhatsApp":
            st.subheader("Texto para Copiar:")
            st.code(texto_zap, language=None)
            st.caption("Toque no ícone de copiar no canto superior direito do bloco acima.")
        else:
            st.info("Para o Instagram, use a imagem ao lado. O texto gerado abaixo pode ser usado na legenda.")
            st.code(texto_zap, language=None)
