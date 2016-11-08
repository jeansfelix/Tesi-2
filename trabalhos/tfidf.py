#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath

reload(sys)
sys.setdefaultencoding("utf-8")

stopWords = set(nltk.corpus.stopwords.words('english'))

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio PreProcessado."
        exit(1)

    diretorioTemporadas = sys.argv[1]
    executarProcessamento(diretorioTemporadas)


def executarProcessamento(diretorioTemporadas):
    temporadas = [t for t in listdir(diretorioTemporadas)]

    for temporada in sorted(temporadas):
        print 'Processando temporada: ' + temporada
        caminhoTemporada = join(diretorioTemporadas, temporada)

        caminhoEpisodios = join(caminhoTemporada, 'episodios')
        episodios = [e for e in listdir(caminhoEpisodios)]

        processarEpisodios(caminhoEpisodios, episodios)


def processarEpisodios(caminhoEpisodios, episodios):

    for episodio in episodios:
        arquivo = open(join(caminhoEpisodios, episodio))
        textoArquivo = arquivo.read();
        arquivo.close()

        palavras = [a for a in textoArquivo.lower().split() if a not in stopWords]

        print palavras


if __name__ == "__main__":
    main()
