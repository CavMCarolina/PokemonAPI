from flask import Flask, request, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import os, requests

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a aplicação Flask
app = Flask(__name__)

# Configura a chave da API Gemini a partir da variável de ambiente
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Função para buscar dados de um Pokémon na PokeAPI
def get_pokemon_data(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    try:
        # Faz a requisição para a API
        r = requests.get(url, timeout=8)
        r.raise_for_status()  # Lança erro se status não for 200
        return r.json()       # Retorna os dados em formato JSON
    except requests.RequestException:
        # Se houver erro na requisição, retorna None
        return None

# Função para perguntar ao modelo Gemini
def ask_llm(pergunta, contexto=""):
    try:
        # Cria o modelo generativo Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")
        # Gera conteúdo com instruções específicas
        resp = model.generate_content(
            f"Você é um assistente especialista em Pokémon. "
            f"Responda em HTML formatado (use <ul>, <li>, <b>, <p>) sem Markdown.\n\n"
            f"Pergunta: {pergunta}\nContexto: {contexto}"
        )
        return resp.text  # Retorna o texto gerado pelo modelo
    except Exception as e:
        # Caso ocorra erro na chamada da API Gemini
        print("Erro na chamada Gemini:", e)
        return "Não consegui gerar a resposta agora. Tente novamente."

# Rota principal do site
@app.route("/", methods=["GET", "POST"])
def index():
    resposta = None
    if request.method == "POST":
        # Pega a pergunta enviada pelo formulário
        pergunta = request.form.get("pergunta", "").strip()
        if pergunta:
            # Verifica se a pergunta contém algum dos Pokémon pré-definidos
            alvo = next((name for name in ["pikachu","bulbasaur","charmander"] if name in pergunta.lower()), None)
            # Busca dados do Pokémon se encontrado
            dados = get_pokemon_data(alvo) if alvo else None
            # Cria contexto com os dados do Pokémon
            contexto = f"Dados: {dados}" if dados else ""
            # Pergunta ao modelo Gemini usando a pergunta e o contexto
            resposta = ask_llm(pergunta, contexto)
    # Renderiza o template HTML passando a resposta
    return render_template("index.html", resposta=resposta)

# Executa a aplicação Flask 
if __name__ == "__main__":
    app.run(debug=True)
