import os

file = open("nomeArquivo.txt", "r")

for line in file:
    fields = line.split(";")
    arquivo = fields[0]
    pastaAtualizacao = fields[1].replace('\n', '')
    print(arquivo + "/" + pastaAtualizacao)
    dirName = pastaAtualizacao
    try:
        os.mkdir(dirName)
        print("Directory ", dirName, " Created ")
    except FileExistsError:
        print("Directory ", dirName, " already exists")

file.close()