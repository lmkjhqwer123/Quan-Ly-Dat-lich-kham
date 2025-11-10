import secrets
import os

# Generate a URL-safe text string, containing 32 random bytes
secret_key = secrets.token_urlsafe(32)

# Define the path to the .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')

# Read existing .env content
env_content = ""
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        env_content = f.read()

# Check if SECRET_KEY already exists
if "SECRET_KEY=" not in env_content:
    with open(env_path, 'a') as f:
        f.write(f"\nSECRET_KEY={secret_key}\n")
    print(f"Generated SECRET_KEY and added to {env_path}")
else:
    print("SECRET_KEY already exists in .env, skipping generation.")
