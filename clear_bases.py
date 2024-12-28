import sqlite3

# Function to clear the users table
def clear_users():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    print("Users table cleared successfully.")

# Function to clear the problems table
def clear_problems():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problems")
    conn.commit()
    conn.close()
    print("Problems table cleared successfully.")

if __name__ == "__main__":
    print("Select an option:")
    print("1. Clear Users Table")
    print("2. Clear Problems Table")
    choice = input("Enter your choice: ")

    if choice == "1":
        clear_users()
    elif choice == "2":
        clear_problems()
    else:
        print("Invalid choice. Exiting.")
