import sys
import re
import os

def preProcessar(caminhoLivro):
    caminhoLivroPreProcessados = "PreProcessado"

    if not (os.path.isdir(caminhoLivroPreProcessados)):
        os.mkdir(caminhoLivroPreProcessados)

    # Executando shell para remover caracteres
    os.system("./removerCaracteresIndesejaveis.sh " + caminhoLivro)

    textoLivro = open(caminhoLivro).read()

    # Removendo enter no fim de cada linha
    textoLivro = re.sub(r'\n', r' ', textoLivro)

    # Removendo linha com numero do capitulo
    textoCapitulos = re.split('Chapter [0-9]+[ ]+', textoLivro)

    # Separando texto capitulos em arquivos
    count = 0
    for textoCapitulo in textoCapitulos:
        if count != 0:
            salvarArquivo(textoCapitulo, os.path.join(caminhoLivroPreProcessados, str(count)))
        count = count + 1

def salvarArquivo(texto, caminho):
    saida = open(caminho, 'w+')
    saida.write(texto)
    saida.close()
