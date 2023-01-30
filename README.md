# Projektni zadatak - završni ispit

**Predmet:** Informacijska sigurnost i blockchain tehnologije

**Autor:** Toni Baskijera

**Ak. god**: 2022./2023.

## Uvod

U ovom projektnom zadatku cilj je stvoriti jednostavan pametni ugovor u programskom jeziku Solidity koji implementira osnovne funkcije tokena, a zatim ga i testirati i isprobati na lokalnoj testnoj mreži, Ganache.

## Solidity pametni ugovor

Za početak, stvoriti ćemo datoteku `token.sol` i unutar nje definirati licencu pod koju želimo staviti ugovor, te verziju Soliditya koju želimo koristiti za implementaciju ugovora (tokena):

```solidity
// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;
```

Nakon toga, definirati ćemo nekoliko varijabli koje će token koristiti, od kojih će sve biti javne:

```solidity
contract Token {
    address public owner;
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
}
```

gdje je:

- owner - adresa vlasnika ugovora
- name - ime tokena
- symbol - simbol tokena
- decimals - broj decimala podržano od strane tokena
- totalSupply - ukupni broj tokena
- balanceOf - stanje tokena za svaku adresu

Nakon toga, dodati ćemo nekoliko `eventa` koji će se emitirati pri izvršenju određenih funkcija, odnosno transakcija na blockchainu:

```solidity
...

event Transfer(address indexed from, address indexed to, uint256 value);
event Mint(address indexed minter, uint256 value);
event Burn(address indexed burner, uint256 value);

...
```

gdje je:

- transfer - event koji će se emitirati pri transferu tokena s jedne adrese na drugu, javlja koja je adresa poslala, a koja primila tokene, te kolika je količina tokena prenesena
- burn - event koji će se emitirati pri "sagorijevanju" postojećih tokena, a javlja koja je adresa izvršila proces (u našem slučaju uvijek vlasnik tokena), te količinu
- mint - event koji će se emitirati pri stvaranju novih tokena, a javlja koja je adresa izvršila proces (u našem slučaju uvijek vlasnik tokena), te količinu

Sljedeći korak je definiranje konstruktora, specijalne funkcije koja se izvrši pri postavljaju ugovora na blockchain, kojom ćemo incijalizirati sve početne varijable na vrijednosti koje proslijedimo funkciji putem parametara (osim varijble `owner`, čiju vrijednost ne proslijedimo već postavimo na vlasnika ugovora):

```solidity
...

constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _totalSupply
    ) {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _totalSupply;
        balanceOf[msg.sender] = _totalSupply;
    }

...
```

Nakon toga, potrebno je implementirati funkcije za funkcionalnosti koje želimo omogućiti u našem ugovoru.

Prva funkcionalnost koju želimo dodati ugovoru je provjera ukupnog broja tokena. Funkciji `checkTotalSupply` ćemo dodati i oznaku `view`, koja se koristi za označavanje funkcija koje ne mijenjaju stanje ugovora i koristi se samo za čitanje informacija iz njega:

```solidity
...

 function checkTotalSupply() public view returns (uint256) {
        return totalSupply;
    }
...
```

Druga funkcionalnost koju želimo dodati ugovoru je provjera stanja tokena za određenu adresu. Funkciji `check balance` jednostavno prosljedimo adresu, a kao povratnu vrijednost dobijemo stanje našeg tokena na toj adresi. Funkciji ćemo dodati i oznaku `view`:

```solidity
...

function checkBalance(address _owner) public view returns (uint256) {
        return balanceOf[_owner];
    }

...
```

Sljedeća funkcionalnost je mogućnost prijenosa tokena s jedne adrese na drugu. Funkcija `transfer` dostupna je svim adresama i omogućava prijenos tokena s adrese koja poziva funkciju na bilo koju drugu, koju prosljedimo kao parametar, zajedno s količinom tokena.

```solidity
...

function transfer(address _to, uint256 _value) public payable {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance!");
        require(_value > 0, "Transfer value can not be 0!");

        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
    }

...
```

Unutar funkcije željenu količinu jednostavno oduzmemo od adrese koja šalje token i pridodamo ih primatelju. Upotrijebili smo i posebnu funkciju `require` u koju prosljeđujemo uvjet koji mora bit zadovoljen, a to je da količina prijenosa tokena mora biti manja od stanja adrese koju funkcija poziva. Nakon svega emitiramo event `Transfer` kojeg smo prije definirali.

