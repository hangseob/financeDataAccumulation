import oracledb
import sys

# Oracle Cloud DB 접속 정보 (ADMIN 계정으로 접속하여 유저 생성)
config = {
    "user": "ADMIN",
    "password": "1stOracleDB.pw",
    "dsn": "s9lbmrnw3zct3j80_high",
    "wallet_path": r'C:\oracle\Wallet',
    "wallet_password": '0458seob.wallet'
}

new_user = "SPT"
new_password = "0458seob.S*T"

def create_spt_user():
    conn = None
    try:
        print(f"Connecting to Oracle Cloud DB as {config['user']}...")
        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
            config_dir=config["wallet_path"],
            wallet_location=config["wallet_path"],
            wallet_password=config["wallet_password"]
        )
        cursor = conn.cursor()
        print("✅ Connected as ADMIN!")

        # 1. 유저 존재 여부 확인 및 삭제 (선택 사항이나 깔끔한 시작을 위해)
        print(f"Checking if user {new_user} already exists...")
        cursor.execute(f"SELECT COUNT(*) FROM all_users WHERE username = '{new_user}'")
        if cursor.fetchone()[0] > 0:
            print(f"   - User {new_user} exists. Dropping it first...")
            cursor.execute(f"DROP USER {new_user} CASCADE")
            print(f"   - User {new_user} dropped.")

        # 2. 유저 생성 (비밀번호: 0458seob.S*T)
        print(f"Creating user {new_user}...")
        # 비밀번호에 특수문자가 포함될 수 있으므로 따옴표 처리 확인
        cursor.execute(f"CREATE USER {new_user} IDENTIFIED BY \"{new_password}\"")
        print(f"   - User {new_user} created successfully.")

        # 3. 권한 부여
        print("Granting permissions...")
        cursor.execute(f"GRANT CONNECT, RESOURCE TO {new_user}")
        cursor.execute(f"ALTER USER {new_user} QUOTA UNLIMITED ON DATA")
        # 추가적인 개발 편의를 위한 권한
        cursor.execute(f"GRANT CREATE VIEW, CREATE SYNONYM TO {new_user}")
        print("   - Basic permissions granted.")

        conn.commit()
        print(f"\n✅ All tasks completed! User '{new_user}' is ready to use.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
    create_spt_user()
