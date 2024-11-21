import os
import hashlib
from datetime import datetime

class UserModel:
    db_path = "database/users.txt"

    @staticmethod
    def hash_password(password):
        """Hash the password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def ensure_database_exists():
        """Ensure the main user database file exists."""
        if not os.path.exists(UserModel.db_path):
            os.makedirs(os.path.dirname(UserModel.db_path), exist_ok=True)
            with open(UserModel.db_path, "w") as file:
                pass  # Create an empty file

    @staticmethod
    def save_user(name, surname, phone, id_number, email, username, password):
        """Save user details to the database file and create a default account."""
        UserModel.ensure_database_exists()
        try:
            with open(UserModel.db_path, "a") as file:
                # Default balance is set to 0.0
                file.write(f"{name},{surname},{phone},{id_number},{email},{username},{UserModel.hash_password(password)},0.0\n")
            # Create a default "Savings" account for the new user
            UserModel.add_account(username, "Savings", 0.0)
        except Exception as e:
            print(f"Error saving user: {e}")

    @staticmethod
    def get_user(username):
        """Retrieve a user's details by username."""
        UserModel.ensure_database_exists()
        try:
            with open(UserModel.db_path, "r") as file:
                for line in file:
                    data = line.strip().split(",")
                    if data[5] == username:  # Username is the 6th field
                        return {
                            "name": data[0],
                            "surname": data[1],
                            "phone": data[2],
                            "id_number": data[3],
                            "email": data[4],
                            "username": data[5],
                            "password_hash": data[6],
                            "balance": float(data[7]),  # Balance is the last field
                        }
        except Exception as e:
            print(f"Error retrieving user: {e}")
        return None

    @staticmethod
    def update_balance(username, new_balance):
        """Update the user's balance in the main database."""
        UserModel.ensure_database_exists()
        lines = []
        try:
            with open(UserModel.db_path, "r") as file:
                for line in file:
                    data = line.strip().split(",")
                    if data[5] == username:
                        data[7] = str(new_balance)  # Update balance
                    lines.append(",".join(data))

            with open(UserModel.db_path, "w") as file:
                for line in lines:
                    file.write(line + "\n")
        except Exception as e:
            print(f"Error updating balance: {e}")

    @staticmethod
    def update_user(username, updates):
        """Update specific fields for a user."""
        UserModel.ensure_database_exists()
        lines = []
        try:
            with open(UserModel.db_path, "r") as file:
                for line in file:
                    data = line.strip().split(",")
                    if data[5] == username:
                        data = [
                            updates.get("name", data[0]),
                            updates.get("surname", data[1]),
                            updates.get("phone", data[2]),
                            updates.get("id_number", data[3]),
                            updates.get("email", data[4]),
                            data[5],  # Username remains the same
                            data[6],  # Password hash remains the same
                            updates.get("balance", data[7]),
                        ]
                    lines.append(",".join(data))

            with open(UserModel.db_path, "w") as file:
                for line in lines:
                    file.write(line + "\n")
        except Exception as e:
            print(f"Error updating user: {e}")

    @staticmethod
    def get_accounts(username):
        """Fetch all accounts for the user."""
        accounts_file = f"database/{username}_accounts.txt"
        if not os.path.exists(accounts_file):
            return []  # No accounts yet

        accounts = []
        try:
            with open(accounts_file, "r") as file:
                for line in file:
                    try:
                        name, balance = line.strip().split(",")
                        accounts.append({"name": name, "balance": float(balance)})
                    except ValueError:
                        print(f"Skipping malformed line in {accounts_file}: {line}")
        except Exception as e:
            print(f"Error reading accounts file for {username}: {e}")
        return accounts

    @staticmethod
    def add_account(username, account_name, initial_balance):
        """Add a new account for the user."""
        if initial_balance < 0:
            print(f"Cannot add account with negative balance: {initial_balance}")
            return False

        accounts_file = f"database/{username}_accounts.txt"
        existing_accounts = UserModel.get_accounts(username)

        # Check for duplicate account names
        if any(account["name"] == account_name for account in existing_accounts):
            print(f"Account with name '{account_name}' already exists for user '{username}'.")
            return False  # Indicate failure to add account

        try:
            with open(accounts_file, "a") as file:
                file.write(f"{account_name},{initial_balance}\n")
            return True  # Indicate success
        except Exception as e:
            print(f"Error adding account for {username}: {e}")
            return False

    @staticmethod
    def get_total_balance(username):
        """Calculate the total balance across all accounts."""
        accounts = UserModel.get_accounts(username)
        return sum(account["balance"] for account in accounts)

    @staticmethod
    def log_transaction(username, transaction_type, amount, details="", balance_after=None):
        """Log a transaction for the user."""
        transaction_file = f"database/{username}_transactions.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(transaction_file, "a") as file:
                file.write(f"{timestamp},{transaction_type},{amount},{details},{balance_after}\n")
        except Exception as e:
            print(f"Error logging transaction for {username}: {e}")

    @staticmethod
    def get_transaction_history(username):
        """Fetch transaction history for the user."""
        transaction_file = f"database/{username}_transactions.txt"
        if not os.path.exists(transaction_file):
            return []  # No transactions yet

        transactions = []
        try:
            with open(transaction_file, "r") as file:
                for line in file:
                    try:
                        timestamp, transaction_type, amount, details, balance_after = line.strip().split(",", 4)
                        transactions.append({
                            "timestamp": timestamp,
                            "type": transaction_type,
                            "amount": float(amount),
                            "details": details,
                            "balance_after": float(balance_after)
                        })
                    except ValueError:
                        print(f"Skipping malformed transaction line: {line}")
        except Exception as e:
            print(f"Error reading transactions for {username}: {e}")
        return transactions
