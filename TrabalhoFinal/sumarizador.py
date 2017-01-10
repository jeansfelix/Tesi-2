#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re, math
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath

reload(sys)
sys.setdefaultencoding("utf-8")

def main():
    diretorioDocumentos = sys.argv[1]
    executarProcessamento(diretorioDocumentos)

def executarProcessamento(diretorioDocumentos):
    documentos = [t for t in listdir(diretorioDocumentos)]

    numDocumentos = len(documentos)
   
    palavrasPresentesEmDocumento = dict()

    for documento in documentos:
        arquivo = open(join(diretorioDocumentos, documento))
        textoDocumento = arquivo.read().decode('utf8');
        arquivo.close()
      
        #Removendo pontuação
        textoDocumento = re.sub(r'''[.,;:!?'"()&]''', r' ', textoDocumento)
        
        #Extraindo palavras do documento e transformando em minúsculas        
        palavrasDoDocumento = textoDocumento.lower().split()

        palavrasPresentesEmDocumento[documento] = palavrasDoDocumento
        
    palavrasEmTodosDocumentos = list()
    for documento in palavrasPresentesEmDocumento.iterkeys():
        palavrasEmTodosDocumentos += palavrasPresentesEmDocumento[documento]
        
    #Calculando TF
    tf = dict(dict())
    for documento in documentos:
        tfDocumento = dict()
        for palavra in palavrasPresentesEmDocumento[documento]:
            if palavra in tfDocumento:
                tfDocumento[palavra] += 1.0
            else:
                tfDocumento[palavra] = 1.0
        
        for palavra in palavrasPresentesEmDocumento[documento]:
            tfDocumento[palavra] = tfDocumento[palavra]
                
        tf[documento] = tfDocumento
    
    #Calculando IDF de cada palavra
    
    #Removendo duplicações.
    palavrasEmTodosDocumentos = list(set(palavrasEmTodosDocumentos))
    
    numeroDeDocumentosEmQuePalavraAparece = dict()
    for palavra in palavrasEmTodosDocumentos:
        for documento in palavrasPresentesEmDocumento.iterkeys(): 
            if palavra in palavrasPresentesEmDocumento[documento]:
                if palavra in numeroDeDocumentosEmQuePalavraAparece:
                    numeroDeDocumentosEmQuePalavraAparece[palavra] += 1.0
                else:
                    numeroDeDocumentosEmQuePalavraAparece[palavra] = 1.0
    
    idf = dict()
    for palavra in palavrasEmTodosDocumentos:
        idf[palavra] = math.log(numDocumentos / numeroDeDocumentosEmQuePalavraAparece[palavra])
    

    #Calculando TF-IDF
    tfidf = dict(dict())
    for documento in documentos:
        tfidfDocumento = dict()
        for palavra in palavrasEmTodosDocumentos:
            if palavra not in tf[documento]:
                tfidfDocumento[palavra] = 0
            else:
                tfidfDocumento[palavra] = tf[documento][palavra] * idf[palavra]
        tfidf[documento] = tfidfDocumento
        
    print tfidf['the_wolf_and_the_lion.txt']['princess']
            
if __name__ == "__main__":
    main()

