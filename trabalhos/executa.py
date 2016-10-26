#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re
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

            if(len(taggeado) == 0):
                continue

            #print taggeado

            gramatica = """NNPS: {<NNP.*>+}
                           NNPVERBO: {<NNP.*>+<VBZ.*>+}
                           OFTHE: {<NNP.*>+<IN><DT><NNP.*>+<NNS.*>*}
                           NNPIN: {<NNP.*>+<IN><NNP.*>+}
                           INNNP: {<IN.*>+<NNP.*>+<POS.*>+<NNP.*>+}
                           NNPOSTROFE: {<NNP.*><POS><NNP.*>}"""

            agrupador = nltk.RegexpParser(gramatica)
            pedregulho = agrupador.parse(taggeado)

            entidadesNomeadas = []
            for pedra in pedregulho:
                if type(pedra) is nltk.Tree:
                    entidadeNomeada = ''
                    for no in pedra.leaves():
                        if len(entidadeNomeada) > 2:
                            #print 'to no if'
                            #print no
                            if no[1] == "NNP":
                                entidadeNomeada += ' ' + no[0]
                            if no[1] == "IN":
                                if no[0] != "of":
                                    break
                                entidadeNomeada += ' ' + no[0]
                            if no[1] == "DT":
                                entidadeNomeada += ' ' + no[0]
                            if no[1] == "POS":
                                entidadeNomeada += no[0]
                            if no[1] == "NNS":
                                entidadeNomeada += ' ' + no[0]
                        else:
                            #print 'to no elze'
                            #print no
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

def gerarTodasEntidadesNomeadas(caminhoEpisodios):
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
    return todasEntidadesNomeadas

def gerarCSV(pathCsvEntidadesNomeadas, todasEntidadesNomeadas):
    csvEntidadesNomeadas = open(pathCsvEntidadesNomeadas, 'w+')

    for entidadeNomeada in todasEntidadesNomeadas.iterkeys():
        csvEntidadesNomeadas.write(entidadeNomeada + ';' + str(todasEntidadesNomeadas[entidadeNomeada]) + '\n')
    csvEntidadesNomeadas.close()

def gerarCSVComAgrupamento(pathCsvEntidadesNomeadas, todasEntidadesNomeadas):
    csvEntidadesNomeadas = open(pathCsvEntidadesNomeadas, 'w+')

    entidadesNomeadasMaiorQueUm = ''
    for entidadeNomeada in todasEntidadesNomeadas.iterkeys():
        if len(todasEntidadesNomeadas[entidadeNomeada][0]) > 1:
            entidadesNomeadasMaiorQueUm += entidadeNomeada + ';' + str(todasEntidadesNomeadas[entidadeNomeada][0]) + ';' + str(todasEntidadesNomeadas[entidadeNomeada][1]) + '\n'
        else:
            entidadesNomeadasMaiorQueUm += todasEntidadesNomeadas[entidadeNomeada][0][0] + ';' + str(todasEntidadesNomeadas[entidadeNomeada][0]) + ';' + str(todasEntidadesNomeadas[entidadeNomeada][1]) + '\n'

    entidadesNomeadasMaiorQueUm = re.sub(r".*[;]1\n", r'', entidadesNomeadasMaiorQueUm)

    listaEntidades = entidadesNomeadasMaiorQueUm.split('\n')
    listaEntidades.sort()

    for entidade in listaEntidades:
        if entidade != '':
            csvEntidadesNomeadas.write(entidade + '\n')

    csvEntidadesNomeadas.close()

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio."
        exit(1)

    diretorioPai = abspath(join(sys.argv[1], pardir))

    caminhoEpisodios = sys.argv[1]

    todasEntidadesNomeadas = gerarTodasEntidadesNomeadas(caminhoEpisodios)
    gerarCSV('entidadesNomeadasComFrequencia.txt', todasEntidadesNomeadas)

    csvEntidadesNomeadasComFrequencia = open('entidadesNomeadasComFrequencia.txt', 'r')

    entidades = {}
    stopWords = ['Ser ','Queen ','Lord ', 'Prince ', 'Lord Commander ', 'Commander ', 'Maester ', 'Grand Maester ']
    for linha in csvEntidadesNomeadasComFrequencia:
        valores = linha.replace('\n','').split(';')

        entidade = valores[0]
        for stopWord in stopWords:
            try:
                localStopWord = re.search(r"" + stopWord, entidade).start()
                if localStopWord == 0:
                    entidade = re.sub(r"" + stopWord, r'', entidade)
            except Exception as e:
                continue

        #print entidade

        if entidade in entidades:
            #print 'to no ife'
            #print entidades[entidade]
            entidades[entidade]=[entidades[entidade][0] + [valores[0]], int(entidades[entidade][1])+int(valores[1])]
        else:
            #print 'to no elze'
            #print valores[0]
            entidades[entidade]=[[valores[0]], int(valores[1])]

    #print entidades

    gerarCSVComAgrupamento("entComAgrupamento.txt", entidades)

    #Marcando entidades no texto

    temporadas = [a for a in listdir(caminhoEpisodios)]
    for temporada in temporadas:
        path = temporada;
        arquivos = [a for a in listdir(join(caminhoEpisodios, path)) if isfile(join(join(caminhoEpisodios, path), a))]

        print 'Marcando Entidades Nomeadas No Texto...'

        pathDestino = basename(path)

        if not exists(pathDestino):
            makedirs(pathDestino)

        for pathArq in arquivos:
            textoPreProcessado = open(join(join(caminhoEpisodios, path), pathArq)).read()

            for entidade in entidades.iterkeys():
                regexp = '('
                listaDeNomes = entidades[entidade][0]


                primeiro = True;
                for nome in listaDeNomes:
                    if primeiro:
                        regexp += nome + r'[ .]' + ')'
                        primeiro = False
                    else:
                        regexp += '|(' + nome + r'[ .]' + ')'

                regexp = re.sub(r'\.', '\\\.', regexp)
                textoPreProcessado = re.sub(r''+ regexp, r'' + '<entity> ' + entidade + ' </entity>', textoPreProcessado)

            #print textoPreProcessado

            arquivo = open(join(path, pathArq), 'w+')
            arquivo.write(textoPreProcessado)

    entidadesComFrequencia = csvEntidadesNomeadasComFrequencia.read()
    csvEntidadesNomeadasComFrequencia.close()

    print 'Terminou!!!'

if __name__ == "__main__":
    main()
