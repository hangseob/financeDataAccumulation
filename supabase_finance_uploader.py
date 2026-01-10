"""
FinanceDataReader로 수집한 금융 데이터를 Supabase에 저장하는 모듈
"""
import FinanceDataReader as fdr
from supabase import create_client, Client
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
import time

# Supabase 접속 정보
SUPABASE_URL = "https://jvyqmtklymxndtapkqez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eXFtdGtseW14bmR0YXBrcWV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjgwMTgzNzEsImV4cCI6MjA4MzU5NDM3MX0.VLr8RtCuOwegJ14odarY2cStVQw9V85vjeE1LZOHZyo"

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class FinanceDataUploader:
    """금융 데이터를 Supabase에 업로드하는 클래스"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    def upload_stock_data(self, 
                         symbol: str, 
                         start_date: str, 
                         end_date: Optional[str] = None,
                         table_name: str = 'stock_prices',
                         batch_size: int = 1000) -> Dict:
        """
        주식 데이터를 Supabase에 업로드
        
        Args:
            symbol: 종목 코드 (예: '005930', 'AAPL')
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD), None이면 오늘까지
            table_name: Supabase 테이블 이름
            batch_size: 배치 크기
            
        Returns:
            업로드 결과 딕셔너리
        """
        print(f"\n{'='*80}")
        print(f"종목 {symbol} 데이터 수집 시작...")
        print(f"기간: {start_date} ~ {end_date or '현재'}")
        print(f"{'='*80}")
        
        try:
            # 데이터 수집
            df = fdr.DataReader(symbol, start_date, end_date)
            
            if df.empty:
                return {
                    'success': False,
                    'symbol': symbol,
                    'error': '데이터가 비어있습니다.'
                }
            
            print(f"✓ 데이터 수집 완료: {len(df)}개 레코드")
            
            # 데이터 변환
            records = self._prepare_stock_records(df, symbol)
            
            # 배치 업로드
            total_uploaded = 0
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                try:
                    # upsert를 사용하여 중복 데이터 자동 처리
                    response = self.supabase.table(table_name).upsert(
                        batch,
                        on_conflict='symbol,date'
                    ).execute()
                    
                    total_uploaded += len(batch)
                    print(f"  업로드 진행: {total_uploaded}/{len(records)} ({total_uploaded/len(records)*100:.1f}%)")
                    time.sleep(0.1)  # API 제한 방지
                    
                except Exception as e:
                    print(f"  ⚠ 배치 업로드 오류: {e}")
                    continue
            
            print(f"✓ 업로드 완료: {total_uploaded}개 레코드")
            
            return {
                'success': True,
                'symbol': symbol,
                'records_collected': len(df),
                'records_uploaded': total_uploaded,
                'start_date': str(df.index[0]),
                'end_date': str(df.index[-1])
            }
            
        except Exception as e:
            print(f"✗ 오류 발생: {e}")
            return {
                'success': False,
                'symbol': symbol,
                'error': str(e)
            }
    
    def _prepare_stock_records(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """DataFrame을 Supabase 레코드 형식으로 변환"""
        records = []
        for date, row in df.iterrows():
            record = {
                'symbol': symbol,
                'date': date.strftime('%Y-%m-%d'),
                'open': float(row.get('Open', 0)) if pd.notna(row.get('Open')) else None,
                'high': float(row.get('High', 0)) if pd.notna(row.get('High')) else None,
                'low': float(row.get('Low', 0)) if pd.notna(row.get('Low')) else None,
                'close': float(row.get('Close', 0)) if pd.notna(row.get('Close')) else None,
                'volume': int(row.get('Volume', 0)) if pd.notna(row.get('Volume')) else None,
                'change': float(row.get('Change', 0)) if pd.notna(row.get('Change')) else None,
                'created_at': datetime.now().isoformat()
            }
            records.append(record)
        return records
    
    def upload_multiple_stocks(self, 
                              symbols: List[str], 
                              start_date: str,
                              end_date: Optional[str] = None,
                              table_name: str = 'stock_prices') -> List[Dict]:
        """
        여러 종목의 데이터를 한번에 업로드
        
        Args:
            symbols: 종목 코드 리스트
            start_date: 시작 날짜
            end_date: 종료 날짜
            table_name: Supabase 테이블 이름
            
        Returns:
            각 종목별 업로드 결과 리스트
        """
        results = []
        total = len(symbols)
        
        print(f"\n{'='*80}")
        print(f"총 {total}개 종목 업로드 시작")
        print(f"{'='*80}")
        
        for idx, symbol in enumerate(symbols, 1):
            print(f"\n[{idx}/{total}] {symbol} 처리중...")
            result = self.upload_stock_data(symbol, start_date, end_date, table_name)
            results.append(result)
            time.sleep(0.5)  # API 제한 방지
        
        # 결과 요약
        success_count = sum(1 for r in results if r['success'])
        print(f"\n{'='*80}")
        print(f"업로드 완료: {success_count}/{total} 성공")
        print(f"{'='*80}")
        
        return results
    
    def upload_index_data(self,
                         index_code: str,
                         start_date: str,
                         end_date: Optional[str] = None,
                         table_name: str = 'index_prices') -> Dict:
        """지수 데이터를 Supabase에 업로드"""
        return self.upload_stock_data(index_code, start_date, end_date, table_name)
    
    def upload_exchange_rate(self,
                           currency_pair: str,
                           start_date: str,
                           end_date: Optional[str] = None,
                           table_name: str = 'exchange_rates') -> Dict:
        """환율 데이터를 Supabase에 업로드"""
        return self.upload_stock_data(currency_pair, start_date, end_date, table_name)
    
    def upload_crypto_data(self,
                          crypto_pair: str,
                          start_date: str,
                          end_date: Optional[str] = None,
                          table_name: str = 'crypto_prices') -> Dict:
        """암호화폐 데이터를 Supabase에 업로드"""
        return self.upload_stock_data(crypto_pair, start_date, end_date, table_name)
    
    def get_stock_list(self, market: str = 'KRX') -> pd.DataFrame:
        """종목 리스트를 조회"""
        return fdr.StockListing(market)
    
    def upload_stock_list(self,
                         market: str = 'KRX',
                         table_name: str = 'stock_list') -> Dict:
        """
        종목 리스트를 Supabase에 업로드
        
        Args:
            market: 시장 코드 ('KRX', 'KOSPI', 'KOSDAQ', 'NASDAQ', 'NYSE' 등)
            table_name: Supabase 테이블 이름
            
        Returns:
            업로드 결과
        """
        print(f"\n{'='*80}")
        print(f"{market} 종목 리스트 업로드 시작...")
        print(f"{'='*80}")
        
        try:
            # 종목 리스트 조회
            df = fdr.StockListing(market)
            print(f"✓ 종목 리스트 조회 완료: {len(df)}개 종목")
            
            # 데이터 변환
            records = []
            for _, row in df.iterrows():
                record = {
                    'code': str(row.get('Code', '')),
                    'name': str(row.get('Name', '')),
                    'market': str(row.get('Market', market)),
                    'close': float(row.get('Close', 0)) if pd.notna(row.get('Close')) else None,
                    'volume': int(row.get('Volume', 0)) if pd.notna(row.get('Volume')) else None,
                    'market_cap': float(row.get('Marcap', 0)) if pd.notna(row.get('Marcap')) else None,
                    'updated_at': datetime.now().isoformat()
                }
                records.append(record)
            
            # 업로드
            response = self.supabase.table(table_name).upsert(
                records,
                on_conflict='code'
            ).execute()
            
            print(f"✓ 업로드 완료: {len(records)}개 종목")
            
            return {
                'success': True,
                'market': market,
                'total_stocks': len(records)
            }
            
        except Exception as e:
            print(f"✗ 오류 발생: {e}")
            return {
                'success': False,
                'market': market,
                'error': str(e)
            }


def main():
    """메인 실행 함수"""
    uploader = FinanceDataUploader(supabase)
    
    print("\n" + "="*80)
    print("FinanceDataReader → Supabase 데이터 업로더")
    print("="*80)
    
    # 예시 1: 한국 주식 데이터 업로드
    print("\n[예시 1] 삼성전자, SK하이닉스, NAVER 최근 1년 데이터 업로드")
    korean_stocks = ['005930', '000660', '035420']
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    results = uploader.upload_multiple_stocks(
        symbols=korean_stocks,
        start_date=start_date,
        table_name='stock_prices'
    )
    
    # 예시 2: 지수 데이터 업로드
    print("\n[예시 2] KOSPI 지수 최근 1년 데이터 업로드")
    uploader.upload_index_data(
        index_code='KS11',
        start_date=start_date,
        table_name='index_prices'
    )
    
    # 예시 3: 환율 데이터 업로드
    print("\n[예시 3] USD/KRW 환율 최근 1년 데이터 업로드")
    uploader.upload_exchange_rate(
        currency_pair='USD/KRW',
        start_date=start_date,
        table_name='exchange_rates'
    )
    
    # 예시 4: 종목 리스트 업로드
    print("\n[예시 4] KRX 전체 종목 리스트 업로드")
    uploader.upload_stock_list(
        market='KRX',
        table_name='stock_list'
    )
    
    print("\n" + "="*80)
    print("모든 작업 완료!")
    print("="*80)


if __name__ == "__main__":
    main()
