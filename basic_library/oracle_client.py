import oracledb
import os
import sys

class OracleClient:
    """
    오라클 클라우드 DB와 통신하기 위한 기본 클라이언트 클래스입니다.
    C:\\oracle\\Wallet 경로의 지갑 정보를 사용하여 접속합니다.
    """
    
    def __init__(self, user="ADMIN", password="1stOracleDB.pw", dsn="s9lbmrnw3zct3j80_high"):
        self.wallet_path = r'C:\oracle\Wallet'
        self.wallet_password = '0458seob.wallet'
        self.config = {
            "user": user,
            "password": password,
            "dsn": dsn
        }
        self.connection = None

    def connect(self):
        """DB에 접속합니다."""
        if not os.path.exists(self.wallet_path):
            raise FileNotFoundError(f"❌ Wallet path not found: {self.wallet_path}")
        
        try:
            self.connection = oracledb.connect(
                user=self.config["user"],
                password=self.config["password"],
                dsn=self.config["dsn"],
                config_dir=self.wallet_path,
                wallet_location=self.wallet_path,
                wallet_password=self.wallet_password
            )
            print(f"[SUCCESS] Connected to Oracle DB ({self.config['dsn']})")
            return self.connection
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            raise

    def close(self):
        """접속을 종료합니다."""
        if self.connection:
            self.connection.close()
            print("[INFO] Connection closed.")

    def execute_query(self, sql, params=None):
        """단일 SQL 쿼리를 실행합니다. (INSERT, UPDATE, DELETE 등)"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params or [])
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            print(f"[ERROR] Query execution failed: {e}")
            raise
        finally:
            cursor.close()

    def fetch_all(self, sql, params=None):
        """SELECT 쿼리를 실행하고 모든 결과를 반환합니다."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, params or [])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"[ERROR] Fetch failed: {e}")
            raise
        finally:
            cursor.close()

    def execute_many(self, sql, data_list):
        """대량의 데이터를 삽입(Bulk Insert)할 때 사용합니다."""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            cursor.executemany(sql, data_list)
            self.connection.commit()
            return cursor.rowcount
        except Exception as e:
            self.connection.rollback()
            print(f"[ERROR] Execute many failed: {e}")
            raise
        finally:
            cursor.close()

# 간단한 사용 예시
if __name__ == "__main__":
    # 터미널 출력 인코딩 설정
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    client = OracleClient()
    try:
        client.connect()
        # 간단한 조회 테스트
        result = client.fetch_all("SELECT USER FROM DUAL")
        print(f"Current User: {result}")
    finally:
        client.close()
