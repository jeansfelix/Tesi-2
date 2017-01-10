#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re, math
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath

nltk.download('punkt')

reload(sys)
sys.setdefaultencoding("utf-8")
limitante = 0.001

class Sentenca:
    sentencaOriginal = ''
    sentencaMinuscula = ''
    score = 0.0

    def __init__(self, sentencaOriginal):
        self.sentencaOriginal = sentencaOriginal
        self.sentencaMinuscula = sentencaOriginal.lower()
    
    def __str__(self):
        return self.sentencaOriginal + ' ' + str(self.score)
        
    def __repr__(self):
        return self.sentencaOriginal + ' ' + str(self.score)
        
def main():
    diretorioDocumentos = sys.argv[1]
    executarProcessamento(diretorioDocumentos)

def executarProcessamento(diretorioDocumentos):
    tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')

    documentos = [t for t in listdir(diretorioDocumentos)]

    mapaPalavrasPorDocumento = dict()

    sentencasPorDocumento = dict()
    
    for documento in documentos:
        arquivo = open(join(diretorioDocumentos, documento))

        #Separando texto em sentenças
        sentencas = list()
        for linha in arquivo:
            sentencas += (tokenizador.tokenize(linha.decode('utf8')))
        arquivo.close()

        listaSentencas = list()
        for sentenca in sentencas:
            listaSentencas.append(Sentenca(sentenca.strip()))

        arquivo = open(join(diretorioDocumentos, documento))
        textoDocumento = arquivo.read().decode('utf8');
        arquivo.close()

        sentencasPorDocumento[documento] = listaSentencas
        
        textoDocumento = re.sub(r'''[.,;:!?'"()&]''', r' ', textoDocumento)
        #Extraindo palavras do documento e transformando em minúsculas        
        palavrasDoDocumento = textoDocumento.lower().split()

        mapaPalavrasPorDocumento[documento] = palavrasDoDocumento
        
    #Calculando TF
    tfidf = criarTFIDF(mapaPalavrasPorDocumento)
    centroid = criarCentroid(tfidf)
    
    for sentenca in listaSentencas:
        sentenca.score = 0.0

        sentencaProcessada = re.sub(r'''[.,;:!?'"()&]''', r' ', sentenca.sentencaMinuscula)

        for palavra in nltk.word_tokenize(sentencaProcessada):
            sentenca.score += centroid[palavra]
    

def criarTFIDF(mapaPalavrasPorDocumento):
    numDocumentos = len(mapaPalavrasPorDocumento.keys())

    palavrasEmTodosDocumentos = list()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        palavrasEmTodosDocumentos += mapaPalavrasPorDocumento[documento]

    tf = dict(dict())
    for documento in mapaPalavrasPorDocumento.iterkeys():
        tfDocumento = dict()
        for palavra in mapaPalavrasPorDocumento[documento]:
            if palavra in tfDocumento:
                tfDocumento[palavra] += 1.0
            else:
                tfDocumento[palavra] = 1.0
        
        tf[documento] = tfDocumento
    
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

    tfCluster = dict()
    for documento in tf.iterkeys():
        for palavra in tf[documento]:
            if palavra in tfCluster:
                tfCluster[palavra] += tf[documento][palavra]
            else:
                tfCluster[palavra] = tf[documento][palavra]

    for palavra in tfCluster.iterkeys():
        tfCluster[palavra] = tfCluster[palavra] / len(palavrasEmTodosDocumentos)

    #Calculando TF-IDF
    tfidf = dict()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        for palavra in palavrasEmTodosDocumentos:
            if palavra not in tfCluster:
                tfidf[palavra] = 0.0
            else:
                tfidf[palavra] = tfCluster[palavra] * idf[palavra]

    return tfidf

def criarCentroid(tfidf):

    centroid = dict()
    for palavra in tfidf.iterkeys():
        if tfidf[palavra] > limitante:
            centroid[palavra] = tfidf[palavra]
        else:
            centroid[palavra] = 0.0
    return centroid
    
if __name__ == "__main__":
    main()

