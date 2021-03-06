#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re, math
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath

reload(sys)
sys.setdefaultencoding("utf-8")

def main():
    if len(sys.argv) != 3:
        print "Deve ser passado o nome do diretorio PreProcessado."
        exit(1)

    diretorioTemporadas = sys.argv[1]
    consulta = sys.argv[2]

    tfidf = executarProcessamento(diretorioTemporadas)

    resultado = ordenar(tfidf, consulta)

def truncate(f, n):
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def ordenar(tfidf, consulta):
    palavrasConsulta = consulta.lower().split()

    episodioValor = dict()
    for documento in tfidf.iterkeys():
        episodioValor[documento] = 0.0
        for palavraConsulta in palavrasConsulta:
            if palavraConsulta in tfidf[documento]:
                episodioValor[documento] += tfidf[documento][palavraConsulta]

    lista = sorted([str(truncate(episodioValor[a], 20)) + ' - ' + a for a in episodioValor.iterkeys()],  reverse=True)

    for cont in range(0,5):
        print lista[cont]



def executarProcessamento(diretorioTemporadas):
    temporadas = [t for t in listdir(diretorioTemporadas)]

    vezesQueUmaPalavraApareceEmUmDocumento = dict(dict())
    quantidadePalavrasPorDocumento = dict()
    for temporada in sorted(temporadas):
        caminhoTemporada = join(diretorioTemporadas, temporada)

        caminhoEpisodios = join(caminhoTemporada, 'episodios')
        episodios = [e for e in listdir(caminhoEpisodios)]

        mapas = processarEpisodios(caminhoEpisodios, episodios)

        for documento in mapas[0].iterkeys():
            vezesQueUmaPalavraApareceEmUmDocumento[documento] = mapas[0][documento]

        for documento in mapas[1].iterkeys():
            quantidadePalavrasPorDocumento[documento] = mapas[1][documento]

    numeroDeDocumentos = 0.0
    numeroDeDocumentosEmQueAPalavraAparece = dict()
    for documento in vezesQueUmaPalavraApareceEmUmDocumento.iterkeys():
        numeroDeDocumentos += 1.0
        for palavra in vezesQueUmaPalavraApareceEmUmDocumento[documento].iterkeys():
            if palavra in numeroDeDocumentosEmQueAPalavraAparece:
                numeroDeDocumentosEmQueAPalavraAparece[palavra] += 1.0
            else:
                numeroDeDocumentosEmQueAPalavraAparece[palavra] = 1.0

    #calculando tfidf
    tfidf = dict(dict())
    for documento in vezesQueUmaPalavraApareceEmUmDocumento.iterkeys():
        tfidfPalavra = dict()
        for palavra in vezesQueUmaPalavraApareceEmUmDocumento[documento].iterkeys():
            tf = vezesQueUmaPalavraApareceEmUmDocumento[documento][palavra] / quantidadePalavrasPorDocumento[documento]
            idf = math.log(numeroDeDocumentos/numeroDeDocumentosEmQueAPalavraAparece[palavra])
            tfidfPalavra[palavra] = tf * idf
        tfidf[documento] = tfidfPalavra

    return tfidf

def processarEpisodios(caminhoEpisodios, episodios):
    vezesQueUmaPalavraApareceEmUmDocumento = dict(dict())
    quantidadePalavrasPorDocumento = dict()
    for episodio in episodios:
        arquivo = open(join(caminhoEpisodios, episodio))
        textoArquivo = arquivo.read().decode('utf8');
        arquivo.close()

        stopWords = set(nltk.corpus.stopwords.words('english'))
        #print stopWords

        textoArquivo = re.sub(r'''[.,;:!?'"()&]''', r' ', textoArquivo)
        palavras = [a for a in textoArquivo.lower().split() if a not in stopWords]

        episodioFormatado = 'S' + caminhoEpisodios.split('/')[1].split('_')[1] + '_' + episodio.split('.txt')[0]
        quantidadePalavrasPorDocumento[episodioFormatado] = len(palavras)

        palavraAparicoes = dict()
        for palavra in palavras:
            if palavra in palavraAparicoes:
                palavraAparicoes[palavra] += 1.0
            else:
                palavraAparicoes[palavra] = 1.0

        vezesQueUmaPalavraApareceEmUmDocumento[episodioFormatado] = palavraAparicoes

    return vezesQueUmaPalavraApareceEmUmDocumento, quantidadePalavrasPorDocumento


if __name__ == "__main__":
    main()
