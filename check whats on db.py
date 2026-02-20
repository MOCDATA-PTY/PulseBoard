#!/usr/bin/env python
"""
Simple test script to read data from the pulseboard MySQL database.
"""

import mysql.connector

# MySQL credentials
DB_HOST = "167.88.43.168"         # Remote server IP
DB_USER = "pulseboard"
DB_PASS = "PulseB0ard@2026Secure"
DB_NAME = "pulseboard"
DB_PORT = 3306

def main():
    try:
        # Connect to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor(dictionary=True)

        # Example: list first 10 users
        cursor.execute("SELECT * FROM auth_user LIMIT 10;")
        users = cursor.fetchall()
        print("=== Users in auth_user ===")
        for u in users:
            print(f"{u['id']}: {u['username']} ({u['first_name']} {u['last_name']})")

        # Example: list first 10 profiles
        cursor.execute("SELECT * FROM accounts_userprofile LIMIT 10;")
        profiles = cursor.fetchall()
        print("\n=== Profiles in accounts_userprofile ===")
        for p in profiles:
            print(f"{p['id']}: User ID {p['user_id']}, Job Title: {p['job_title']}")

        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")

if __name__ == "__main__":
    main()