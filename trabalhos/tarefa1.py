#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs
from os import listdir, makedirs
from os.path import isfile, join, basename, exists

reload(sys)
sys.setdefaultencoding("utf-8")

print 'Number of arguments:', len(sys.argv), 'arguments.'

if len(sys.argv) != 2:
    print "Deve ser passado o nome do arquivo."
    exit(1)

path = sys.argv[1];
arquivos = [a for a in listdir(path) if isfile(join(path, a))]

print 'Procurando Entidades Nomeadas...'

pathDestino = basename(path)

if not exists(pathDestino):
    makedirs(pathDestino)

todasEntidadesNomeadas = []
pathCsvEntidadesNomeadas = 'entidadesNomeadas_' + pathDestino + '.txt'
csvEntidadesNomeadas = open(join(pathDestino,pathCsvEntidadesNomeadas), 'w+')

for pathArq in arquivos:
    arquivo = open(join(path, pathArq))

    print  'Processando arquivo ' + join(path, pathArq)

    stringLida = arquivo.read()

    saida = open(join(pathDestino, pathArq.replace(".txt", "_ARQUIVO-GERADO.txt")), 'w+')

    saida.write('Texto do Artigo:\n')
    saida.write(stringLida)

    tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')
    stringLida = stringLida.encode(encoding='U7', errors='strict')

    sentencas = []
    listaLinhas = [x for x in stringLida.split('\n') if x]
    for linha in listaLinhas:
        sentencasLinha = tokenizador.tokenize(linha)
        for sentencaLinha in sentencasLinha:
            sentencas.append(sentencaLinha)

    saida.write("\n\nSentencas:\n['")
    for sentenca in sentencas:
        saida.write(sentenca + "', '")
    saida.write(']')

    palavras = []
    for sentenca in sentencas:
        palavras.append(nltk.word_tokenize(sentenca))

    saida.write("\n\nEntidades Nomeadas:\n")

    for palavra in palavras:
        taggeado = nltk.pos_tag(palavra)

        gramatica = "NNPS: {<NNP>*}"
        agrupador = nltk.RegexpParser(gramatica)
        pedregulho = agrupador.parse(taggeado)

        entidadesNomeadas = []
        for pedra in pedregulho:
            if type(pedra) is nltk.Tree:
                entidadeNomeada = ''
                for no in pedra.leaves():
                    if len(entidadeNomeada) > 2:
                        entidadeNomeada += ' ' + no[0]
                    else:
                        entidadeNomeada = no[0]
                if len(entidadeNomeada) != 0:
                    entidadesNomeadas.append(entidadeNomeada)

        if len(entidadesNomeadas) != 0:
            saida.write('[')
            cont = 0
            for entidadeNomeada in entidadesNomeadas:
                if cont > 0:
                    saida.write(", '"+ entidadeNomeada + "'")
                else:
                    saida.write("'"+ entidadeNomeada + "'")
                cont += 1
            saida.write(']\n')

        todasEntidadesNomeadas += entidadesNomeadas

    saida.close()

print 'gerandoCsv...' + pathCsvEntidadesNomeadas

todasEntidadesNomeadas = list(set(todasEntidadesNomeadas))
primeiro = True
for entidadeNomeada in todasEntidadesNomeadas:
    csvEntidadesNomeadas.write(entidadeNomeada + '\n')

print 'Terminou!!!'
