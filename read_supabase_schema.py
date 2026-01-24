"""
Supabase 전체 스키마 목록 및 테이블 정보를 하드코딩 없이 탐색하는 스크립트
"""
import sys
import io
import requests

# Windows 환경에서 한글 출력을 위한 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase 연결 정보
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

def explore_supabase():
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    print("=" * 80)
    print("[Supabase 정밀 탐색 시스템 - 스키마 및 테이블 분석]")
    print("=" * 80)
    print(f"연결 URL: {SUPABASE_URL}\n")

    # 1. 전체 스키마 정보 수집 시도
    # PostgREST는 기본적으로 여러 스키마를 노출하도록 설정될 수 있습니다.
    # 우선 API 루트에서 어떤 스키마들이 언급되는지 확인합니다.
    try:
        print("🔍 스키마 목록 분석 중...")
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
        if response.status_code != 200:
            print(f"❌ 접속 실패: {response.status_code}")
            return

        spec = response.json()
        
        # OpenAPI 스펙 내의 basePath나 다른 메타데이터를 통해 스키마 추정
        # 실제 Supabase UI에서 보이는 스키마 리스트를 가져오기 위해 
        # PostgREST의 'Accept-Profile' 기능을 활용한 탐색이 가능하지만, 
        # 여기서는 우선 발견된 정보들을 출력합니다.
        
        # PostgREST에서 기본적으로 제공하는 스키마들 (탐색 시도 대상)
        common_schemas = ['public', 'financial_data', 'storage', 'auth', 'extensions']
        found_schemas = []

        for schema in common_schemas:
            # 각 스키마별로 OpenAPI 스펙이 존재하는지 확인
            schema_headers = headers.copy()
            schema_headers["Accept-Profile"] = schema
            try:
                res = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=schema_headers, timeout=3)
                if res.status_code == 200:
                    found_schemas.append(schema)
            except:
                continue

        print(f"✅ 총 {len(found_schemas)}개의 활성 스키마가 발견되었습니다.")
        print("-" * 40)
        for i, schema in enumerate(found_schemas, 1):
            print(f"  {i}. {schema}")
        print("-" * 40 + "\n")

        # 2. 각 스키마별 테이블 상세 정보 출력
        for schema in found_schemas:
            print(f"📂 [스키마: {schema}] 내의 테이블 목록")
            
            schema_headers = headers.copy()
            schema_headers["Accept-Profile"] = schema
            res = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=schema_headers)
            
            if res.status_code == 200:
                schema_spec = res.json()
                definitions = schema_spec.get('definitions', {})
                
                if not definitions:
                    print("   (이 스키마에는 노출된 테이블이 없습니다.)")
                else:
                    print(f"   {'테이블 이름':<25} | {'컬럼 수':<10}")
                    print(f"   {'-' * 40}")
                    for name, details in sorted(definitions.items()):
                        col_count = len(details.get('properties', {}))
                        print(f"   {name:<25} | {col_count:<10}")
            else:
                print(f"   ⚠️ 스키마 정보를 읽을 수 없습니다. (HTTP {res.status_code})")
            print()

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    explore_supabase()
