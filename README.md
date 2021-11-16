# DataSprints

## Case Técnico Engenharia de Dados

### Descrição para reprodução das análises

Para a solução das questões, foi criado o arquivo "main.py" onde nele se encontra todo o código utilizado para a atividade.

Os arquivos .json e .csv disponibilizados devem estar localizados no mesmo diretório do arquivo "main.py" para que a rotina seja executada.

O arquivo está dividido por módulos que correspondem a solução de cada pergunta.

No desenvolvimento deste case, eu optei por praticar sempre quando possível a utilização de queries em SQL para responder aos itens. A solução foi estruturada pensando em cada questão isoladamente, e não de forma eficiente em processamento em que poderia ser extraída apenas uma vez a base e então realizada todas as transformações sobre ela. 

Com base nisso, o primeiro passo foi carregar os arquivos json e csv em um banco de dados.
Com o banco de dados montado, foram realizadas as extrações e transformações dos dados para as respectivas questões.

As rotinas de solução para cada questão estão na seção "Main Function" do arquivo main.py.

Para a solução, basta remover os comentários em:

#loadData(files)

#question1()

#question2()

#question3()

#question4()

#question5()

#question6()

Para a visualização em mapa com latitude e longitude, a biblioteca Folium deve ser instalada.

O mapa com os pontos de embarque e desembarque das corridas encontra-se no arquivo "index.html".





