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
RELACOES = []
MAPA_EPISODIOS_TEMPORADA = dict()

def aplicarGramatica(sentencasTokenizadas, nomeEpisodioFormatado):
    gramaticaEntidades = r"""DATA: {<NNP><CD><.><CD>}
                             NOMES: {<NNP>+|<NNPS>+}
                             NNPINDTNNP: {<NOMES>(<IN><DT><NOMES>)+}
                             NNPINNNP: {<NOMES><IN><NOMES>}
                             NNPOSTROFE: {<NOMES><POS><NOMES>}"""

    gramaticaRelacoes = r"""DATA: {<NNP><CD><.><CD>}
                            NOMES: {<NNP>+|<NNPS>+}
                            NNPINDTNNP: {<NOMES>(<IN><DT><NOMES>)+}
                            NNPINNNP: {<NOMES><IN><NOMES>}
                            NNPOSTROFE: {<NOMES><POS><NOMES>}
                            ENTIDADE: {<DATA>|<NOMES>|<NNPINDTNNP>|<NNPINNNP>|<NNPOSTROFE>}
                            ADVERBIO: {<RB>|<RBR>|<RBS>}
                            VERBO: {<VB.*>|<TO><VB.*>}
                            RELACAO: {<ADVERBIO>*<VERBO>+<IN>*}
                            ENTIDADERELACAOENTIDADE: {<ENTIDADE><RELACAO><ENTIDADE>}"""

    textoEpisodio = ''
    cacheReferenciados = []
    for sentencaTokenizada in sentencasTokenizadas:

        if len(sentencaTokenizada) == 0:
            textoEpisodio += '\n'
            continue

        agrupadorEntidades = nltk.RegexpParser(gramaticaEntidades)

        taggeadoEntidades = nltk.pos_tag(sentencaTokenizada)

        sentencaEntidadesParseada = agrupadorEntidades.parse(taggeadoEntidades)

        agrupadorRelacoes = nltk.RegexpParser(gramaticaRelacoes)
        taggeadoRelacoes = nltk.pos_tag(sentencaTokenizada)
        sentencaRelacoesParseada = agrupadorRelacoes.parse(taggeadoRelacoes)

        #print taggeado
        #print sentencaParseada

        IN_Desejados = ['of', 'on']
        for arvore in sentencaEntidadesParseada:
            if type(arvore) is nltk.Tree:
                ehEntidade = True
                entidadeNomeada = ''
                for folha in arvore.leaves():
                    if len(entidadeNomeada) != '':
                        if folha[1] == 'IN' and folha[0] not in IN_Desejados:
                            ehEntidade = False

                        if folha[1] == 'POS':
                            entidadeNomeada += folha[0]
                        elif folha[1] == ',':
                            entidadeNomeada += folha[0]
                        else:
                            entidadeNomeada += ' ' + folha[0]
                    else:
                        entidadeNomeada = folha[0]

                if len(entidadeNomeada) != '':
                    if ehEntidade:
                        ENTIDADES_NOMEADAS.append(entidadeNomeada)

                        entidade = ''

                        global titulos
                        entidade = entidadeNomeada
                        for titulo in titulos:
                            if entidadeNomeada.startswith(titulo):
                                entidade = re.sub(r'' + titulo, r'', entidadeNomeada)

                        naoEstaNoCache = True
                        for referenciado in cacheReferenciados:
                            if entidade.startswith(referenciado):
                                if len(referenciado) > len(entidade):
                                    cacheReferenciados.append(referenciado)
                                    textoEpisodio += '<entidade "' + referenciado + '">' + entidadeNomeada + '</entidade> '
                                else:
                                    cacheReferenciados.append(entidade)
                                    textoEpisodio += '<entidade "' + entidade + '">' + entidadeNomeada + '</entidade> '
                                    cacheReferenciados.remove(referenciado)
                                naoEstaNoCache = False
                                break

                            elif referenciado.startswith(entidade):
                                if len(referenciado) > len(entidade):
                                    cacheReferenciados.append(referenciado)
                                    textoEpisodio += '<entidade "' + referenciado + '">' + entidadeNomeada + '</entidade> '
                                else:
                                    cacheReferenciados.append(entidade)
                                    textoEpisodio += '<entidade "' + entidade + '">' + entidadeNomeada + '</entidade> '
                                    cacheReferenciados.remove(referenciado)
                                naoEstaNoCache = False
                                break

                        if naoEstaNoCache:
                            cacheReferenciados.append(entidade)
                            textoEpisodio += '<entidade "' + entidade + '">' + entidadeNomeada + '</entidade> '

                        if len(cacheReferenciados) > 30:
                            del cacheReferenciados[0]

                    else:
                        textoEpisodio += entidadeNomeada + ' '
            else:
                if (arvore[0] == arvore[1] and re.match(r'[.,;?!]', arvore[0]) != None):
                    textoEpisodio = re.sub(r'[ ]\Z', r'', textoEpisodio) + arvore[0]
                elif re.match(r".*'.*", arvore[0]) != None:
                    textoEpisodio = re.sub(r'[ ]\Z', r'', textoEpisodio) + arvore[0] + ' '
                else:
                    textoEpisodio += arvore[0] + ' '

        textoEpisodio += '\n'

        for arvore in sentencaRelacoesParseada:
            if type(arvore) is nltk.Tree:
                relacao = ''
                if arvore.label() == 'ENTIDADERELACAOENTIDADE':
                    ehPrimeiraEntidade = True
                    for subarvore in arvore:
                        tempRelacao = ''
                        if subarvore.label() == 'ENTIDADE':
                            for folha in subarvore.leaves():
                                if folha[1] == 'IN' and folha[0] not in IN_Desejados:
                                    break;
                                if tempRelacao != '':
                                    tempRelacao += ' ' + folha[0]
                                else:
                                    tempRelacao = folha[0]
                            if ehPrimeiraEntidade:
                                tempRelacao += ','
                                ehPrimeiraEntidade = False
                        elif subarvore.label() == 'RELACAO':
                            for folha in subarvore.leaves():
                                if tempRelacao != '':
                                    tempRelacao += ' ' + folha[0]
                                else:
                                    tempRelacao = folha[0]
                            tempRelacao += ','
                        relacao+=tempRelacao

                    RELACOES.append(nomeEpisodioFormatado + ',' + relacao)

    return textoEpisodio