Sljedeća je funkcionalnost "mintanja", odnosno stvaranja postojećih tokena. Funkcija `mint` kao parametar prima količinu novog tokena koju želimo stvoriti:

```solidity
...

 function mint(uint256 _value) public {
        require(msg.sender == owner, "Only owner can mint tokens!");
        require(_value > 0, "Mint value can not be 0!");
        totalSupply += _value;
        balanceOf[msg.sender] += _value;
        emit Mint(msg.sender, _value);
    }
...
```

Unutar funkcije željenu količinu pridodamo adresi koja je pozvala funkciju, te ukupno količinu tokena uvećamo za istu. Postavljen je i uvjet kako bi samo vlasnik ugovora mogao pozvati funkciju `mint`, kao i uvjet da količina mintanja mora biti veća od 0. Nakon svega emitiramo event `Mint` kojeg smo prije definirali.

Za kraj, dodati ćemo funkcionalnost "sagorijevanja", odnosno brisanje postojećih tokena. Funkcija `burn` kao parametar prima količinu novog tokena koju želimo sagorijeti, izbrisati:

```solidity
...

 function burn(uint256 _value) public {
        require(msg.sender == owner, "Only owner can burn tokens!");
        require(
            balanceOf[msg.sender] >= _value,
            "Burn value can't be higher than balance!"
        );
        require(_value > 0, "Burn value can not be 0!");

        balanceOf[msg.sender] -= _value;
        totalSupply -= _value;
        emit Burn(msg.sender, _value);
    }
...
```

Unutar funkcije željenu količinu oduzmemo adresi koja je pozvala funkciju, te ukupno količinu tokena umanjimo za istu. Postavljen je i uvjet kako bi samo vlasnik ugovora mogao pozvati funkciju `burn`, kao i uvjet da količina sagorijevanja mora biti veća od 0. Nakon svega emitiramo event `Burn` kojeg smo prije definirali.

Cjelokupni sadržaj datoteke `token.sol`:

```solidity
// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

contract Token {
    address public owner;
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Mint(address indexed minter, uint256 value);
    event Burn(address indexed burner, uint256 value);

    constructor(
        string memory _name,
        string memory _symbol,
        uint8 _decimals,
        uint256 _totalSupply
    ) {
        owner = msg.sender;
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _totalSupply;
        balanceOf[msg.sender] = _totalSupply;
    }

    function checkBalance(address _owner) public view returns (uint256) {
        return balanceOf[_owner];
    }

    function transfer(address _to, uint256 _value) public payable {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance!");
        require(_value > 0, "Transfer value can not be 0!");

        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
    }

    function mint(uint256 _value) public {
        require(msg.sender == owner, "Only owner can mint tokens!");
        require(_value > 0, "Mint value can not be 0!");
        totalSupply += _value;
        balanceOf[msg.sender] += _value;
        emit Mint(msg.sender, _value);
    }

    function burn(uint256 _value) public {
        require(msg.sender == owner, "Only owner can burn tokens!");
        require(
            balanceOf[msg.sender] >= _value,
            "Burn value can't be higher than balance!"
        );
        require(_value > 0, "Burn value can not be 0!");

        balanceOf[msg.sender] -= _value;
        totalSupply -= _value;
        emit Burn(msg.sender, _value);
    }
}

```

## Testiranje na Ganache testnoj mreži

Za testiranje ugovora koristiti ćemo testnu mrežu Ganache. Pokrenuti ćemo je u Docker kontejneru naredbom `docker run` kojoj ćemo pridodati parametar  `--publish` kojim ćemo izložiti određene portove hostu, te zatim navesti sliku za pokretanje(koju će Docker automatski preuzeti ukoliko je nemamo):

