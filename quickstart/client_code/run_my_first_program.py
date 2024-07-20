import asyncio
import random
import py_nillion_client as nillion
import os

from py_nillion_client import NodeKey, UserKey
from dotenv import load_dotenv
from nillion_python_helpers import get_quote_and_pay, create_nillion_client, create_payments_config

from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey

# Function for Guess the Number game
def guess_the_number():
    print("Welcome to Guess the Number!")
    print("I'm thinking of a number between 1 and 100.")
    secret_number = random.randint(1, 100)
    attempts = 0
    
    while True:
        guess = input("Enter your guess (or 'quit' to exit): ")
        
        if guess.lower() == 'quit':
            print("Thanks for playing! The secret number was", secret_number)
            return None
        
        try:
            guess = int(guess)
            attempts += 1
            
            if guess < 1 or guess > 100:
                print("Please enter a number between 1 and 100.")
                continue
            
            if guess < secret_number:
                print("Too low! Try again.")
            elif guess > secret_number:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You guessed it right in {attempts} attempts!")
                return attempts
        
        except ValueError:
            print("Invalid input! Please enter a valid number.")

# Async main function integrating Guess the Number game
async def main():
    # Initialization and setup code here
    
    # Integrate Guess the Number game
    attempts = guess_the_number()
    
    if attempts is not None:
        # Continue with blockchain interaction
        # 1. Initial setup
        # 1.1. Get cluster_id, grpc_endpoint, & chain_id from the .env file
        cluster_id = os.getenv("NILLION_CLUSTER_ID")
        grpc_endpoint = os.getenv("NILLION_NILCHAIN_GRPC")
        chain_id = os.getenv("NILLION_NILCHAIN_CHAIN_ID")
        # 1.2 pick a seed and generate user and node keys
        seed = "my_seed"
        userkey = UserKey.from_seed(seed)
        nodekey = NodeKey.from_seed(seed)

        # 2. Initialize NillionClient against nillion-devnet
        # Create Nillion Client for user
        client = create_nillion_client(userkey, nodekey)

        party_id = client.party_id
        user_id = client.user_id

        # Store the number of attempts on the blockchain
        new_secret = nillion.NadaValues(
            {
                "attempts": nillion.SecretInteger(attempts),
            }
        )

        # Set permissions for storing attempts
        permissions = nillion.Permissions.default_for_user(client.user_id)
        permissions.add_compute_permissions({client.user_id: {}})

        # Pay for and store the attempts in the network and print the returned store_id
        payments_config = create_payments_config(chain_id, grpc_endpoint)
        payments_client = LedgerClient(payments_config)
        payments_wallet = LocalWallet(
            PrivateKey(bytes.fromhex(os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0"))),
            prefix="nillion",
        )

        receipt_store = await get_quote_and_pay(
            client,
            nillion.Operation.store_values(new_secret, ttl_days=5),
            payments_wallet,
            payments_client,
            cluster_id,
        )

        store_id = await client.store_values(
            cluster_id, new_secret, permissions, receipt_store
        )

        print(f"Stored attempts: {attempts} on blockchain with store_id: {store_id}")

if __name__ == "__main__":
    asyncio.run(main())
