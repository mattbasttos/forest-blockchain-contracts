# Smart Contracts – Monitoramento Florestal e Aposentadoria de Créditos de Carbono

Este repositório contém contratos inteligentes desenvolvidos em **Solidity**, utilizando o **Foundry** como framework principal, voltados para **monitoramento florestal** e **aposentadoria (retirement) de créditos de carbono**. O projeto foi estruturado com foco em testes automatizados, boas práticas de segurança e reutilização de bibliotecas consolidadas.

---

## 📁 Estrutura do Projeto

```text
lib/
 ├─ forge-std/                 # Biblioteca padrão do Foundry (Test, Script, Vm)
 └─ openzeppelin-contracts/    # Contratos OpenZeppelin (Ownable, ERCs, etc.)

scripts/
 └─ Deploy.s.sol               # Script de deploy dos contratos

src/
 ├─ carbonRetirement.sol       # Contrato de aposentadoria de créditos de carbono
 └─ forestMonitor.sol          # Contrato de monitoramento florestal

test/
 ├─ carbonRetirement.t.sol     # Testes unitários do CarbonRetirement
 └─ forestMonitor.t.sol        # Testes unitários do ForestMonitor
```

---

## 🛠️ Pré-requisitos

Certifique-se de ter os seguintes itens instalados:

* **Foundry** (forge, cast, anvil)
* **Git**
* **Node.js** (opcional, apenas se for integrar com front-end)

Instalação do Foundry:

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

---

## 📦 Instalação do Projeto

Clone o repositório e instale as dependências:

```bash
git clone <url-do-repositorio>
cd <nome-do-projeto>

forge install
```

Caso as dependências não estejam configuradas:

```bash
forge install OpenZeppelin/openzeppelin-contracts
```

---

## ⚙️ Compilação dos Contratos

Para compilar todos os contratos:

```bash
forge build
```

---

## 🧪 Execução dos Testes

Execute todos os testes unitários:

```bash
forge test
```

Com logs detalhados:

```bash
forge test -vvv
```

Os testes validam:

* Regras de negócio dos contratos
* Controle de acesso
* Emissão e registro de eventos
* Condições inválidas e falhas esperadas

---

## 📜 Contratos Inteligentes

### 🌳 `ForestMonitor.sol`

Contrato responsável por registrar e consultar informações relacionadas ao **monitoramento florestal**, como:

* Registro de áreas monitoradas
* Atualização de métricas ambientais
* Armazenamento de evidências ou hashes (ex: dados de satélite)
* Controle de permissões para entidades autorizadas

Uso típico:

* Oráculos ou agentes autorizados registram dados ambientais
* Outros contratos ou aplicações consultam o estado florestal

---

### ♻️ `CarbonRetirement.sol`

Contrato responsável pela **aposentadoria de créditos de carbono**, garantindo que créditos não sejam reutilizados.

Funcionalidades principais:

* Registro de créditos de carbono
* Aposentadoria (retirement) de créditos
* Associação de créditos a projetos ou áreas monitoradas
* Emissão de eventos auditáveis

Uso típico:

* Projetos ambientais solicitam a aposentadoria de créditos
* Auditorias on-chain verificam créditos aposentados

---

## 🚀 Deploy dos Contratos

O deploy é realizado via script Foundry localizado em `scripts/Deploy.s.sol`.

### Deploy em rede local (Anvil)

Inicie uma blockchain local:

```bash
anvil
```

Em outro terminal, execute:

```bash
forge script scripts/Deploy.s.sol \
  --rpc-url http://localhost:8545 \
  --private-key <SUA_PRIVATE_KEY> \
  --broadcast
```

### Deploy em Testnet / Mainnet

```bash
forge script scripts/Deploy.s.sol \
  --rpc-url <RPC_URL> \
  --private-key <PRIVATE_KEY> \
  --broadcast --verify
```

> ⚠️ **Atenção:** nunca versionar chaves privadas. Utilize variáveis de ambiente.

---

## 🔐 Variáveis de Ambiente (Recomendado)

```bash
export PRIVATE_KEY=0x...
export RPC_URL=https://...
```

E então:

```bash
forge script scripts/Deploy.s.sol --rpc-url $RPC_URL --private-key $PRIVATE_KEY --broadcast
```

---

## 📊 Interação com os Contratos (Cast)

Exemplo de chamada de função:

```bash
cast call <ENDERECO_CONTRATO> "funcao()"
```

Exemplo de envio de transação:

```bash
cast send <ENDERECO_CONTRATO> "funcao(uint256)" 10 \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

---

## 🧠 Boas Práticas Adotadas

* Uso de bibliotecas **OpenZeppelin**
* Testes automatizados com **forge-std**
* Scripts de deploy reproduzíveis
* Separação clara entre lógica, testes e deploy

---

## 📌 Observações Finais

Este projeto foi desenvolvido com foco acadêmico e experimental, podendo ser estendido para:

* Integração com oráculos (Chainlink, API off-chain)
* Conexão com front-end (React, Next.js)
* Integração com blockchains permissionadas (ex: Hyperledger Besu)

---

<!-- ## 📄 Licença

Este projeto é distribuído sob a licença **MIT**. -->
