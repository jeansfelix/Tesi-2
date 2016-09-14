#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk

print 'Number of arguments:', len(sys.argv), 'arguments.'

if len(sys.argv) != 2:
    print "Deve ser passado o nome do arquivo."
    exit(1)

arquivo = open(sys.argv[1])
stringLida = arquivo.read().decode('UTF-8')

print 'Texto Referente Ao Artigo:'
print stringLida

tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')
stringLida = stringLida.encode(encoding='U7', errors='strict')

sentencas = []
listaLinhas = [x for x in stringLida.split('\n') if x]
for linha in listaLinhas:
    sentencasLinha = tokenizador.tokenize(linha)
    for sentencaLinha in sentencasLinha:
        sentencas.append(sentencaLinha)

print '\n\nSentenças:'
print sentencas

palavras = []
for sentenca in sentencas:
    palavras.append(nltk.word_tokenize(sentenca))

print '\n\nEntidades Nomeadas:'

for palavra in palavras:
    taggeado = nltk.pos_tag(palavra)

    gramatica = """THENNP: {<DT.*>+<NNP.*>+}
                   NNPS: {<NNP.*>+<NN.*>+}
                   NNPVERBO: {<NNP.*>+<VBZ.*>+}
                   NNPIN: {<NNP.*>+<IN.*>+}
                   INNNP: {<IN.*>+<NNP.*>+<POS.*>+<NNP.*>+}
                   FALA: {<NNP.*>+<:.*>+}
                   FALADO: {<:.*>+<NNP.*>+}"""
    agrupador = nltk.RegexpParser(gramatica)
    pedregulho = agrupador.parse(taggeado)

    entidadesNomeadas = []
    for pedra in pedregulho:
        if type(pedra) is nltk.Tree:
            entidadeNomeada = ''
            for no in pedra.leaves():
                if len(entidadeNomeada) > 2:
                    if no[1] == "NNP":
                        entidadeNomeada += ' ' + no[0]
                    if no[1] == "POS":
                        entidadeNomeada += no[0]
                else:
                    if no[1] == "NNP":
                        entidadeNomeada = no[0]
            if len(entidadeNomeada) != 0:
                entidadesNomeadas.append(entidadeNomeada)

    if len(entidadesNomeadas) != 0:
        print entidadesNomeadas