def processarEpisodios(caminhoEpisodios, episodios):
    mapaEpisodioTextoEpisodio = dict()

    for episodio in episodios:
        tokenizador = nltk.data.load('tokenizers/punkt/english.pickle')

        arquivo = open(join(caminhoEpisodios, episodio))

        sentencas = []
        for linha in arquivo:
            sentencas += (tokenizador.tokenize(linha.decode('utf8')))

        arquivo.close()

        #print sentencas

        sentencasTokenizadas = []
        for sentenca in sentencas:
            sentencasTokenizadas.append(nltk.word_tokenize(sentenca))

        nomeEpisodioFormatado = 'S' + caminhoEpisodios.split('/')[1].split('_')[1] + '_' + episodio.split('.txt')[0]
        nomeEpisodioFormatado = re.sub(',','' ,nomeEpisodioFormatado)
        mapaEpisodioTextoEpisodio[episodio] = aplicarGramatica(sentencasTokenizadas, nomeEpisodioFormatado)

    return mapaEpisodioTextoEpisodio

def executarProcessamento(diretorioTemporadas):
    temporadas = [t for t in listdir(diretorioTemporadas)]

    mapaEpisodioTextoEpisodio = dict()

    for temporada in sorted(temporadas):
        print 'Processando temporada: ' + temporada
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

def gerarCSVRelacoes(relacoes):
    csvRelacoes = open(join(DIRETORIO_DESTINO, 'relacoes.csv'), 'w+')

    csvRelacoes.write('Episodio,Entidade1,Relação,Entidade2' + '\n')
    for relacao in sorted(relacoes):
        csvRelacoes.write(relacao + '\n')
    csvRelacoes.close()

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
    gerarCSVRelacoes(RELACOES)


def escreverEmArquivo(caminho, texto):
    arquivo = open(caminho, 'w+')
    arquivo.write(texto)
    arquivo.close()

def criarPasta(caminho):
    if not (isdir(caminho)):
        makedirs(caminho)

if __name__ == "__main__":
    main()
