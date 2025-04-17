# API para converter arquivos OGG em MP3 (versão completa)

from flask import Flask, request, send_file, jsonify
from pydub import AudioSegment
import os
import uuid
import shutil

app = Flask(__name__)

# Pasta temporária para uploads
UPLOAD_FOLDER = 'uploads_temp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Extensões permitidas
EXTENSOES_PERMITIDAS = {'ogg'}

# Função para verificar extensão
def extensao_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

# Rota para converter OGG em MP3
@app.route('/converter', methods=['POST'])
def converter_ogg_para_mp3():
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado.'}), 400

    arquivo = request.files['arquivo']

    if arquivo.filename == '':
        return jsonify({'erro': 'Nome de arquivo inválido.'}), 400

    if not extensao_permitida(arquivo.filename):
        return jsonify({'erro': 'Extensão de arquivo não permitida.'}), 400

    try:
        # Gerar nomes únicos
        id_unico = str(uuid.uuid4())
        caminho_ogg = os.path.join(UPLOAD_FOLDER, f'{id_unico}.ogg')
        caminho_mp3 = os.path.join(UPLOAD_FOLDER, f'{id_unico}.mp3')

        # Salvar o arquivo OGG
        arquivo.save(caminho_ogg)

        # Converter OGG para MP3
        audio = AudioSegment.from_ogg(caminho_ogg)
        audio.export(caminho_mp3, format='mp3')

        # Apagar o arquivo OGG temporário
        os.remove(caminho_ogg)

        # Enviar o arquivo MP3 convertido
        resposta = send_file(caminho_mp3, as_attachment=True, download_name='audio_convertido.mp3')

        # Agendar exclusão do arquivo após envio (em segundo plano se quiser depois otimizar)
        @resposta.call_on_close
        def limpar_arquivos():
            if os.path.exists(caminho_mp3):
                os.remove(caminho_mp3)

        return resposta

    except Exception as e:
        return jsonify({'erro': f'Ocorreu um erro na conversão: {str(e)}'}), 500

# Endpoint de health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
