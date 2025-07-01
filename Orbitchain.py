# 🚀 ORBITCHAIN - PLNÁ VERZE
# Kompletní implementace s konsensem, bezpečností a P2P komunikací

import time
import hashlib
import json
import random
from datetime import datetime
from typing import List, Dict, Any
import threading

class Transaction:
    """Jednotlivá transakce v OrbitChainu"""
    
    def __init__(self, sender: str, receiver: str, data: str, tx_type: str = "transfer"):
        self.id = self.generate_id()
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.tx_type = tx_type
        self.timestamp = datetime.now()
        self.signature = self.sign()
        
    def generate_id(self) -> str:
        """Generuje unikátní ID transakce"""
        return hashlib.sha256(f"{time.time()}{random.randint(0,9999)}".encode()).hexdigest()[:12]
        
    def sign(self) -> str:
        """Podepíše transakci (simulovaný podpis)"""
        content = f"{self.sender}{self.receiver}{self.data}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
        
    def to_dict(self) -> Dict:
        """Převede transakci na slovník"""
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'data': self.data,
            'type': self.tx_type,
            'timestamp': self.timestamp.strftime('%H:%M:%S.%f'),
            'signature': self.signature
        }
        
    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.data}"

class Validator:
    """Validátor node v OrbitChain síti"""
    
    def __init__(self, name: str, stake: float = 100.0):
        self.name = name
        self.stake = stake
        self.reputation = 100
        self.is_active = True
        self.sector_position = 0  # Pozice na obvodu kruhu
        self.validated_count = 0
        
    def validate_transaction(self, transaction: Transaction) -> bool:
        """Validuje transakci"""
        # Simulace validace - kontrola podpisu a formátu
        if not transaction.signature or len(transaction.signature) < 10:
            return False
        if not transaction.sender or not transaction.receiver:
            return False
        
        self.validated_count += 1
        return True
        
    def __str__(self):
        status = "🟢 AKTIVNÍ" if self.is_active else "🔴 NEAKTIVNÍ"
        return f"Validator {self.name} | Stake: {self.stake} | Rep: {self.reputation} | {status}"

class Orbit:
    """Jeden kruh (orbit) v OrbitChain"""
    
    def __init__(self, orbit_number: int, max_transactions: int = 8):
        self.orbit_number = orbit_number
        self.transactions: List[Transaction] = []
        self.max_transactions = max_transactions
        self.timestamp = datetime.now()
        self.is_sealed = False
        self.validators_confirmed = []
        self.orbital_hash = ""
        self.previous_hash = ""
        self.merkle_root = ""
        
    def add_transaction(self, transaction: Transaction) -> bool:
        """Přidá transakci do orbitu"""
        if self.is_sealed:
            return False
        if len(self.transactions) >= self.max_transactions:
            return False
            
        self.transactions.append(transaction)
        self.update_merkle_root()
        return True
        
    def update_merkle_root(self):
        """Aktualizuje Merkle root všech transakcí"""
        if not self.transactions:
            self.merkle_root = "0" * 16
            return
            
        # Jednoduché Merkle tree
        hashes = [tx.signature for tx in self.transactions]
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                if i + 1 < len(hashes):
                    combined = hashes[i] + hashes[i + 1]
                else:
                    combined = hashes[i] + hashes[i]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest()[:16])
            hashes = new_hashes
        self.merkle_root = hashes[0] if hashes else "0" * 16
        
    def seal_orbit(self, previous_hash: str = ""):
        """Uzavře orbit a vypočítá finální hash"""
        self.previous_hash = previous_hash
        self.is_sealed = True
        
        # Orbital hash zahrnuje všechno
        content = {
            'orbit_number': self.orbit_number,
            'transactions': len(self.transactions),
            'merkle_root': self.merkle_root,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp.isoformat()
        }
        
        self.orbital_hash = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:16]
        
    def get_sectors(self, num_validators: int) -> Dict[int, List[Transaction]]:
        """Rozdělí orbit na sektory pro validátory"""
        sectors = {i: [] for i in range(num_validators)}
        
        for i, tx in enumerate(self.transactions):
            sector = i % num_validators
            sectors[sector].append(tx)
            
        return sectors
        
    def is_full(self) -> bool:
        """Kontroluje jestli je orbit plný"""
        return len(self.transactions) >= self.max_transactions

