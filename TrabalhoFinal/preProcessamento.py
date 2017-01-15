import sys
import re
import os

def preProcessar(caminhoLivro):
    caminhoLivroPreProcessados = "PreProcessado"

    # Executando shell para remover caracteres
    os.system("./removerCaracteresIndesejaveis.sh " + caminhoLivro)

    if not (os.path.isdir(caminhoLivroPreProcessados)):
        os.mkdir(caminhoLivroPreProcessados)

    textoLivro = open(caminhoLivro).read()

    textoLivro = re.sub(r'\n', r' ', textoLivro)
    textoCapitulos = re.split('Chapter [0-9]+[ ]+', textoLivro)

    count = 0
    for textoCapitulo in textoCapitulos:
        if count != 0:
            salvarArquivo(textoCapitulo, os.path.join(caminhoLivroPreProcessados, str(count)))
        count = count + 1

    print "Terminou!"

def salvarArquivo(texto, caminho):
    saida = open(caminho, 'w+')
    saida.write(texto)
    saida.close()

def criarPasta(caminho):
    if not (os.path.isdir(caminho)):
        os.mkdir(caminho)
