from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# List of usernames and passwords
users = {
    'Bindu': 'Bindu_123',
    'Eswar': 'Eswar_123',
    'Siva': 'Siva_123',
}

# Generate bcrypt hashes for each user
hashed_users = {user: bcrypt.generate_password_hash(password).decode('utf-8') for user, password in users.items()}

# Print the hashed passwords
for user, hashed_password in hashed_users.items():
    print(f"Username: {user}, Hashed Password: {hashed_password}")