```shell
toni@toni-WRT-WX9:~$ docker run --publish 8545:8545 trufflesuite/ganache-cli:latest
Ganache CLI v6.12.2 (ganache-core: 2.13.2)
(node:1) [DEP0005] DeprecationWarning: Buffer() is deprecated due to security and usability issues. Please use the Buffer.alloc(), Buffer.allocUnsafe(), or Buffer.from() methods instead.
(Use `node --trace-deprecation ...` to show where the warning was created)

Available Accounts
==================
(0) 0x49588a9097F3fDb77F219A800a615Cf006CC10C9 (100 ETH)
(1) 0x6D1235245644f97826a606EBC77c385d467d81a6 (100 ETH)
(2) 0x2DE6cCbAff0F8B2E0E8060D29AA060e973CD7704 (100 ETH)
(3) 0x08B464822851D3fAf47f60C967B5C18D0d655639 (100 ETH)
(4) 0x25b7ec0eC387D907532382bA6d83dB15A92d349d (100 ETH)
(5) 0xE0535f12505685CE6530739F76608b7fACf7E8E4 (100 ETH)
(6) 0xd97D8C5a59589c6f8Dc993eF0f5ebc1469aFaA7b (100 ETH)
(7) 0x2F638Ab361f7188a8CA9a2aA2Ee2f7D6E6cD42B9 (100 ETH)
(8) 0xa746c4552cEdAAe389F8C38e51833Caf20449014 (100 ETH)
(9) 0x94ca0C56385C4DA4E0Df51e0Af5403D695f22AB0 (100 ETH)

Private Keys
==================
(0) 0x62c66bda4990c4615302504684b4e58a34e3a8b992af3bd1399558e5d572f21e
(1) 0x409571f1ebca0153930f9698af3b92e6789143050a721e86f0b5d7d35bcd68e0
(2) 0x29c71c99bd8f626e9f7ad90d949e1557fc199453a071da0af8d751cefd4094fb
(3) 0xd8eef8d98d1dc4eebee60ed90951edeead95ee4aecb7b1b6983bd030aaf0e999
(4) 0xd268dbaf8d7b61957b38b17f0b85a54679a53ca1091678fd7753b32934a505d8
(5) 0x75a19976247db33f34ee99ce3755d2dee5cded4ec43078083b56012a7c8b2a84
(6) 0x4078fa95ef46477af163c54bdaf7a6d3ba954db8531279ae1ad0ad830654ccb4
(7) 0xd6bdfabe46c6140dccbe3215d7b084f1831df7e2deac88b14f190323372b9c35
(8) 0x8cfa057094fcdde86886719ec485ffa5c7221fb94115fa3a0bbf77b1d763c7e2
(9) 0x23de230bd26b3c78eb295222a7d323560a56424a60b9100a3b66bbd42ec801ff

HD Wallet
==================
Mnemonic:      meadow use october spray result gentle weasel timber exist above food enjoy
Base HD Path:  m/44'/60'/0'/0/{account_index}

Gas Price
==================
20000000000

Gas Limit
==================
6721975

Call Gas Limit
==================
9007199254740991

Listening on 0.0.0.0:8545
```

Ganache - CLI je ispisao nekoliko adresa s pripadnim privatnim ključevima, koje ćemo iskoristiti za testiranje funkcionalnosti ugovora. Ne prekidajući Ganache, možemo prijeći na sljedeći korak.

Stvoriti ćemo novu datoteku `deploy.py` u koju ćemo unesti sljedeći sadržaj, kojim ćemo učitati i kompajlirati naš pametni ugovor, a zatim izvući potrebne dijelove:

```py
import json
from web3 import Web3
from solcx import compile_standard, install_solc

install_solc("0.8.0")

# --- CONTRACT COMPILING

# Read the contents of the token.sol contract file
with open("./token.sol", "r") as file:
    token_file = file.read()

# Compile the Solidity contract using the solcx package
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"token.sol": {"content": token_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.0",
)

# Save the compiled contract's bytecode and ABI to a local file
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Extract bytecode from the compiled contract
bytecode = compiled_sol["contracts"]["token.sol"]["Token"]["evm"]["bytecode"]["object"]

# Extract ABI from the compiled contract
abi = compiled_sol["contracts"]["token.sol"]["Token"]["abi"]

```

Ukoliko se javlja greška o nedostatku modula `solcx`, potrebno ga je instalirati naredbom `pip3 install py-solc-x`.

Nadalje, deployati ćemo ugovor na testnoj mreži, pritom mu prosljeđujući potrebne parametre putem konstruktora. Kao vlastitu potrebno je unesti jednu od prije ispisanih adresa, zajedno s pripadajućim ključem:

```py
...

# --- CONNECTING TO GANACHE AND DEPLOYING THE CONTRACT

# Connect to ganache
w3 = Web3(Web3.HTTPProvider("http://0.0.0.0:8545"))
chain_id = 1337
my_address = input('Enter your address: ')
private_key = input('Enter your private key: ')
name = input("Enter token name: ")
symbol = input("Enter token symbol: ").upper()
decimals = input("Enter token decimals: ")
total_supply = input("Enter total supply: ")

# Create the contract in python
Token = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the nonce
nonce = w3.eth.getTransactionCount(my_address)

# Build a transaction
transaction = Token.constructor(name, symbol, int(decimals), int(total_supply)).build_transaction(
    {"chainId": chain_id, "from": my_address,
        "nonce": nonce, "gasPrice": w3.eth.gas_price}
)

# Sign a transaction
signed_txn = w3.eth.account.sign_transaction(
    transaction, private_key=private_key)

# Send the signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
```

