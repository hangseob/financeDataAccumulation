# mmkt_rate 테이블 스키마 정보

이미지에서 추출한 `mmkt_rate` 테이블의 컬럼 정보 및 추정 타입입니다.

## 테이블 명: `mmkt_rate`

| Column Name | Data Type (추정) | 설명 | 예시 데이터 |
| :--- | :--- | :--- | :--- |
| **TDATE** | `VARCHAR(8)` | 거래 일자 (YYYYMMDD) | '20260123' |
| **CCY** | `VARCHAR(3)` | 통화 코드 1 | 'EUR', 'KRW', 'USD', 'AUD' |
| **CCY2** | `VARCHAR(3)` | 통화 코드 2 | 'EUR', 'KRW', 'USD', 'AUD' |
| **RATETYPE** | `VARCHAR(10)` | 금리 유형 | 'BASE', 'BOND' |
| **CURVE_ID** | `VARCHAR(20)` | 커브 식별자 | 'EURBASE', 'AUDTSY', 'BRLTSY' |
| **RATE_ID** | `VARCHAR(20)` | 금리 식별자 | 'EURBASE', 'AUDTSY3Y', 'AUDTSY15Y' |
| **TENOR_NAME** | `VARCHAR(10)` | 테너(만기) 명칭 | 'N', '3Y', '15V', '2Y' |
| **REL_TENOR_NAME** | `VARCHAR(10)` | 관련 테너 명칭 | 'N' |
| **MID** | `DECIMAL(20, 10)` | 중간값 (Mid Rate) | 0.0215, 0.0425925 |
| **BID** | `DECIMAL(20, 10)` | 매수 호가 (Bid Rate) | 0.0215, 0.042619 |
| **ASK** | `DECIMAL(20, 10)` | 매도 호가 (Ask Rate) | 0.0215, 0.042566 |

---

### SQL Create Table 문 (참고용)

```sql
CREATE TABLE mmkt_rate (
    tdate VARCHAR(8) NOT NULL,
    ccy VARCHAR(3) NOT NULL,
    ccy2 VARCHAR(3),
    ratetype VARCHAR(10),
    curve_id VARCHAR(20),
    rate_id VARCHAR(20),
    tenor_name VARCHAR(10),
    rel_tenor_name VARCHAR(10),
    mid DECIMAL(20, 10),
    bid DECIMAL(20, 10),
    ask DECIMAL(20, 10),
    PRIMARY KEY (tdate, rate_id) -- 데이터 특성에 따라 조정 필요
);
```
