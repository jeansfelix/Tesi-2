#!/usr/bin/python
# -*- coding: utf-8 -*-
import preProcessamento
import sys, nltk, math, re, operator
from os import listdir
from os.path import join

#nltk.download('punkt')

reload(sys)
sys.setdefaultencoding("utf-8")
limitante = 0.001

class Sentenca:
    sentencaOriginal = ''
    sentencaMinuscula = ''
    capitulo = ''
    ordem = 0
    score = 0.0

    def __init__(self, sentencaOriginal, ordem, capitulo):
        self.sentencaOriginal = sentencaOriginal
        self.sentencaMinuscula = sentencaOriginal.lower()
        self.ordem = ordem
        self.capitulo = capitulo

    def __str__(self):
        return self.sentencaOriginal + ' ' + str(self.score)

    def __repr__(self):
        return self.sentencaOriginal + ' ' + str(self.score)

def main():
    if len(sys.argv) < 3:
        print 'Por favor, digite os argumentos desta forma: python sumarizador.py <caminhoLivro> <percentualResumo>'
        exit(1)

    preProcessamento.preProcessar(sys.argv[1])
    diretorioDocumentos = 'PreProcessado'
    executarProcessamento(diretorioDocumentos, sys.argv[2])

def executarProcessamento(diretorioDocumentos, percentualResumo):
    tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')

    documentos = [t for t in listdir(diretorioDocumentos)]
    documentos.sort(key=int)

    mapaPalavrasPorDocumento = dict()
    sentencasPorDocumento = dict()
    ordem = 0
    for documento in documentos:
        arquivo = open(join(diretorioDocumentos, documento))

        #Separando texto em sentenças
        sentencas = (tokenizador.tokenize(arquivo.read().decode('utf8')))
        arquivo.close()

        listaSentencas = list()
        for sentenca in sentencas:
            listaSentencas.append(Sentenca(sentenca.strip(), ordem, documento))
            ordem = ordem + 1

        arquivo = open(join(diretorioDocumentos, documento))
        textoDocumento = arquivo.read().decode('utf8');
        arquivo.close()

        sentencasPorDocumento[documento] = listaSentencas

        textoDocumento = re.sub(r'''[.,;:!?'"()&]''', r' ', textoDocumento)
        #Extraindo palavras do documento e transformando em minúsculas
        palavrasDoDocumento = nltk.word_tokenize(textoDocumento.lower())

        mapaPalavrasPorDocumento[documento] = palavrasDoDocumento

    #Calculando TF
    tfidf = criarTFIDF(mapaPalavrasPorDocumento)
    centroid = criarCentroid(tfidf)

    listaSentencas = list()
    for documento in sentencasPorDocumento.iterkeys():
        for sentenca in sentencasPorDocumento[documento]:
            sentenca.score = 0.0

            sentencaProcessada = re.sub(r'''[.,;:!?'"()&]''', r' ', sentenca.sentencaMinuscula)

            for palavra in nltk.word_tokenize(sentencaProcessada):
                sentenca.score += centroid[palavra]

            listaSentencas.append(sentenca)

    sentencasPorScore = sorted(listaSentencas, key=operator.attrgetter('score'))

    tam = len(sentencasPorScore)
    numeroSentencasDesprezadas = tam - int(tam * float(percentualResumo))
    sentencasComMaiorScore = sentencasPorScore[numeroSentencasDesprezadas:]

    arquivoResumo = open('resumo.txt', 'w+')

    print 'Quantidade de sentenças no livro: ' + str(tam)
    print 'Quantidade de sentenças extraídas: ' + str(tam - numeroSentencasDesprezadas)

    capitulo = ''
    resumo = ''
    for sentenca in sorted(sentencasComMaiorScore, key=operator.attrgetter('ordem')):
        if str(capitulo) != str(sentenca.capitulo):
            resumo += '\nCapitulo ' + sentenca.capitulo + '\n'
            capitulo = sentenca.capitulo
        resumo += sentenca.sentencaOriginal + '\n'

    arquivoResumo.write(resumo)
    arquivoResumo.close()


def criarTFIDF(mapaPalavrasPorDocumento):
    numDocumentos = len(mapaPalavrasPorDocumento.keys())

    palavrasEmTodosDocumentos = list()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        palavrasEmTodosDocumentos += mapaPalavrasPorDocumento[documento]

    tf = dict()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        for palavra in mapaPalavrasPorDocumento[documento]:
            if palavra in tf:
                tf[palavra] += 1.0
            else:
                tf[palavra] = 1.0

    #Calculando IDF de cada palavra

    #Removendo duplicações.
    palavrasEmTodosDocumentos = list(set(palavrasEmTodosDocumentos))

    numeroDeDocumentosEmQuePalavraAparece = dict()
    for palavra in palavrasEmTodosDocumentos:
        for documento in mapaPalavrasPorDocumento.iterkeys():
            if palavra in mapaPalavrasPorDocumento[documento]:
                if palavra in numeroDeDocumentosEmQuePalavraAparece:
                    numeroDeDocumentosEmQuePalavraAparece[palavra] += 1.0
                else:
                    numeroDeDocumentosEmQuePalavraAparece[palavra] = 1.0

    idf = dict()
    for palavra in palavrasEmTodosDocumentos:
        idf[palavra] = math.log(numDocumentos / numeroDeDocumentosEmQuePalavraAparece[palavra])

    for palavra in tf.iterkeys():
        tf[palavra] = tf[palavra] / len(palavrasEmTodosDocumentos)

    #Calculando TF-IDF
    tfidf = dict()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        for palavra in palavrasEmTodosDocumentos:
            if palavra not in tf:
                tfidf[palavra] = 0.0
            else:
                tfidf[palavra] = tf[palavra] * idf[palavra]

    return tfidf

def criarCentroid(tfidf):
    centroid = dict()
    for palavra in tfidf.iterkeys():
        if tfidf[palavra] > limitante:
            centroid[palavra] = tfidf[palavra]
        else:
            centroid[palavra] = 0.0
    return centroid


def salvarArquivo(texto, caminho):
    saida = open(caminho, 'w+')
    saida.write(texto)
    saida.close()

if __name__ == "__main__":
    main()
