#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath

reload(sys)
sys.setdefaultencoding("utf-8")

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

    mapa_tf_episodioNumPalavras = dict()
    for episodio in episodios:
        arquivo = open(join(caminhoEpisodios, episodio))
        textoArquivo = arquivo.read().decode('utf8');
        arquivo.close()

        stopWords = set(nltk.corpus.stopwords.words('english'))
        #print stopWords

        textoArquivo = re.sub(r'''[.,;:!?'"()]''', r' ', textoArquivo)
        palavras = [a for a in textoArquivo.lower().split() if a not in stopWords]
        n_palavrasDistintas = len(set(palavras))

        print n_palavrasDistintas

        tf = dict()
        for palavra in palavras:
            if palavra in tf:
                tf[palavra] += 1.0
            else:
                tf[palavra] = 1.0

        mapa_tf_episodioNumPalavras[episodio] = [tf, n_palavrasDistintas];

    palavrasDistintas = []
    for episodio in mapa_tf_episodioNumPalavras.iterkeys():
        palavrasDistintas += mapa_tf_episodioNumPalavras[episodio][0].iterkeys()

    palavrasDistintas = set(palavrasDistintas)

    mapaNumAparicoesDaPalavra = dict()
    for palavra in palavrasDistintas:
        for episodio in mapa_tf_episodioNumPalavras.iterkeys():
            if palavra in mapa_tf_episodioNumPalavras[episodio][0].iterkeys():
                if palavra in mapaNumAparicoesDaPalavra:
                    mapaNumAparicoesDaPalavra[palavra] += mapa_tf_episodioNumPalavras[episodio][0][palavra]
                else:
                    mapaNumAparicoesDaPalavra[palavra] = 1.0

    print mapaNumAparicoesDaPalavra

if __name__ == "__main__":
    main()