U posljednjem dijelu `deploy.py` datoteke, kreirati ćemo jednostavni meni koji odgovara funkcijama ugovora. Važno je napomenuti da je pri svakom pozivanju funkcija koje mijenjanju stanje blockchaina potrebno uvećati takozvani `nonce`, jedinstveni broj koji se može koristiti samo jednom unutar blockchaina s ciljem sprječavanja *replay napada*:

```py
...

# --- BLOCKCHAIN INTERACTION

token = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

while True:
    print("\nMENU\n-----")
    print("1. Check total supply")
    print("2. Check balance")
    print("3. Transfer")
    print("4. Mint")
    print("5. Burn")
    print("6. Exit")
    choice = int(input("\nEnter your choice:"))

    if choice == 1:
        print("Total supply of " + symbol + " token is " +
              str(token.functions.checkTotalSupply().call()))

    elif choice == 2:
        address = input("Enter address: ")
        print("Address " + str(address) + " has " +
              str(token.functions.checkBalance(my_address).call()) + symbol)

    elif choice == 3:
        nonce += 1
        receiver = input("Enter reciever address: ")
        transfer_value = input("Enter transfer amount: ")
        print("\nBefore transfer")
        print("Your account balance: " +
              str(token.functions.checkBalance(my_address).call()) + symbol)
        print("Receiver balance: " +
              str(token.functions.checkBalance(receiver).call()) + symbol)

        store_transaction = token.functions.transfer(receiver, int(transfer_value)).buildTransaction(
            {"chainId": chain_id, "from": my_address,
                "nonce": nonce, "gasPrice": w3.eth.gas_price}
        )
        signed_store_txn = w3.eth.account.sign_transaction(
            store_transaction, private_key=private_key
        )

        send_store_tx = w3.eth.send_raw_transaction(
            signed_store_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

        print("\nAfter transfer")
        print("Your account balance: " +
              str(token.functions.checkBalance(my_address).call()) + symbol)
        print("Receiver balance: " +
              str(token.functions.checkBalance(receiver).call()) + symbol)

    elif choice == 4:
        nonce += 1
        mint_value = input("Enter mint amount: ")
        print("\nTotal supply of " + symbol + " token before mint is " +
              str(token.functions.checkTotalSupply().call()))
        print("Before mint your account balance: " +
              str(token.functions.checkBalance(my_address).call()) + symbol)

        store_transaction = token.functions.mint(int(mint_value)).buildTransaction(
            {"chainId": chain_id, "from": my_address,
                "nonce": nonce, "gasPrice": w3.eth.gas_price}
        )
        signed_store_txn = w3.eth.account.sign_transaction(
            store_transaction, private_key=private_key
        )

        send_store_tx = w3.eth.send_raw_transaction(
            signed_store_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

        print("Total supply of " + symbol + " token  after mint is " +
              str(token.functions.checkTotalSupply().call()))
        print("After mint your account balance is: " +
              str(token.functions.checkBalance(my_address).call()) + symbol)

    elif choice == 5:
        nonce += 1
        burn_value = input("Enter burn amount: ")
        print("\nTotal supply of " + symbol + " token before burn is " +
              str(token.functions.checkTotalSupply().call()))
        print("Before burn your account balance was: " +
              str(token.functions.checkBalance(my_address).call()) + symbol)

        store_transaction = token.functions.burn(int(burn_value)).buildTransaction(
            {"chainId": chain_id, "from": my_address,
                "nonce": nonce, "gasPrice": w3.eth.gas_price}
        )
        signed_store_txn = w3.eth.account.sign_transaction(
            store_transaction, private_key=private_key
        )

        send_store_tx = w3.eth.send_raw_transaction(
            signed_store_txn.rawTransaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

        print("Total supply of " + symbol + " token after burn is " +
              str(token.functions.checkTotalSupply().call()))
        print("After burn your account balance is: " +
              str(token.functions.checkBalance(my_address).call()) + symbol)

    elif choice == 6:
        break

    else:
        print("Wrong Choice")

    repeat = input("\nDo you want to continue? (y/n)")
    if repeat == 'n' or repeat == 'N':
        break

```

Sada kada je sve spremno, možemo i pokrenuti `deploy.py` datoteku, pa testirati sve funkcionalnosti:

