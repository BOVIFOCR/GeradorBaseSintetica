# Documentação

<!-- trunk-ignore(markdownlint/MD013) -->
A implementação divide a tarefa de sintetizar fotos de documentos a partir de fotos em reais em 2 sub-tarefas:

- **anonimização**
  - localiza as regiões da foto real que contém dados sensíveis e as apaga
  - essa tarefa é coberta pela regra `make anonimize`
- **síntese**
  <!-- trunk-ignore(markdownlint/MD013) -->
  - preenche as regiões borradas durante a anonimização por dados sintéticos, apresentados de forma fiel a estética da foto original
  - essa tarefa é coberta pela regra `make synth`

## Código fonte do sintetizador

<!-- trunk-ignore(markdownlint/MD013) -->
Essa seção documenta o código fonte que implementa os processos mais fundamentais à construção do nBID.

Os processos são implementados em Python e estão localizados no diretório [`src/`](../src/).

### Dependência entre regras `make` e arquivos

<!-- trunk-ignore(markdownlint/MD013) -->
O gráfico abaixo representa a dependência das regras `make` (a [principal interface](../Makefile) para executar os processos implementados em Python) a cada arquivo do código fonte, assim como as dependências entre os próprios arquivos.

<!-- trunk-ignore(markdownlint/MD033) -->
<img src="./assets/Synth - Source Code Dependency.svg">

O gráfico utiliza a seguinte legenda visual:

- componentes em branco representam regras `make`
- componentes retangulares representam arquivos Python
  <!-- trunk-ignore(markdownlint/MD013) -->
  - arquivos representados em verde contém funções que já foram reimplementadas com o objetivo de intensificar a fidelidade das imagens sintetizadas, e **são responsáveis por processos que ainda podem ser melhorados**
  <!-- trunk-ignore(markdownlint/MD013) -->
  - arquivos representados em amarelo contém funções que **não foram suficientemente exploradas** e **podem atuar em certos pontos de melhoria**
    <!-- trunk-ignore(markdownlint/MD013) -->
    - arquivos representados em lilás contém funções cujas implementações já atendem aos requisitos da aplicação
