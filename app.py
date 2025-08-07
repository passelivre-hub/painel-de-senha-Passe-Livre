from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from gtts import gTTS
import os

app = Flask(__name__, static_url_path="/static")
CORS(app)

senha_atual = 0
guiche_atual = ""
historico_chamadas = []
repetir_audio = False  # controla pedido de repetição

@app.route("/")
def painel():
    return render_template("painel.html")

@app.route("/atendente")
def atendente():
    return render_template("atendente.html")

@app.route("/historico")
def historico():
    return render_template("historico.html", chamadas=reversed(historico_chamadas[-10:]))

@app.route("/dados_painel")
def dados_painel():
    return jsonify({
        "senha": str(senha_atual).zfill(3),
        "guiche": guiche_atual
    })

@app.route("/chamar_senha", methods=["POST"])
def chamar_senha():
    global senha_atual, guiche_atual, repetir_audio

    senha = request.form.get("senha")
    guiche = request.form.get("guiche")

    if not guiche:
        return jsonify({"erro": "Guichê é obrigatório"}), 400

    if senha:
        senha_atual = int(senha)
    else:
        senha_atual += 1

    guiche_atual = guiche
    senha_formatada = str(senha_atual).zfill(3)

    # Caminho para o áudio
    audio_path = os.path.join("static", "audios", f"senha_{senha_formatada}_guiche_{guiche_atual}.mp3")

    if not os.path.exists(audio_path):
        texto = f"Senha número {senha_atual}, dirija-se à mesa {guiche_atual}"
        try:
            tts = gTTS(text=texto, lang="pt-br")
            tts.save(audio_path)
        except Exception as e:
            return jsonify({"erro": f"Erro ao gerar áudio: {e}"}), 500

    historico_chamadas.append({"senha": senha_formatada, "guiche": guiche_atual})
    repetir_audio = True

    return jsonify({
        "mensagem": "Senha chamada com sucesso",
        "senha": senha_formatada
    })

@app.route("/repetir_som", methods=["POST"])
def repetir_som():
    global repetir_audio
    repetir_audio = True
    return jsonify({"mensagem": "Pedido de repetição enviado"})

@app.route("/verificar_repeticao")
def verificar_repeticao():
    global repetir_audio
    if repetir_audio:
        repetir_audio = False
        return jsonify({"repetir": True})
    return jsonify({"repetir": False})

if __name__ == "__main__":
    os.makedirs("static/audios", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))  # compatível com Render
    app.run(debug=True, host="0.0.0.0", port=port)
