# 🧪 Testes de Desempenho - Blockchain de Créditos de Carbono REDD+

Este repositório contém os scripts de teste de carga e desempenho desenvolvidos com **Locust** e **Web3.py** para validar a arquitetura distribuída de créditos de carbono. Os testes avaliam a latência, vazão (*throughput*) e integridade dos contratos inteligentes na rede permissionada (Hyperledger Besu/Anvil).

## 📋 Pré-requisitos

Antes de executar os testes, certifique-se de ter o ambiente configurado:

* **Python 3.8+**

### Instalação das Dependências

Instale as bibliotecas Python necessárias:

```bash
pip install locust web3 hexbytes

```

---

## ⚙️ Configuração do Ambiente

1. **Inicie a Blockchain Local:**

2. **Deploy dos Contratos:**
Faça o deploy dos contratos `forestMonitor` e `carbonRetirement`.
* *Nota: O `carbonRetirement` deve receber o endereço do `forestMonitor` no construtor.*


3. **Atualize os Scripts:**
Abra os arquivos `.py` e atualize as constantes com os endereços gerados na etapa anterior:
```python
FOREST_ADDRESS = "0x..." 
CARBON_ADDRESS = "0x..."

```


*Certifique-se também de que os arquivos `.json` com o ABI dos contratos estão na mesma pasta (ou no caminho correto).*

---

## 🚀 Executando os Testes

Para facilitar a análise, os testes foram segregados em dois arquivos distintos.

### 1. Teste do Monitoramento (`teste-foresfMonitor.py`)

Foca no registro de dados geoespaciais e criação dos NFTs.

* **Objetivo:** Medir o custo de persistência de metadados complexos *on-chain*.
* **Cenário:** Escrita (`createforestRecord`) vs Leitura (`getforestRecord`).

**Comando para rodar com Interface Web:**

```bash
locust -f teste-foresfMonitor.py

```

Acesse `http://localhost:8089` e configure a quantidade de usuários.

### 2. Teste de Aposentadoria (`teste-carbonRetirement.py`)

Foca no ciclo de vida do crédito e prevenção de dupla contagem.

* **Objetivo:** Validar a atomicidade da função `retireCredit`.
* **Lógica:** O script realiza um *Mint* invisível (não contabilizado no tempo) antes de medir exclusivamente o tempo da transação de *Retire*.
* **Cenário:** Escrita (`retireCredit`) vs Leitura (`isRetired`).

**Comando de execução:**

```bash
locust -f teste-carbonRetirement.py

```

## 📊 Interpretando os Resultados

O Locust gerará estatísticas no terminal ou na interface web. Para o artigo, foque nas seguintes métricas:

1. **RPS (Requests Per Second):** O *Throughput* da rede. Deve crescer linearmente com o número de usuários até o ponto de saturação.
2. **Average Latency (ms):**
* **Leitura:** Esperado < 20ms (Processamento local).
* **Escrita:** Esperado > 100ms (Custo do Consenso/Mineração).


3. **Failures:** Devem ser **0**. Qualquer falha indica erro de *nonce*, falta de *gas* ou erro na lógica do contrato (ex: dupla contagem bloqueada corretamente gera erro no Locust se não tratada, mas no nosso script capturamos isso como sucesso da lógica de negócio se for a intenção).

## 🛠️ Resolução de Problemas Comuns

* **Erro `Nonce too low`:**
* Isso acontece se o Locust enviar transações mais rápido do que o nó consegue confirmar.
* *Solução:* Reinicie o Anvil para resetar os nonces ou aumente o `wait_time` na classe `User` do script.


* **Erro `File not found (ABI)`:**
* Verifique se o caminho para `forestMonitor.json` ou `CarbonRetirement.json` está correto no início do script.


* **Latência de Escrita Zerada ou Falha Instantânea:**
* Geralmente indica que a transação nem chegou a ser enviada (erro de assinatura ou endereço errado). Verifique as chaves privadas e endereços dos contratos.