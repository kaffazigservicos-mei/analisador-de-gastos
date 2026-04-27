📊 Guia do Usuário: Analisador de Gastos OFX
Este pacote contém uma ferramenta completa para transformar seus extratos bancários em um dashboard financeiro inteligente.

1. 🛠️ Preparação do Ambiente
Antes de abrir o aplicativo pela primeira vez, você precisa instalar os requisitos necessários.

Abrir o Terminal (CMD):

Pressione as teclas Windows + R, digite cmd e aperte Enter.

Navegar até a pasta do App:

No terminal, digite cd seguido do caminho onde você salvou esta pasta.

Exemplo: cd C:\Projetos\GestaoFinanceira

Instalar Dependências:

Digite o comando abaixo e aguarde a finalização:

Bash
pip install -r requirements.txt
2. 🚀 Como Iniciar o Aplicativo
Sempre que quiser usar o app, siga este procedimento:

Abra o Terminal (CMD).

Navegue até a pasta (usando o comando cd como mostrado acima).

Digite o comando de inicialização:

Bash
streamlit run app.py
O sistema abrirá automaticamente uma aba no seu navegador de internet.

3. 🕹️ Como Usar o Sistema
Importando Dados
Clique em "📁 Importar Extrato" para expandir a área de upload.

Selecione seu arquivo .OFX exportado do banco.

Clique no botão 🔄 Processar Novo Arquivo.

Atenção: O sistema possui trava de duplicidade. Se você subir o mesmo arquivo duas vezes, ele ignorará as transações repetidas para não contaminar seu saldo.

Categorizando Gastos
Na tabela "DETALHAMENTO", você pode clicar na coluna "Categoria" para classificar cada gasto.

Após classificar, clique no botão 💾 Salvar Alterações no final da tabela. Uma notificação aparecerá confirmando o salvamento.

Dashboard e Gráficos
Card de Despesas: Exibe o valor real total de todas as saídas registradas no período.

Gráfico TOP 5: Este gráfico destaca exclusivamente as 5 categorias onde houve o maior volume de gastos.

Observação Importante: A soma das barras do gráfico pode ser menor que o valor total exibido no Card de Despesas. 
Isso ocorre porque o gráfico prioriza a visualização dos seus 5 maiores gargalos financeiros, omitindo categorias menores para manter a clareza visual.

4. 🧽 Manutenção e "Reset" (Dica de Ouro)
Se você desejar apagar todos os dados e começar o gerenciamento do zero (limpar o banco de dados):

Feche o terminal onde o app está rodando.

Vá até a pasta do projeto pelo explorador de arquivos do Windows.

Localize o arquivo financeiro.db e delete-o.

Ao rodar o comando streamlit run app.py novamente, o sistema criará um banco novo e vazio.
--------------------------------------------
Foco em automação, precisão de dados e gestão eficiente.
