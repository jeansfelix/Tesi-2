#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath

reload(sys)
sys.setdefaultencoding("utf-8")

def processaTemporada(temporada):
    path = temporada;
    arquivos = [a for a in listdir(path) if isfile(join(path, a))]

    print 'Procurando Entidades Nomeadas...'

    pathDestino = basename(path)

    if not exists(pathDestino):
        makedirs(pathDestino)

    todasEntidadesNomeadas = dict()

    for pathArq in arquivos:
        arquivo = open(join(path, pathArq))

        #print  'Processando arquivo ' + join(path, pathArq)

        stringLida = arquivo.read()

        saida = open(join(pathDestino, pathArq.replace(".txt", "_ARQUIVO-GERADO.txt")), 'w+')

        tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')
        stringLida = stringLida.decode('utf8')

        sentencas = []
        listaLinhas = [x for x in stringLida.split('\n') if x]
        for linha in listaLinhas:
            sentencasLinha = tokenizador.tokenize(linha)
            for sentencaLinha in sentencasLinha:
                sentencas.append(sentencaLinha)

        listaDeSentencaTokenizada = []
        for sentenca in sentencas:
            listaDeSentencaTokenizada.append(nltk.word_tokenize(sentenca))

        for sentencaTokenizada in listaDeSentencaTokenizada:
            taggeado = nltk.pos_tag(sentencaTokenizada)

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
                saida.write('[')
                cont = 0
                for entidadeNomeada in entidadesNomeadas:
                    if cont > 0:
                        saida.write(", '"+ entidadeNomeada + "'")
                    else:
                        saida.write("'"+ entidadeNomeada + "'")
                    cont += 1
                saida.write(']\n')

            #todasEntidadesNomeadas += entidadesNomeadas
            for entidadeNomeada in entidadesNomeadas:
                if entidadeNomeada in todasEntidadesNomeadas:
                    todasEntidadesNomeadas[entidadeNomeada] += 1
                else:
                    todasEntidadesNomeadas[entidadeNomeada] = 1

        saida.close()

    return  todasEntidadesNomeadas

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio."
        exit(1)

    diretorioPai = abspath(join(sys.argv[1], pardir))

    caminhoEpisodios = sys.argv[1]
    caminhoEpisodiosPreProcessados = join(diretorioPai, "PreProcessado")

    if not (isdir(caminhoEpisodiosPreProcessados)):
        os.mkdir(caminhoEpisodiosPreProcessados)

    temporadas = [a for a in listdir(caminhoEpisodios)]

    todasEntidadesNomeadas = dict()
    for temporada in temporadas:
        entidadesNomeadasPorTemporada = processaTemporada(join(caminhoEpisodios, temporada))
        #todasEntidadesNomeadas = list(set(todasEntidadesNomeadas + entidadesNomeadasPorTemporada))
        for chave in entidadesNomeadasPorTemporada.iterkeys():
            if chave in todasEntidadesNomeadas:
                todasEntidadesNomeadas[chave] += entidadesNomeadasPorTemporada[chave]
            else:
                todasEntidadesNomeadas[chave] = entidadesNomeadasPorTemporada[chave]

    pathCsvEntidadesNomeadas = 'entidadesNomeadas.txt'
    csvEntidadesNomeadas = open(pathCsvEntidadesNomeadas, 'w+')

    for entidadeNomeada in todasEntidadesNomeadas.iterkeys():
        csvEntidadesNomeadas.write(entidadeNomeada + ' ' + str(todasEntidadesNomeadas[entidadeNomeada]) + '\n')

    print 'Terminou!!!'

if __name__ == "__main__":
    main()
