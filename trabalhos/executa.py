#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, nltk, codecs, re
from os import listdir, makedirs, pardir
from os.path import isfile, isdir, join, basename, exists, abspath
from nltk.probability import FreqDist

reload(sys)
sys.setdefaultencoding("utf-8")

titulos = ['Ser ','Queen ','Lord ', 'Prince ', 'Princess ', 'Lord Commander ', 'Commander ', 'Maester ', 'Grand Maester ']

DIRETORIO_DESTINO = ''
ENTIDADES_NOMEADAS = []
MAPA_EPISODIOS_TEMPORADA = dict()

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

def main2():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio."
        exit(1)

    diretorioPai = abspath(join(sys.argv[1], pardir))

    caminhoEpisodios = sys.argv[1]

    todasEntidadesNomeadas = gerarTodasEntidadesNomeadas(caminhoEpisodios)
    gerarCSV('entidadesNomeadasComFrequencia.txt', todasEntidadesNomeadas)

    csvEntidadesNomeadasComFrequencia = open('entidadesNomeadasComFrequencia.txt', 'r')

    entidades = dict()
    titulos = ['Ser ','Queen ','Lord ', 'Prince ', 'Princess ', 'Lord Commander ', 'Commander ', 'Maester ', 'Grand Maester ']
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

def aplicarGramatica(sentencasTokenizadas):
    textoEpisodio = ''
    for sentencaTokenizada in sentencasTokenizadas:
        gramatica = r"""NNPS: {<NNP.*>+}
                       NNPINDTNNP: {<NNP.*>+<IN><DT><NNP.*>+<NNS.*>*}
                       NNPINNNP: {<NNPS>+<IN><NNPS>+<NNS.*>}
                       NNPOSTROFE: {<NNP.*><POS><NNP.*>+}"""

        agrupador = nltk.RegexpParser(gramatica)

        taggeado = nltk.pos_tag(sentencaTokenizada)

        sentencaParseada = agrupador.parse(taggeado)

        #print taggeado

        for arvore in sentencaParseada:
            if type(arvore) is nltk.Tree:
                entidadeNomeada = ''
                for folha in arvore.leaves():
                    if len(entidadeNomeada) > 2:
                        if folha[1] == 'POS':
                            entidadeNomeada += folha[0]
                        else:
                            entidadeNomeada += ' ' + folha[0]
                    else:
                        entidadeNomeada = folha[0]

                if entidadeNomeada != '':
                    ENTIDADES_NOMEADAS.append(entidadeNomeada)
                    textoEpisodio += '<entidade>' + entidadeNomeada + '</entidade> '
            else:
                if (arvore[0] == arvore[1] and re.match(r'[.,;?!]', arvore[0]) != None):
                    textoEpisodio = re.sub(r'[ ]\Z', r'', textoEpisodio) + arvore[0]
                elif re.match(r".*'.*", arvore[0]) != None:
                    textoEpisodio = re.sub(r'[ ]\Z', r'', textoEpisodio) + arvore[0] + ' '
                else:
                    textoEpisodio += arvore[0] + ' '

        textoEpisodio += '\n'

    return textoEpisodio

def processarEpisodios(caminhoEpisodios, episodios):
    mapaEpisodioTextoEpisodio = dict()

    for episodio in episodios:
        arquivo = open(join(caminhoEpisodios, episodio))
        stringLida = arquivo.read()
        arquivo.close()

        stringLida = stringLida.decode('utf8')

        tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')
        sentencas = tokenizador.tokenize(stringLida)

        sentencasTokenizadas = []
        for sentenca in sentencas:
            sentencasTokenizadas.append(nltk.word_tokenize(sentenca))

        mapaEpisodioTextoEpisodio[episodio] = aplicarGramatica(sentencasTokenizadas)

    return mapaEpisodioTextoEpisodio

def executarProcessamento(diretorioTemporadas):
    temporadas = [t for t in listdir(diretorioTemporadas)]

    mapaEpisodioTextoEpisodio = dict()

    for temporada in temporadas:
        caminhoTemporada = join(diretorioTemporadas, temporada)

        caminhoAtores = join(caminhoTemporada, 'atores')
        caminhoEpisodios = join(caminhoTemporada, 'episodios')
        caminhoFalas =  join(caminhoTemporada, 'falas')
        caminhoMortes = join(caminhoTemporada, 'mortes')

        episodios = [e for e in listdir(caminhoAtores)]
        MAPA_EPISODIOS_TEMPORADA[temporada] = episodios

        mapaEpisodioTextoEpisodio = dict(mapaEpisodioTextoEpisodio.items() + (processarEpisodios(caminhoEpisodios, episodios).items()))

    return mapaEpisodioTextoEpisodio

def gerarArquivoTextoMarcado(diretorioTemporadas, mapaEpisodioTextoEpisodio):
    diretorioTextoMarcado = join(DIRETORIO_DESTINO, 'entidadesMarcadasNoTexto')
    criarPasta(diretorioTextoMarcado)

    for temporada in [t for t in listdir(diretorioTemporadas)]:
        diretorioTemporada = join(diretorioTextoMarcado, temporada)
        criarPasta(diretorioTemporada)
        for episodio in MAPA_EPISODIOS_TEMPORADA[temporada]:
            textoMarcado = mapaEpisodioTextoEpisodio[episodio]
            escreverEmArquivo(join(diretorioTemporada, episodio), textoMarcado)

def gerarCSVEntidadesNomeadas(todasEntidadesNomeadas):
    csvEntidadesNomeadas = open(join(DIRETORIO_DESTINO,'entidadesNomeadas.csv'), 'w+')

    entidadesNomeadasSemMonoSilabas = [a for a in todasEntidadesNomeadas if len(a) > 2]

    for entidadeNomeada in sorted(entidadesNomeadasSemMonoSilabas):
        csvEntidadesNomeadas.write(entidadeNomeada + '\n')
    csvEntidadesNomeadas.close()

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio PreProcessado."
        exit(1)

    diretorioTemporadas = sys.argv[1]

    global DIRETORIO_DESTINO
    DIRETORIO_DESTINO = join(abspath(join(diretorioTemporadas, pardir)), 'saida')
    criarPasta(DIRETORIO_DESTINO)

    mapaEpisodioTextoEpisodio = executarProcessamento(diretorioTemporadas)

    diretorioTextoMarcado = join(DIRETORIO_DESTINO, 'entidadesMarcadasNoTexto')
    criarPasta(diretorioTextoMarcado)

    gerarArquivoTextoMarcado(diretorioTemporadas, mapaEpisodioTextoEpisodio)

    gerarCSVEntidadesNomeadas(ENTIDADES_NOMEADAS)

def escreverEmArquivo(caminho, texto):
    arquivo = open(caminho, 'w+')
    arquivo.write(texto)
    arquivo.close()

def criarPasta(caminho):
    if not (isdir(caminho)):
        makedirs(caminho)

if __name__ == "__main__":
    main()
