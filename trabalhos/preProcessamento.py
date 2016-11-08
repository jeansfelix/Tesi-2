import sys
import re
import os

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio."
        exit(1)

    diretorioPai = os.path.abspath(os.path.join(sys.argv[1], os.pardir))

    caminhoEpisodios = sys.argv[1]
    caminhoEpisodiosPreProcessados = os.path.join(diretorioPai, "PreProcessado")

    # Executando shell para remover caracteres
    os.system("./removerCaracteresIndesejaveis.sh " + caminhoEpisodios)

    if not (os.path.isdir(caminhoEpisodiosPreProcessados)):
        os.mkdir(caminhoEpisodiosPreProcessados)

    temporadas = [a for a in os.listdir(caminhoEpisodios)]

    for temporada in temporadas:
        episodios = [a for a in os.listdir(os.path.join(caminhoEpisodios, temporada))]

        caminhoTemporadaPreProcessado = os.path.join(caminhoEpisodiosPreProcessados, temporada)
        criarPasta(caminhoTemporadaPreProcessado)

        pastaEp = 'episodios'
        pastaMortes = 'mortes'
        pastaAtores = 'atores'
        pastaFalas = 'falas'

        criarPasta(os.path.join(caminhoTemporadaPreProcessado, pastaEp))
        criarPasta(os.path.join(caminhoTemporadaPreProcessado, pastaMortes))
        criarPasta(os.path.join(caminhoTemporadaPreProcessado, pastaAtores))
        criarPasta(os.path.join(caminhoTemporadaPreProcessado, pastaFalas))

        print "Limpando texto " + temporada
        for episodio in episodios:
            #print "Limpando ep: " + episodio + ' ' + temporada

            caminhoEp = os.path.join(caminhoTemporadaPreProcessado, pastaEp)
            caminhoMortes = os.path.join(caminhoTemporadaPreProcessado, pastaMortes)
            caminhoAtores = os.path.join(caminhoTemporadaPreProcessado, pastaAtores)
            caminhoFalas = os.path.join(caminhoTemporadaPreProcessado, pastaFalas)

            textoArquivo = open(os.path.join(os.path.join(caminhoEpisodios, temporada), episodio)).read()

            textoEpisodio = recuperarEpisodio(textoArquivo)
            salvarArquivo(textoEpisodio, os.path.join(caminhoEp, episodio))

            mortesEpisodio = recuperarMortes(textoArquivo)
            salvarArquivo(mortesEpisodio, os.path.join(caminhoMortes, episodio))

            atoresEpisodio = recuperarAtores(textoArquivo)
            salvarArquivo(atoresEpisodio, os.path.join(caminhoAtores, episodio))

            falasEpisodio = recuperarFalas(textoArquivo)
            salvarArquivo(falasEpisodio, os.path.join(caminhoFalas, episodio))

    print "Terminou!"

def salvarArquivo(texto, caminho):
    saida = open(caminho, 'w+')
    saida.write(texto)
    saida.close()

def recuperarEpisodio(texto):
    try:
        inicioTrecho = re.search(r"(Written by)", texto).start()
        fimTrecho = re.search(r"([Rr]ecap)((\n)|[Ee]dit)|Appearances|\Z", texto).start()
        trecho = texto[inicioTrecho:fimTrecho]
    except Exception as e:
        return ''

    trecho = limparTexto(trecho)
    trecho = re.sub(r'"', r'', trecho)

    return trecho

def recuperarMortes(texto):
    try:
        inicioTrecho = re.search(r"(Deaths)((\n)|[])([Ee]dit)?(\n)?", texto).start()
        fimTrecho = re.search(r"([Cc]ast)[ ]([Nn]otes)", texto).start()
        trecho = texto[inicioTrecho:fimTrecho]

        inicioTrecho = re.search(r"(Deaths)((\n)|[])([Ee]dit)?(\n)?", trecho).start()
        fimTrecho = re.search(r"([C]ast)|(Production)", trecho).start()
        trecho = trecho[inicioTrecho:fimTrecho]
    except Exception as e:
        return ''

    return limparTexto(trecho)