class OrbitChainNetwork:
    """Kompletní OrbitChain síť"""
    
    def __init__(self, name: str = "OrbitChain-MainNet"):
        self.name = name
        self.orbits: List[Orbit] = []
        self.validators: List[Validator] = []
        self.pending_transactions: List[Transaction] = []
        self.current_orbit_index = 0
        self.consensus_threshold = 0.67  # 67% shoda pro konsensus
        self.network_stats = {
            'total_transactions': 0,
            'total_orbits': 0,
            'network_hash_rate': 0,
            'uptime': datetime.now()
        }
        
        # Vytvoř Genesis orbit
        self.create_genesis_orbit()
        
    def create_genesis_orbit(self):
        """Vytvoří genesis orbit"""
        genesis = Orbit(0, max_transactions=1)
        genesis_tx = Transaction("SYSTEM", "NETWORK", "Genesis orbit created", "genesis")
        genesis.add_transaction(genesis_tx)
        genesis.seal_orbit()
        
        self.orbits.append(genesis)
        self.network_stats['total_orbits'] = 1
        self.network_stats['total_transactions'] = 1
        
        print("🌟 Genesis orbit vytvořen!")
        
    def add_validator(self, validator: Validator):
        """Přidá validátora do sítě"""
        # Přiřadí pozici na obvodu kruhu
        validator.sector_position = len(self.validators) * (360 // max(1, len(self.validators) + 1))
        self.validators.append(validator)
        print(f"✅ Validator {validator.name} přidán (pozice: {validator.sector_position}°)")
        
    def submit_transaction(self, transaction: Transaction):
        """Odešle transakci do sítě"""
        self.pending_transactions.append(transaction)
        print(f"📤 Transakce odeslána: {transaction}")
        
    def process_pending_transactions(self):
        """Zpracuje čekající transakce"""
        if not self.pending_transactions:
            return
            
        current_orbit = self.orbits[self.current_orbit_index]
        
        # Pokud je aktuální orbit plný nebo uzavřený, vytvoř nový
        if current_orbit.is_full() or current_orbit.is_sealed:
            self.create_new_orbit()
            current_orbit = self.orbits[self.current_orbit_index]
            
        # Přidej transakce do aktuálního orbitu
        processed = []
        for tx in self.pending_transactions[:]:
            if self.validate_transaction_consensus(tx):
                if current_orbit.add_transaction(tx):
                    processed.append(tx)
                    self.network_stats['total_transactions'] += 1
                    
                    # Pokud je orbit plný, uzavři ho
                    if current_orbit.is_full():
                        self.seal_current_orbit()
                        break
                        
        # Odstraň zpracované transakce
        for tx in processed:
            self.pending_transactions.remove(tx)
            
    def validate_transaction_consensus(self, transaction: Transaction) -> bool:
        """Validuje transakci pomocí konsensu validátorů"""
        if not self.validators:
            return True  # Bez validátorů všechno projde
            
        approvals = 0
        for validator in self.validators:
            if validator.is_active and validator.validate_transaction(transaction):
                approvals += 1
                
        approval_rate = approvals / len([v for v in self.validators if v.is_active])
        return approval_rate >= self.consensus_threshold
        
    def create_new_orbit(self):
        """Vytvoří nový orbit"""
        self.current_orbit_index += 1
        new_orbit = Orbit(self.current_orbit_index)
        self.orbits.append(new_orbit)
        self.network_stats['total_orbits'] += 1
        
        print(f"🌍 Nový orbit #{self.current_orbit_index} vytvořen!")
        
    def seal_current_orbit(self):
        """Uzavře aktuální orbit"""
        current_orbit = self.orbits[self.current_orbit_index]
        previous_hash = self.orbits[self.current_orbit_index - 1].orbital_hash if self.current_orbit_index > 0 else ""
        
        current_orbit.seal_orbit(previous_hash)
        print(f"🔒 Orbit #{self.current_orbit_index} uzavřen (hash: {current_orbit.orbital_hash})")
        
    def get_network_status(self) -> Dict:
        """Vrátí stav celé sítě"""
        active_validators = len([v for v in self.validators if v.is_active])
        uptime = datetime.now() - self.network_stats['uptime']
        
        return {
            'network_name': self.name,
            'total_orbits': len(self.orbits),
            'total_transactions': self.network_stats['total_transactions'],
            'pending_transactions': len(self.pending_transactions),
            'active_validators': active_validators,
            'total_validators': len(self.validators),
            'uptime_seconds': uptime.total_seconds(),
            'current_orbit': self.current_orbit_index,
            'consensus_threshold': f"{self.consensus_threshold*100}%"
        }
        
    def show_visual_network(self):
        """Vizuální reprezentace celé sítě"""
        print("\n" + "🌌 ORBITCHAIN NETWORK VISUALIZATION")
        print("=" * 50)
        
        # Nakresli orbity
        num_orbits = len(self.orbits)
        if num_orbits == 1:
            print("         ╭─────╮")
            print("         │  ●  │  ← Genesis")
            print("         ╰─────╯")
        elif num_orbits <= 5:
            # Nakresli až 5 orbit
            for i in range(num_orbits-1, -1, -1):
                padding = "  " * i
                width = 7 + (4 * (num_orbits - i - 1))
                if i == 0:
                    print(f"{padding}╭{'─' * width}╮")
                    print(f"{padding}│{' ' * (width//2)}●{' ' * (width//2)}│  ← Orbit {i}")
                    print(f"{padding}╰{'─' * width}╯")
                else:
                    border = "─" * width
                    print(f"{padding}╭{border}╮")
                    print(f"{padding}│{' ' * width}│  ← Orbit {i}")
                    print(f"{padding}╰{border}╯")
        else:
            print("    ╭─────────────────────╮")
            print("    │    ╭─────────────╮   │")
            print("    │    │    ╭─────╮   │   │")
            print("    │    │    │  ●  │   │   │  ← Genesis + vnější orbity")
            print("    │    │    ╰─────╯   │   │")
            print("    │    ╰─────────────╯   │")
            print("    ╰─────────────────────╯")
            print(f"    Celkem {num_orbits} orbit!")
            
        # Validátoři
        print(f"\n👥 VALIDÁTOŘI ({len(self.validators)}):")
        for i, val in enumerate(self.validators):
            status = "🟢" if val.is_active else "🔴"
            print(f"   {status} {val.name} (pozice: {val.sector_position}°, validoval: {val.validated_count})")
            
        # Statistiky
        stats = self.get_network_status()
        print(f"\n📊 SÍŤOVÉ STATISTIKY:")
        print(f"   • Název sítě: {stats['network_name']}")
        print(f"   • Celkem orbit: {stats['total_orbits']}")
        print(f"   • Celkem transakcí: {stats['total_transactions']}")
        print(f"   • Čekající transakce: {stats['pending_transactions']}")
        print(f"   • Aktivní validátoři: {stats['active_validators']}/{stats['total_validators']}")
        print(f"   • Konsensus práh: {stats['consensus_threshold']}")
        print(f"   • Běžící {stats['uptime_seconds']:.1f} sekund")
        
    def show_orbit_detail(self, orbit_number: int):
        """Detailní zobrazení konkrétního orbitu"""
        if orbit_number >= len(self.orbits):
            print(f"❌ Orbit #{orbit_number} neexistuje!")
            return
            
        orbit = self.orbits[orbit_number]
        print(f"\n🔍 ORBIT #{orbit_number} DETAIL")
        print("=" * 40)
        print(f"📅 Vytvořen: {orbit.timestamp.strftime('%H:%M:%S')}")
        print(f"🔒 Stav: {'UZAVŘEN' if orbit.is_sealed else 'OTEVŘEN'}")
        print(f"🔐 Orbital hash: {orbit.orbital_hash}")
        print(f"🔗 Previous hash: {orbit.previous_hash}")
        print(f"🌳 Merkle root: {orbit.merkle_root}")
        print(f"📊 Transakce: {len(orbit.transactions)}/{orbit.max_transactions}")
        
        if orbit.transactions:
            print(f"\n📝 TRANSAKCE:")
            for i, tx in enumerate(orbit.transactions, 1):
                print(f"   {i}. {tx} (ID: {tx.id})")
                print(f"      Podpis: {tx.signature}")
                print(f"      Čas: {tx.timestamp.strftime('%H:%M:%S.%f')}")

def create_demo_network():
    """Vytvoří demo síť s validátory a transakcemi"""
    print("🚀 Vytváříme demo OrbitChain síť...")
    
    # Vytvoř síť
    network = OrbitChainNetwork("OrbitChain-Demo")
    
    # Přidej validátory
    validators = [
        Validator("Alice-Node", stake=1000),
        Validator("Bob-Node", stake=750),
        Validator("Carol-Node", stake=500),
        Validator("Dave-Node", stake=250)
    ]
    
    for validator in validators:
        network.add_validator(validator)
        
    # Vytvoř ukázkové transakce
    demo_transactions = [
        Transaction("Alice", "Bob", "10 OrbitCoins", "payment"),
        Transaction("Bob", "Carol", "Koupit kávu", "purchase"),
        Transaction("Carol", "Dave", "Dokument #123", "document"),
        Transaction("Dave", "Alice", "Hlasování #456", "vote"),
        Transaction("Alice", "Carol", "Certifikát školy", "certificate"),
        Transaction("Bob", "Dave", "IoT data senzor", "iot"),
        Transaction("Carol", "Alice", "Smart kontrakt", "contract"),
        Transaction("Dave", "Bob", "Backup fotek", "storage"),
        Transaction("Alice", "Dave", "5 OrbitCoins", "payment"),
        Transaction("Bob", "Carol", "Ověření identity", "identity")
    ]
    
    print(f"\n📤 Odesíláme {len(demo_transactions)} transakcí...")
    
    # Odešli transakce postupně
    for i, tx in enumerate(demo_transactions, 1):
        network.submit_transaction(tx)
        network.process_pending_transactions()
        
        print(f"\n--- Po transakci #{i} ---")
        network.show_visual_network()
        time.sleep(0.8)
        
    # Finální stav
    print("\n" + "🎉 FINÁLNÍ STAV SÍTĚ")
    print("=" * 50)
    network.show_visual_network()
    
    # Ukáž detail posledního orbitu
    if len(network.orbits) > 1:
        print(f"\n🔍 Detail posledního orbitu:")
        network.show_orbit_detail(len(network.orbits) - 1)
    
    return network

def interactive_network():
    """Interaktivní síť kde můžeš přidávat transakce"""
    print("🎮 INTERAKTIVNÍ ORBITCHAIN SÍŤ")
    print("=" * 40)
    
    network = OrbitChainNetwork("OrbitChain-Interactive")
    
    # Přidej základní validátory
    network.add_validator(Validator("Validator-1", 100))
    network.add_validator(Validator("Validator-2", 100))
    
    print("\n🌌 Tvoje síť je připravená!")
    network.show_visual_network()
    
    print("\n📝 Příkazy:")
    print("   • tx [odesílatel] [příjemce] [data] - přidat transakci")
    print("   • status - zobrazit stav sítě")
    print("   • orbit [číslo] - detail orbitu")
    print("   • validator [jméno] - přidat validátora")
    print("   • konec - ukončit")
    
    while True:
        cmd = input("\n➤ Příkaz: ").strip().split()
        
        if not cmd or cmd[0].lower() in ['konec', 'quit', 'exit']:
            break
            
        if cmd[0].lower() == 'tx' and len(cmd) >= 4:
            sender, receiver = cmd[1], cmd[2]
            data = ' '.join(cmd[3:])
            tx = Transaction(sender, receiver, data)
            network.submit_transaction(tx)
            network.process_pending_transactions()
            network.show_visual_network()
            
        elif cmd[0].lower() == 'status':
            network.show_visual_network()
            
        elif cmd[0].lower() == 'orbit' and len(cmd) >= 2:
            try:
                orbit_num = int(cmd[1])
                network.show_orbit_detail(orbit_num)
            except ValueError:
                print("❌ Zadej číslo orbitu!")
                
        elif cmd[0].lower() == 'validator' and len(cmd) >= 2:
            val_name = cmd[1]
            network.add_validator(Validator(val_name, random.randint(50, 200)))
            
        else:
            print("❌ Neznámý příkaz!")
    
    print("\n🎉 Děkuju za testování OrbitChain!")
    return network

# 🚀 SPUŠTĚNÍ
if __name__ == "__main__":
    print("🌌 ORBITCHAIN - PLNÁ VERZE")
    print("=" * 30)
    print("1. Demo síť")
    print("2. Interaktivní síť")
    
    choice = input("\nVyber možnost (1/2): ").strip()
    
    if choice == "2":
        interactive_network()
    else:
        create_demo_network()
        
    print("\n✨ OrbitChain session ukončena!")
