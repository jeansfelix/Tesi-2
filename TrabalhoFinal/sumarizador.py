#!/usr/bin/python
# -*- coding: utf-8 -*-
import preProcessamento
import sys, nltk, math, re, operator, collections
from os import listdir
from os.path import join

reload(sys)
sys.setdefaultencoding("utf-8")

# Importando biblioteca do nltk
nltk.download('punkt')

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

    print 'Extraindo Sentenças...'
    diretorioDocumentos = 'PreProcessado'
    executarProcessamento(diretorioDocumentos, sys.argv[2])

def executarProcessamento(diretorioDocumentos, percentualResumo):
    tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')

    # recuperando arquivos com texto dos capitulos
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

        # Criando objetos Sentenca com o valor da sentença, ordem e numero do capitulo
        listaSentencas = list()
        for sentenca in sentencas:
            listaSentencas.append(Sentenca(sentenca.strip(), ordem, documento))
            ordem = ordem + 1

        arquivo = open(join(diretorioDocumentos, documento))
        textoDocumento = arquivo.read().decode('utf8');
        arquivo.close()

        # Guardando as sentenças de cada capitulo
        sentencasPorDocumento[documento] = listaSentencas

        #Extraindo palavras do documento e transformando em minúsculas
        textoDocumento = re.sub(r'''[.,;:!?'"()&]''', r' ', textoDocumento)
        palavrasDoDocumento = nltk.word_tokenize(textoDocumento.lower())

        mapaPalavrasPorDocumento[documento] = palavrasDoDocumento

    #Calculando TF
    tfidf = criarTFIDF(mapaPalavrasPorDocumento)


    # Calculando totais de palavras e palavras desprezadas
    total = 0.0
    count = 0
    totalPalavras = 0
    for palavra in tfidf.iterkeys():
        totalPalavras += 1
        if tfidf[palavra] > 0.001:
            total += tfidf[palavra]
            count += 1

    global limitante
    limitante = total / count

    print 'Limitante:' + str(limitante)
    print 'Total Palavras:' + str(count)

    # Gerando centroide da
    centroide = criarCentroide(tfidf)


    # Calculando o score de cada sentença
    listaSentencas = list()
    numeroSentencasCapitulo = dict()
    for documento in sentencasPorDocumento.iterkeys():
        numeroSentencas = 0
        for sentenca in sentencasPorDocumento[documento]:
            sentenca.score = 0.0
            sentencaProcessada = re.sub(r'''[.,;:!?'"()&]''', r' ', sentenca.sentencaMinuscula)

            for palavra in nltk.word_tokenize(sentencaProcessada):
                sentenca.score += centroide[palavra]

            listaSentencas.append(sentenca)
            numeroSentencas += 1
        numeroSentencasCapitulo[documento] = numeroSentencas

    # Ordenando sentencas por score
    sentencasPorScore = sorted(listaSentencas, key=operator.attrgetter('score'))

    # Extraindo o percentual de sentencas requisitado
    tam = len(sentencasPorScore)
    numeroSentencasDesprezadas = tam - int(tam * float(percentualResumo))
    sentencasComMaiorScore = sentencasPorScore[numeroSentencasDesprezadas:]

    arquivoResumo = open('resumo.txt', 'w+')

    print 'Quantidade de sentenças no livro: ' + str(tam)
    print 'Quantidade de sentenças extraídas: ' + str(tam - numeroSentencasDesprezadas)

    capitulo = ''
    resumo = ''
    mapaNumeroSentencasResumoCapitulo = dict()
    for sentenca in sorted(sentencasComMaiorScore, key=operator.attrgetter('ordem')):
        if str(capitulo) != str(sentenca.capitulo):
	    if capitulo != '':
                mapaNumeroSentencasResumoCapitulo[capitulo] = numeroSentencas
            numeroSentencas = 0
            resumo += '\nCapitulo ' + sentenca.capitulo + '\n'
            capitulo = sentenca.capitulo
        resumo += sentenca.sentencaOriginal + '\n'
        numeroSentencas += 1

    mapaNumeroSentencasResumoCapitulo[capitulo] = numeroSentencas

    arquivoResumo.write(resumo)
    arquivoResumo.close()
    print 'Percentual de resumo dos capítulos'
    listaChaves = mapaNumeroSentencasResumoCapitulo.keys()
    listaChaves.sort(key=int)
    for capitulo in listaChaves:
        print 'Capitulo ' + str(capitulo) + ' ' + str(float(mapaNumeroSentencasResumoCapitulo[capitulo]) / float(numeroSentencasCapitulo[capitulo]))


def criarTFIDF(mapaPalavrasPorDocumento):
    numDocumentos = len(mapaPalavrasPorDocumento.keys())

    palavrasEmTodosDocumentos = list()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        palavrasEmTodosDocumentos += mapaPalavrasPorDocumento[documento]

    # Calculando tf de cada palavra
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
        tf[palavra] = tf[palavra] / float(len(palavrasEmTodosDocumentos))

    #Calculando TF-IDF
    tfidf = dict()
    for documento in mapaPalavrasPorDocumento.iterkeys():
        for palavra in palavrasEmTodosDocumentos:
            if palavra not in tf:
                tfidf[palavra] = 0.0
            else:
                tfidf[palavra] = tf[palavra] * idf[palavra]

    return tfidf

def criarCentroide(tfidf):
    centroid = dict()
    count = 0
    for palavra in tfidf.iterkeys():
        if tfidf[palavra] > limitante:
            centroid[palavra] = tfidf[palavra]
            count +=1
        else:
            centroid[palavra] = 0.0

    print 'Palavras > limitante: ' + str(count)

    return centroid


def salvarArquivo(texto, caminho):
    saida = open(caminho, 'w+')
    saida.write(texto)
    saida.close()

if __name__ == "__main__":
    main()
