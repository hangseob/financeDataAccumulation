"""
삼성전자 주가 조회 스크립트

Supabase에서 삼성전자 최근 한 달 데이터를 조회합니다.
"""
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd

# Supabase 접속 정보
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_samsung_recent_month():
    """삼성전자 최근 한 달 데이터 조회"""
    print("\n" + "="*80)
    print("삼성전자(005930) 최근 한 달 주가")
    print("="*80)
    
    # 한 달 전 날짜 계산
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        # Supabase에서 조회
        result = supabase.table('stock_prices') \
            .select('date, close, open, high, low, volume, change') \
            .eq('symbol', '005930') \
            .gte('date', one_month_ago) \
            .order('date', desc=True) \
            .execute()
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(result.data)
        
        if df.empty:
            print("⚠ 데이터가 없습니다. 테이블에 데이터를 먼저 업로드하세요.")
            return None
        
        # 날짜 형식 변환
        df['date'] = pd.to_datetime(df['date'])
        
        # 변화율을 퍼센트로 변환
        df['change_pct'] = (df['change'] * 100).round(2)
        
        # 한글 컬럼명 추가
        df_display = df.copy()
        df_display.columns = ['날짜', '종가', '시가', '고가', '저가', '거래량', '변화율', '등락률(%)']
        
        print(f"\n조회 기간: {one_month_ago} ~ {datetime.now().strftime('%Y-%m-%d')}")
        print(f"총 거래일: {len(df)}일\n")
        
        # 상위 10개만 출력
        print("최근 10거래일:")
        print(df_display.head(10).to_string(index=False))
        
        # 통계 정보
        print("\n" + "="*80)
        print("통계 정보")
        print("="*80)
        print(f"평균 종가: {df['close'].mean():,.0f}원")
        print(f"최고가: {df['high'].max():,.0f}원 ({df[df['high'] == df['high'].max()]['date'].iloc[0].strftime('%Y-%m-%d')})")
        print(f"최저가: {df['low'].min():,.0f}원 ({df[df['low'] == df['low'].min()]['date'].iloc[0].strftime('%Y-%m-%d')})")
        print(f"평균 거래량: {df['volume'].mean():,.0f}주")
        
        # 기간 수익률
        first_close = df.iloc[-1]['close']
        last_close = df.iloc[0]['close']
        period_return = ((last_close - first_close) / first_close * 100)
        print(f"기간 수익률: {period_return:+.2f}%")
        
        return df
        
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return None


def get_samsung_recent_n_days(days: int = 20):
    """삼성전자 최근 N일 데이터 조회"""
    print("\n" + "="*80)
    print(f"삼성전자(005930) 최근 {days}거래일 주가")
    print("="*80)
    
    try:
        # 최근 N일 조회 (LIMIT 사용)
        result = supabase.table('stock_prices') \
            .select('*') \
            .eq('symbol', '005930') \
            .order('date', desc=True) \
            .limit(days) \
            .execute()
        
        df = pd.DataFrame(result.data)
        
        if df.empty:
            print("⚠ 데이터가 없습니다.")
            return None
        
        df['date'] = pd.to_datetime(df['date'])
        df['change_pct'] = (df['change'] * 100).round(2)
        
        # 전일 대비 변동
        df_sorted = df.sort_values('date')
        df_sorted['prev_close'] = df_sorted['close'].shift(1)
        df_sorted['day_change'] = df_sorted['close'] - df_sorted['prev_close']
        
        # 다시 역순 정렬
        df_sorted = df_sorted.sort_values('date', ascending=False)
        
        print(f"\n총 {len(df)}거래일\n")
        
        # 출력
        display_df = df_sorted[['date', 'close', 'open', 'high', 'low', 'volume', 'change_pct', 'day_change']].copy()
        display_df.columns = ['날짜', '종가', '시가', '고가', '저가', '거래량', '등락률(%)', '전일대비']
        
        print(display_df.to_string(index=False))
        
        return df_sorted
        
    except Exception as e:
        print(f"✗ 오류 발생: {e}")
        return None


