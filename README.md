# LDP Trabalho 1

## Instruções

Instalar um editor de texto, recomendamos o [Visual Studio Code](https://code.visualstudio.com/) com a extensão [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop).

Instalar o MikTex no Windows, [aqui](https://miktex.org/howto/install-miktex) tem instruções; instalar Perl, [aqui](https://strawberryperl.com/) tem instruções; e instalar Python, [aqui](https://www.python.org/downloads/) tem instruções.

_DICA: Se tiveres scoop instalado (ver [aqui](https://scoop.sh/)), podes instalar o MikTex, Perl e Python com o comando `scoop install miktex perl python`._

## Resumo

### Aplicação de Segurança Informática

Os alunos têm o objetivo de realizarem uma aplicação de segurança informática construída com uma linguagem de programação dinâmica: Python; Ruby; Perl ou PHP. Recomenda-se o uso de Python. A escrita de código adicional na linguagem de programação C/C++ com o eventual uso de bibliotecas adicionais é possível e eventualmente desejável.
Os alunos devem realizar uma ferramenta de segurança informática que:

- permita detetar e listar que portos de rede se encontram disponíveis numa ou mais máquinas remotas;
- Elaborar um UDP flood (DoS) para um IP remoto (poderá utilizar a biblioteca scapy)
- Elaborar um SYN flood(TCP SYN Packets – pode ser a um serviço http ou SMTP, ou outro qualquer à escolha do aluno) (poderá utilizar a biblioteca scapy)
- Analisar e processar ficheiros de log (pelo menos de 2 serviços, ex: http, ssh) listando a origem dos acessos e/ou tentativas de acesso inválidas, os serviços a analisar deverão estar instalado no computador local de cada aluno. O output do processamento deverá mencionar:
- Listas de origem do país;
- timestamp das tentativas e ou acessos;
- etc.
- Outra opção para análise e recebimento de logs pode ser com recurso à utilização de um syslog server, esta opção é valorizada em relação à anterior. Exemplos de Syslog Servers que poderão usar: graylog, Fluentd, Flume, rsyslog, etc.
- Outra opção para análise e recebimento de logs, poderá ser com a utilização e acesso a um router da Mikrotik (routerOS), opção valorizada em relação às anteriores.
- Elaborar um serviço básico de troca de mensagens seguras entre um cliente e servidor, utilizando chaves
  simétricas e/ou assimétricas;
- Funcionalidades a valorizar para além do serviço básico de troca de mensagens
- Serviço de troca de mensagens multiutilizador, com o arquivamento das mensagens seguras trocadas entre todos os intervenientes, estas mensagens devem ser armazenadas em ficheiros de texto encriptados com chaves assimétricas. As mensagens apenas devem ser armazenadas no lado do servidor. É obrigatório que seja possível a consulta/visualização de todas as mensagens utilizando a chave privada correspondente.

Para o mínimo ser atingido basta o arquivamento das mensagens entre um cliente e o servidor.

- Pretende-se que seja possível a pedido de um qualquer cliente do sistema de troca de
  mensagens a listagem, a remoção, o download de todas as mensagens arquivadas
  existentes no servidor em que o cliente foi interveniente.
- outras caraterísticas de segurança informática podem ser incorporadas no trabalho sendo valorizadas casuisticamente.
  A ferramenta pode ser projetada para uso em modo de linha de comando ou modo gráfico dando-se preferência ao modo de linha de comando.
  A aplicação deve permitir a produção de relatórios de segurança em formato PDF. Listas de informação devem ser produzidas em formato CSV. Deve poder ser produzida e processada informação para uma base de dados SQLite.

Alguns elementos de interesse para esta aplicação:

- uso das bibliotecas de rede de Python ou outras linguagens de programação dinâmicas;
- uso da biblioteca libpcap;
- a geração de PDFs com reportlab;
- gráficos com estatísticas, nomeadamente usando a biblioteca matplotlib;
- mapas geográficos usando as bases de dados GeoIP;
- autenticação no acesso à aplicação e aos scripts;
- cifragem dos dados, dados armazenados em ficheiros ou sqlite;
  A aplicação projetada pode usar bibliotecas e ferramentas externas à aplicação.

### Sistema Operativo

O sistema operativo escolhido para a realização do trabalho pode ser um dos seguintes:

- BSD numa das suas variantes;
- Linux numa das suas variantes;
- OSX numa das suas variantes.
  Sugere-se que o trabalho seja desenvolvido numa máquina virtual ligeira e com um editor de texto de sistema em modo de consola, por exemplo: vi, emacs, nano, etc. A utilização de ambientes integrados de desenvolvido, vulgarmente conhecidos por IDE, ou de editores que necessitem de suporte gráfico é fortemente desencorajada.
