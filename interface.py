import os
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import speech_recognition as sr
import openai

# 🔑 Configuração da API do OpenAI (Substitua com sua chave)
openai.api_key = ''

# 📂 Escolher pasta de destino
def escolher_pasta():
    pasta = filedialog.askdirectory()
    entrada_pasta.delete(0, tk.END)
    entrada_pasta.insert(0, pasta)

# 🔤 Função para limpar nomes de arquivos (remover caracteres inválidos)
def limpar_nome_arquivo(nome_arquivo):
    caracteres_invalidos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for caractere in caracteres_invalidos:
        nome_arquivo = nome_arquivo.replace(caractere, "_")
    return nome_arquivo

# ⬇️ Função para baixar vídeo/áudio
def baixar_video():
    link = entrada_link.get()
    pasta_destino = entrada_pasta.get()
    opcao = formato_var.get()

    if not link or not pasta_destino:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos!")
        return

    try:
        # Configurações do yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best' if opcao == "MP3" else 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ffmpeg_location': r'c:\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe'
        }

        # Inicia o download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        # Inicializa a variável antes do loop
        arquivo_limpo = None

        # Ajusta o nome do arquivo para evitar caracteres inválidos
        for arquivo in os.listdir(pasta_destino):
            if arquivo.endswith('.mp3') or arquivo.endswith('.mp4'):
                arquivo_limpo = limpar_nome_arquivo(arquivo)
                caminho_original = os.path.join(pasta_destino, arquivo)
                caminho_limpo = os.path.join(pasta_destino, arquivo_limpo)
                os.rename(caminho_original, caminho_limpo)

        # Verifica se um arquivo válido foi encontrado
        if arquivo_limpo and opcao == "MP3":
            arquivo_mp3 = os.path.join(pasta_destino, arquivo_limpo)
            transcricao = transcrever_audio(arquivo_mp3)

            if transcricao and transcricao.strip():
                resumo = gerar_resumo(transcricao)

                # Salvar resumo em um arquivo .txt
                resumo_path = os.path.join(pasta_destino, arquivo_limpo.replace(".mp3", "_resumo.txt"))
                with open(resumo_path, "w", encoding="utf-8") as resumo_file:
                    resumo_file.write(resumo)

        # Mensagem de sucesso
        messagebox.showinfo("Sucesso", "Download e resumo concluídos com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# 🎙️ Função para transcrever o áudio
def transcrever_audio(arquivo_audio):
    r = sr.Recognizer()
    with sr.AudioFile(arquivo_audio) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="pt-BR")
    except sr.UnknownValueError:
        return "Não foi possível entender o áudio."
    except sr.RequestError as e:
        return f"Erro ao solicitar transcrição: {e}"

# 🧠 Função para gerar resumo com OpenAI
def gerar_resumo(texto):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Resuma o seguinte texto:\n\n{texto}",
        max_tokens=200
    )
    return response.choices[0].text.strip()

# 🎨 Configurações visuais (Modo Escuro)
COR_FUNDO = "#121212"
COR_TEXTO = "white"
COR_BOTAO = "#1DB954"
COR_BOTAO_TEXTO = "black"

# 📌 Criar interface gráfica
janela = tk.Tk()
janela.title("YouTube Downloader + Resumo AI")
janela.geometry("500x500")
janela.resizable(False, False)
janela.configure(bg=COR_FUNDO)

# 🏷️ Título
titulo = tk.Label(janela, text="YouTube Downloader + IA", font=("Arial", 16, "bold"), bg=COR_FUNDO, fg=COR_TEXTO)
titulo.pack(pady=10)

# 🌐 Campo do link
tk.Label(janela, text="Link do vídeo:", font=("Arial", 12), bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=5)
entrada_link = tk.Entry(janela, width=60, bg="#333", fg=COR_TEXTO, insertbackground=COR_TEXTO)
entrada_link.pack(pady=5)

# 📂 Escolher pasta
tk.Label(janela, text="Pasta de destino:", font=("Arial", 12), bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=5)
frame_pasta = tk.Frame(janela, bg=COR_FUNDO)
frame_pasta.pack(pady=5)
entrada_pasta = tk.Entry(frame_pasta, width=45, bg="#333", fg=COR_TEXTO, insertbackground=COR_TEXTO)
entrada_pasta.pack(side=tk.LEFT, padx=5)
tk.Button(frame_pasta, text="Escolher", command=escolher_pasta, bg=COR_BOTAO, fg=COR_BOTAO_TEXTO).pack(side=tk.RIGHT, padx=5)

# 🎥 Escolher formato
tk.Label(janela, text="Escolha o formato:", font=("Arial", 12), bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=5)
formato_var = tk.StringVar(value="MP4")
frame_formatos = tk.Frame(janela, bg=COR_FUNDO)
frame_formatos.pack()
tk.Radiobutton(frame_formatos, text="MP4 (Vídeo)", variable=formato_var, value="MP4", font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO, selectcolor=COR_FUNDO).pack(side=tk.LEFT, padx=10)
tk.Radiobutton(frame_formatos, text="MP3 (Áudio)", variable=formato_var, value="MP3", font=("Arial", 11), bg=COR_FUNDO, fg=COR_TEXTO, selectcolor=COR_FUNDO).pack(side=tk.LEFT, padx=10)

# ⬇️ Botão de download
btn_baixar = tk.Button(janela, text="Baixar", command=baixar_video, font=("Arial", 12, "bold"), bg=COR_BOTAO, fg=COR_BOTAO_TEXTO, width=15)
btn_baixar.pack(pady=20)

# 🏁 Iniciar GUI
janela.mainloop()
