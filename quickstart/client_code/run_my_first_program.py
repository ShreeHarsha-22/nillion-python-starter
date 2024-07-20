import asyncio
import random
import os
from dotenv import load_dotenv
from nillion_python_helpers import create_nillion_client, create_payments_config, get_quote_and_pay
from cosmpy.aerial.client import LedgerClient
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from nada_dsl import *

# Load environment variables
load_dotenv()

async def main():
    # Guess the Number game logic
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
                break
        
        except ValueError:
            print("Invalid input! Please enter a valid number.")
    
    # Continue with blockchain interaction
    cluster_id = os.getenv("NILLION_CLUSTER_ID")
    grpc_endpoint = os.getenv("NILLION_NILCHAIN_GRPC")
    chain_id = os.getenv("NILLION_NILCHAIN_CHAIN_ID")
    seed = "my_seed"
    
    # Initialize Nillion client
    userkey = UserKey.from_seed(seed)
    nodekey = NodeKey.from_seed(seed)
    client = create_nillion_client(userkey, nodekey)
    
    # Define NADA DSL structure
    party1 = Party(name="Party1")
    party2 = Party(name="Party2")
    
    attempts_secret = SecretInteger(Input(name="attempts", party=party2))
    
    output_attempts = Output(attempts_secret, "attempts", party1)
    
    # Prepare data for storage
    new_secret = nillion.NadaValues({
        "attempts": attempts
    })
    
    # Set permissions
    permissions = nillion.Permissions.default_for_user(client.user_id)
    permissions.add_compute_permissions({client.user_id: {}})
    
    # Configure payments
    payments_config = create_payments_config(chain_id, grpc_endpoint)
    payments_client = LedgerClient(payments_config)
    private_key = PrivateKey(bytes.fromhex(os.getenv("NILLION_NILCHAIN_PRIVATE_KEY_0")))
    payments_wallet = LocalWallet(private_key, prefix="nillion")
    
    # Get quote and pay for operation
    receipt_store = await get_quote_and_pay(
        client,
        nillion.Operation.store_values(new_secret, ttl_days=5),
        payments_wallet,
        payments_client,
        cluster_id
    )
    
    # Store values on blockchain
    store_id = await client.store_values(cluster_id, new_secret, permissions, receipt_store)
    print(f"Stored attempts: {attempts} on blockchain with store_id: {store_id}")

if __name__ == "__main__":
    asyncio.run(main())