```shell
toni@toni-WRT-WX9:~/solidity-project$ python3 deploy.py
Enter your address: 0x49588a9097F3fDb77F219A800a615Cf006CC10C9
Enter your private key: 0x62c66bda4990c4615302504684b4e58a34e3a8b992af3bd1399558e5d572f21e
Enter token name: Blockchain
Enter token symbol: ISBIT
Enter token decimals: 18
Enter total supply: 100

MENU
-----
1. Check total supply
2. Check balance
3. Transfer
4. Mint
5. Burn
6. Exit

Enter your choice:1
Total supply of ISBIT token is 100

Do you want to continue? (y/n)y

MENU
-----
1. Check total supply
2. Check balance
3. Transfer
4. Mint
5. Burn
6. Exit

Enter your choice:2
Enter address: 0x49588a9097F3fDb77F219A800a615Cf006CC10C9
Address 0x49588a9097F3fDb77F219A800a615Cf006CC10C9 has 100ISBIT

Do you want to continue? (y/n)y

MENU
-----
1. Check total supply
2. Check balance
3. Transfer
4. Mint
5. Burn
6. Exit

Enter your choice:3
Enter reciever address: 0x6D1235245644f97826a606EBC77c385d467d81a6
Enter transfer amount: 30

Before transfer
Your account balance: 100ISBIT
Receiver balance: 0ISBIT

After transfer
Your account balance: 70ISBIT
Receiver balance: 30ISBIT

Do you want to continue? (y/n)y

MENU
-----
1. Check total supply
2. Check balance
3. Transfer
4. Mint
5. Burn
6. Exit

Enter your choice:4
Enter mint amount: 100

Total supply of ISBIT token before mint is 100
Before mint your account balance: 70ISBIT
Total supply of ISBIT token  after mint is 200
After mint your account balance is: 170ISBIT

Do you want to continue? (y/n)y

MENU
-----
1. Check total supply
2. Check balance
3. Transfer
4. Mint
5. Burn
6. Exit

Enter your choice:5
Enter burn amount: 100

Total supply of ISBIT token before burn is 200
Before burn your account balance was: 170ISBIT
Total supply of ISBIT token after burn is 100
After burn your account balance is: 70ISBIT

Do you want to continue? (y/n)n

```

U ganache-cli možemo vidjeti i ispisane transakcije:

```shell
...

Listening on 0.0.0.0:8545
eth_getTransactionCount
eth_gasPrice
eth_chainId
eth_estimateGas
eth_sendRawTransaction

  Transaction: 0x65683968c9dd77d77b9cefca4bbf6fc9aee9b5e61751dca45b735264cf28feb9
  Contract created: 0x6968a3e660b55a42f4be2230d499f7fd61f6b645
  Gas usage: 1068253
  Block Number: 1
  Block Time: Sun Jan 29 2023 18:21:41 GMT+0000 (Coordinated Universal Time)

eth_getTransactionReceipt
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_gasPrice
eth_chainId
eth_estimateGas
eth_sendRawTransaction

  Transaction: 0xaec4e7bcac186ba059af26e8d0aced5702931d1f90b5a68cd406b8453b5991a4
  Gas usage: 52421
  Block Number: 2
  Block Time: Sun Jan 29 2023 18:23:01 GMT+0000 (Coordinated Universal Time)

eth_getTransactionReceipt
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_gasPrice
eth_chainId
eth_estimateGas
eth_sendRawTransaction

  Transaction: 0xaefd3f3a2ce2484cb7579be149e9a1c7ea2fd9abb19bd97dd5ee067d6e4e496d
  Gas usage: 36271
  Block Number: 3
  Block Time: Sun Jan 29 2023 18:23:29 GMT+0000 (Coordinated Universal Time)

eth_getTransactionReceipt
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_chainId
eth_call
eth_gasPrice
eth_chainId
eth_estimateGas
eth_sendRawTransaction

  Transaction: 0x608dc3c68a8d8e213803df1392dd6a0a3b7f49749a69d43205053d6ef63fcde9
  Gas usage: 37175
  Block Number: 4
  Block Time: Sun Jan 29 2023 18:23:49 GMT+0000 (Coordinated Universal Time)

eth_getTransactionReceipt
eth_chainId
eth_call
eth_chainId
eth_call

```

## GitHub poveznica

<https://github.com/tbaskijera/solidity-project>

## Literatura

- [1] <https://web3py.readthedocs.io/en/v5/#>
- [2] <https://trufflesuite.com/docs/ganache/>