def recuperarAtores(texto):
    try:
        inicioTrecho = re.search(r"([Ss]tarring)([Ee]dit)?", texto).start()
        fimTrecho = re.search(r"(Uncredited)|(Cast[ ]notes)|\Z", texto).start()
        trecho = texto[inicioTrecho:fimTrecho]
    except Exception as e:
        return ''

    return limparTexto(trecho)

def recuperarFalas(texto):
    try:
        inicioTrecho = re.search(r"([Mm]emorable([ ])?[Qq]uotes(Edit)?)", texto).start()
        fimTrecho = re.search(r"\Z", texto).start()
        trecho = texto[inicioTrecho:fimTrecho]

        inicioTrecho = re.search(r"([Mm]emorable([ ])?[Qq]uotes(Edit)?)", trecho).start()
        fimTrecho = re.search(r"([Gg]allery([ ]?Edit)?\n)|JSSnippetsStack|(Image[ ][Gg]allery(Edit)?)|([Pp]romotional[ ][Ii]mages(Edit)?)|([Ss]ee [Aa]lso)|\Z", trecho).start()
        trecho = trecho[inicioTrecho:fimTrecho]
    except Exception as e:
        return ''

    return limparTexto(trecho)

def limparTexto(texto):
    texto = re.sub(r"Contents\[.*\]", r'', texto)
    texto = re.sub(r"Written by(\n|Edit)", r'', texto)
    texto = re.sub(r"Directed by(\n|Edit)", r'', texto)
    texto = re.sub(r"Previous(\n|Edit)", r'', texto)
    texto = re.sub(r"Next(\n|Edit)", r'', texto)
    texto = re.sub(r"Episode Guide(\n|Edit)", r'', texto)
    texto = re.sub(r"Summary(\n|Edit)", r'', texto)
    texto = re.sub(r"Plot(\n|Edit)", r'', texto)
    texto = re.sub(r"Deaths(\n|Edit)", r'', texto)
    texto = re.sub(r"Appearances(\n|Edit)", r'', texto)
    texto = re.sub(r"Cast(\n|Edit)", r'', texto)
    texto = re.sub(r"First(\n|Edit)", r'', texto)
    texto = re.sub(r"Recap(\n|Edit)", r'', texto)
    texto = re.sub(r"Stunt performers\n", r'', texto)
    texto = re.sub(r"Cast notes(\n|Edit)", r'', texto)
    texto = re.sub(r"Notes(\n|Edit)", r'', texto)
    texto = re.sub(r"In the books(\n|Edit)", r'', texto)
    texto = re.sub(r"Memorable quotes(\n|Edit)", r'', texto)
    texto = re.sub(r"Episode commentary(\n|Edit)", r'', texto)
    texto = re.sub(r"[Mm]arketing(\n|Edit)", r'', texto)
    texto = re.sub(r"[/\\]", r' ', texto)
    texto = re.sub(r"[\[\]]", r'', texto)

    texto = re.sub(r"Edit\n", r'\n', texto)
    texto = re.sub(r"(\n.*)?([A-Z][a-z]*[ ]?)?([Uu]ncredited\n.*)", r'', texto)
    texto = re.sub(r"(\.[0-9])", r' ', texto)
    texto = re.sub(ur"[\u2014]", r'', texto)
    texto = re.sub(r"(\n.*)?([A-Z][a-z]*[ ]?)?([Ss]tarring\n.*)", r'', texto)

    while  texto != re.sub(r"\n\n\n", r'\n\n', texto):
        texto = re.sub(r"\n\n\n", r'\n\n', texto)

    return texto

def criarPasta(caminho):
    if not (os.path.isdir(caminho)):
        os.mkdir(caminho)

if __name__ == "__main__":
    main()
