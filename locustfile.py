import time
import random
import json
import os
from locust import User, task, events, between
from web3 import Web3

# --- CONFIGURAÇÕES ---
RPC_URL = "http://127.0.0.1:8545"

# PREENCHA COM SEUS ENDEREÇOS ATUAIS (O script converte para Checksum automaticamente)
# Certifique-se de que estes endereços foram gerados na sessão ATUAL do Anvil
FOREST_ADDRESS = Web3.to_checksum_address("0xC66AB83418C20A65C3f8e83B3d11c8C3a6097b6F") 
CARBON_ADDRESS = Web3.to_checksum_address("0xeF31027350Be2c7439C1b0BE022d49421488b72C") 

ANVIL_PRIVATE_KEYS = [
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffbb",
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",
    "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",
    "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6"
]

# --- UTILITÁRIOS ---
def load_abi_safe(filename):
    """Tenta carregar o ABI de forma segura e extrai a lista correta."""
    if not os.path.exists(filename):
        print(f"CRÍTICO: Arquivo ABI '{filename}' não encontrado no diretório atual.")
        return None
        
    try:
        with open(filename, 'r') as f:
            content = json.load(f)
            # Suporte tanto para arquivo puro quanto artefato do Foundry
            if isinstance(content, dict) and 'abi' in content:
                return content['abi']
            elif isinstance(content, list):
                return content
            else:
                print(f"CRÍTICO: Formato JSON inválido em '{filename}'.")
                return None
    except Exception as e:
        print(f"CRÍTICO: Erro ao ler '{filename}': {e}")
        return None

# Carregamento dos ABIs
FOREST_ABI = load_abi_safe('out/forestMonitor.sol/forestMonitor.json') 
CARBON_ABI = load_abi_safe('out/carbonRetirement.sol/CarbonRetirement.json')

# Validação inicial para não rodar se faltar arquivo
if not FOREST_ABI or not CARBON_ABI:
    print("--- PARANDO EXECUÇÃO: Faltam arquivos ABI ---")
    exit(1)

# Tópico do evento Transfer(address,address,uint256)
TRANSFER_TOPIC = Web3.keccak(text="Transfer(address,address,uint256)").hex()

class CarbonRetirementUser(User):
    wait_time = between(1, 3)

    def on_start(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.forest = self.w3.eth.contract(address=FOREST_ADDRESS, abi=FOREST_ABI)
        self.carbon = self.w3.eth.contract(address=CARBON_ADDRESS, abi=CARBON_ABI)
        
        self.private_key = random.choice(ANVIL_PRIVATE_KEYS)
        self.account = self.w3.eth.account.from_key(self.private_key)

    def _setup_mint_token(self):
        """
        Gera token silenciosamente. Retorna ID ou None se falhar.
        """
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')
            
            tx = self.forest.functions.createforestRecord(
                f"SETUP_{random.randint(1,999999)}", "SetupArea", "2024", "2023", "0,0", 100, 500
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            for log in receipt['logs']:
                if log['topics'][0].hex() == TRANSFER_TOPIC:
                    return int(log['topics'][3].hex(), 16)
            return None
        except Exception as e:
            # Imprime erro de setup para ajudar no debug, mas não reporta ao Locust
            print(f"[SETUP MINT ERROR] {type(e).__name__}: {e}")
            return None

    @task(1)
    def test_retire_credit(self):
        """
        TESTE DE ESCRITA: Aposenta o crédito.
        """
        # 1. Setup (Invisível)
        token_id = self._setup_mint_token()
        
        if token_id is None:
            # Se falhou o setup, retornamos. O print acima já mostrou o porquê.
            return 

        # 2. Ação (Medida)
        start_time = time.time()
        name = "retireCredit"

        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')

            tx = self.carbon.functions.retireCredit(token_id).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt['status'] == 1:
                total_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="TX", name=name, 
                    response_time=total_time, response_length=0, exception=None
                )
            else:
                raise Exception("Transação reverteu (Status 0)")

        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            # Imprime erro crítico no terminal para você ver o que é
            print(f"[WRITE ERROR] {name}: {e}")
            
            events.request.fire(
                request_type="TX", name=name, 
                response_time=total_time, response_length=0, exception=e
            )

    @task(3)
    def test_is_retired_view(self):
        """
        TESTE DE LEITURA
        """
        check_id = random.randint(1, 50)
        start_time = time.time()
        name = "isRetired"

        try:
            self.carbon.functions.isRetired(check_id).call()
            
            total_time = int((time.time() - start_time) * 1000)
            events.request.fire(
                request_type="READ", name=name, 
                response_time=total_time, response_length=0, exception=None
            )
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            
            # --- DEBUG IMPORTANTE ---
            # Isso vai mostrar se é BadFunctionCallOutput (ABI/Endereço errado)
            # ou ConnectionError (RPC fora do ar)
            print(f"[READ ERROR] {name}: {type(e).__name__} - {e}")

            events.request.fire(
                request_type="READ", name=name, 
                response_time=total_time, response_length=0, exception=e
            )