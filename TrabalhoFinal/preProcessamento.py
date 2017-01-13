import sys
import re
import os

def main():
    if len(sys.argv) != 2:
        print "Deve ser passado o nome do diretorio."
        exit(1)

    diretorioPai = os.path.abspath(os.path.join(sys.argv[1], os.pardir))

    caminhoLivro = sys.argv[1]
    caminhoLivroPreProcessados = os.path.join(diretorioPai, "PreProcessado")
    
    # Executando shell para remover caracteres
    os.system("./removerCaracteresIndesejaveis.sh " + caminhoLivro)

    if not (os.path.isdir(caminhoLivroPreProcessados)):
        os.mkdir(caminhoLivroPreProcessados)

    nomeLivro = 'pride_and_prejudice'
    textoLivro = open(os.path.join(caminhoLivro, nomeLivro + '.txt')).read()

    textoLivro = re.sub(r'\n', r' ', textoLivro)
    textoCapitulos = re.split('Chapter [0-9]+[ ]+', textoLivro)
    
    count = 0
    for textoCapitulo in textoCapitulos:
        if count != 0:
            salvarArquivo(textoCapitulo, os.path.join(caminhoLivroPreProcessados, nomeLivro + '_' + str(count) + '.txt'))
        count = count + 1
    
    print "Terminou!"

def salvarArquivo(texto, caminho):
    saida = open(caminho, 'w+')
    saida.write(texto)
    saida.close()
  


def criarPasta(caminho):
    if not (os.path.isdir(caminho)):
        os.mkdir(caminho)

if __name__ == "__main__":
    main()
