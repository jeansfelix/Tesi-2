#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import os

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretório."
        exit(1)

    diretorioPai = os.path.abspath(os.path.join(sys.argv[1], os.pardir))

    caminhoEpisodios = sys.argv[1]
    caminhoEpisodiosPreProcessados = os.path.join(diretorioPai, "PreProcessado")

    if not (os.path.isdir(caminhoEpisodiosPreProcessados)):
        os.mkdir(caminhoEpisodiosPreProcessados)

    temporadas = [a for a in os.listdir(caminhoEpisodios)]

    for temporada in temporadas:
        episodios = [a for a in os.listdir(os.path.join(caminhoEpisodios, temporada))]

        criarPasta(os.path.join(caminhoEpisodiosPreProcessados, temporada))

        for episodio in episodios:
            textoEpisodio = open(os.path.join(os.path.join(caminhoEpisodios, temporada),episodio))
            textoLimpo = limpaTexto(textoEpisodio.read())
            caminhoTextoLimpo = os.path.join(os.path.join(caminhoEpisodiosPreProcessados, temporada), episodio)
            saida = open(caminhoTextoLimpo, 'w+')
            saida.write(textoLimpo)

def limpaTexto(texto):
    try:
        inicioTrecho = re.search(r"(Summary[ ]?|Synopsis[ ]?)(Edit)?", texto).start()
        fimTrecho = re.search(r"Marketing|Image|Gallery|\Z", texto).start()
        trecho = texto[inicioTrecho:fimTrecho]
    except Exception as e:
        return ''

    trecho = re.sub(r"Summary\n", r'', trecho)
    trecho = re.sub(r"Deaths\n", r'', trecho)
    trecho = re.sub(r"Appearances\n", r'', trecho)
    trecho = re.sub(r"Cast\n", r'', trecho)
    trecho = re.sub(r"First\n", r'', trecho)
    trecho = re.sub(r"Recap\n", r'', trecho)
    trecho = re.sub(r"Stunt performers\n", r'', trecho)
    trecho = re.sub(r"Cast notes\n", r'', trecho)
    trecho = re.sub(r"Notes\n", r'', trecho)
    trecho = re.sub(r"In the books\n", r'', trecho)
    trecho = re.sub(r"Memorable quotes\n", r'', trecho)
    trecho = re.sub(r"Episode commentary\n", r'', trecho)
    trecho = re.sub(r"[/\\]", r' ', trecho)
    trecho = re.sub(r"[\[\]]", r'', trecho)

    trecho = re.sub(r"(\n.*)?([A-Z][a-z]*[ ]?)?Edit\n", r'', trecho)
    trecho = re.sub(r"(\n.*)?([A-Z][a-z]*[ ]?)?([Uu]ncredited\n.*)", r'', trecho)
    textoProcessado = re.sub(r"(\n.*)?([A-Z][a-z]*[ ]?)?([Ss]tarring\n.*)", r'', trecho)

    return textoProcessado

def criarPasta(caminho):
    if not (os.path.isdir(caminho)):
        os.mkdir(caminho)

if __name__ == "__main__":
    main()
