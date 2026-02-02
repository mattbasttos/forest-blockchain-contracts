import time
import random
import json
import os
from locust import User, task, events, between
from web3 import Web3

# --- CONFIGURAÇÕES ---
RPC_URL = "http://127.0.0.1:8545"

# Preencher com os dados de contratos reais
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3" 

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

abi_path = 'out/forestMonitor.sol/forestMonitor.json'
if not os.path.exists(abi_path):
    print(f"ERRO: Arquivo não encontrado em {abi_path}")
    exit(1)

with open(abi_path, 'r') as f:
    artifact = json.load(f)
    CONTRACT_ABI = artifact['abi']

class ForestMonitorUser(User):
    wait_time = between(1, 3)
    
    last_minted_id = 0 

    def on_start(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.contract = self.w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
        self.private_key = random.choice(ANVIL_PRIVATE_KEYS)
        self.account = self.w3.eth.account.from_key(self.private_key)

    @task(1)
    def create_record(self):
        start_time = time.time()
        name = "createforestRecord"
        
        try:
            # Pega nonce 'pending' para evitar colisão na fila
            nonce = self.w3.eth.get_transaction_count(self.account.address, 'pending')

            tx = self.contract.functions.createforestRecord(
                f"IMG_{random.randint(1,99999)}",
                "Amazonia", "2023", "2022", "-3.00,-60.00", 100, 500
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            
            # --- CORREÇÃO AQUI: .raw_transaction (snake_case) ---
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Espera minerar
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                ForestMonitorUser.last_minted_id += 1
                
                total_time = int((time.time() - start_time) * 1000)
                events.request.fire(
                    request_type="WRITE", name=name, 
                    response_time=total_time, response_length=0, exception=None
                )
            else:
                raise Exception("Transação falhou (revert)")

        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            # Ignora erros de nonce temporários para não poluir o gráfico
            if "nonce" in str(e).lower() or "replacement" in str(e).lower():
                pass
            else:
                events.request.fire(
                    request_type="WRITE", name=name, 
                    response_time=total_time, response_length=0, exception=e
                )

    @task(3)
    def get_record(self):
        if ForestMonitorUser.last_minted_id < 1:
            return

        token_id = random.randint(1, ForestMonitorUser.last_minted_id)
        
        start_time = time.time()
        name = "getforestRecord"

        try:
            self.contract.functions.getforestRecord(token_id).call()
            
            events.request.fire(
                request_type="READ", name=name, 
                response_time=int((time.time() - start_time) * 1000), 
                response_length=0, exception=None
            )
        except Exception as e:
            events.request.fire(
                request_type="READ", name=name, 
                response_time=int((time.time() - start_time) * 1000), 
                response_length=0, exception=e
            )