def get_samsung_summary():
    """삼성전자 최근 한 달 요약 통계"""
    print("\n" + "="*80)
    print("삼성전자(005930) 최근 한 달 요약")
    print("="*80)
    
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        result = supabase.table('stock_prices') \
            .select('*') \
            .eq('symbol', '005930') \
            .gte('date', one_month_ago) \
            .order('date') \
            .execute()
        
        df = pd.DataFrame(result.data)
        
        if df.empty:
            print("⚠ 데이터가 없습니다.")
            return
        
        df['date'] = pd.to_datetime(df['date'])
        
        # 요약 정보
        print(f"\n📊 기본 정보")
        print(f"   종목명: 삼성전자")
        print(f"   종목코드: 005930")
        print(f"   조회기간: {df['date'].min().strftime('%Y-%m-%d')} ~ {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"   거래일수: {len(df)}일")
        
        print(f"\n💰 가격 정보")
        print(f"   현재가: {df.iloc[-1]['close']:,.0f}원")
        print(f"   평균가: {df['close'].mean():,.0f}원")
        print(f"   최고가: {df['high'].max():,.0f}원")
        print(f"   최저가: {df['low'].min():,.0f}원")
        print(f"   가격 범위: {(df['high'].max() - df['low'].min()):,.0f}원")
        
        print(f"\n📈 수익률")
        first_close = df.iloc[0]['close']
        last_close = df.iloc[-1]['close']
        period_return = ((last_close - first_close) / first_close * 100)
        print(f"   기간 수익률: {period_return:+.2f}%")
        print(f"   최고 일간 등락률: {(df['change'].max() * 100):+.2f}%")
        print(f"   최저 일간 등락률: {(df['change'].min() * 100):+.2f}%")
        
        print(f"\n📊 거래량")
        print(f"   평균 거래량: {df['volume'].mean():,.0f}주")
        print(f"   최대 거래량: {df['volume'].max():,.0f}주")
        print(f"   최소 거래량: {df['volume'].min():,.0f}주")
        
    except Exception as e:
        print(f"✗ 오류 발생: {e}")


def save_to_excel(df: pd.DataFrame, filename: str = '삼성전자_주가.xlsx'):
    """데이터를 엑셀 파일로 저장"""
    try:
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"\n✓ 엑셀 파일 저장 완료: {filename}")
    except ImportError:
        print("\n⚠ openpyxl이 설치되지 않았습니다.")
        print("설치: pip install openpyxl")
        # CSV로 대신 저장
        csv_filename = filename.replace('.xlsx', '.csv')
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        print(f"✓ CSV 파일 저장 완료: {csv_filename}")
    except Exception as e:
        print(f"✗ 저장 오류: {e}")


def main():
    """메인 함수"""
    print("\n" + "="*80)
    print("삼성전자 주가 조회 도구")
    print("="*80)
    
    print("\n옵션을 선택하세요:")
    print("  1. 최근 한 달 데이터")
    print("  2. 최근 20거래일 데이터")
    print("  3. 최근 한 달 요약 통계")
    print("  4. 전체 실행 (1+2+3)")
    
    try:
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == '1':
            df = get_samsung_recent_month()
            if df is not None and input("\n엑셀로 저장하시겠습니까? (y/n): ").lower() == 'y':
                save_to_excel(df)
                
        elif choice == '2':
            df = get_samsung_recent_n_days(20)
            if df is not None and input("\n엑셀로 저장하시겠습니까? (y/n): ").lower() == 'y':
                save_to_excel(df)
                
        elif choice == '3':
            get_samsung_summary()
            
        elif choice == '4':
            df = get_samsung_recent_month()
            get_samsung_recent_n_days(20)
            get_samsung_summary()
            
        else:
            print("잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n\n작업이 취소되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {e}")


if __name__ == "__main__":
    main()
