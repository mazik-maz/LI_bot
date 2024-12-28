import sqlite3

def add_problem(photo_path, answer):
    """
    Adds a problem to the database.

    :param photo_path: Path to the photo file.
    :param answer: Correct answer for the problem.
    """
    try:
        # Read photo as binary data
        with open(photo_path, 'rb') as file:
            photo_data = file.read()

        # Connect to the database
        conn = sqlite3.connect("bot_database.db")
        cursor = conn.cursor()

        # Insert problem into the database
        cursor.execute("INSERT INTO problems (photo, answer) VALUES (?, ?)", (photo_data, answer))
        conn.commit()
        print("Problem added successfully!")

    except FileNotFoundError:
        print("Error: Photo file not found.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()

if __name__ == "__main__":

    list = [('problems/1.png', "20.4"),
            ('problems/2.png', "18"),
            ('problems/3.png', "29.1"),
            ('problems/4.png', "9.5"),
            ('problems/5.png', "16.1, 8.5"),
            ]

    # Example usage
    print("Add a new problem to the database.")
    for i in range(5):
        photo_path = list[i][0]
        answer = list[i][1]
        add_problem(photo_path, answer)
