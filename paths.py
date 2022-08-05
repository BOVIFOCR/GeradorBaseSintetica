# Arquivo unicamente feito para não ter que mudar os paths em todos os arquivos.

path_base = '.' #paths.path

# Path com a imagem.
path_entrada = f'{path_base}/input/'
path_saida = f'{path_base}/reboot/'

# Nome do json de saída do VIA ANNOTATOR com as informações de todas as imagens rotuladas.
# json_name = 'new.json'
json_path = f'{path_base}/labels/'

# Diretórios que aguardam produtos intermediários da síntese
path_back = f'{path_base}/back'
path_crop = f'{path_base}/crop'
path_mask = f'{path_base}/mask'
path_tiles = f'{path_base}/tile'

# Diretório que guarda arquivos estáticos, como
path_static = f'{path_base}/files'