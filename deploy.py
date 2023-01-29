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
