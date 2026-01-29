### prompt candidates

* 화면에 차트를 띄울때 Plotly library 를 쓰는 것과 streamlit library를 쓰는게 혼재되어 있어서 문제가 되는거 아닐까?
만일 그렇다면 가급적 plotly 로만 구현해줘. 
기존 파일을 수정하지 말고 새로운 파일로 만들어줘

* 날짜 슬라이더를 조작했을때 화면 스크롤이 최 상단으로 움직이는 이슈를 해결하기 위해 어떤 조치들을 취했는지 설명해줘. 그리고 너는 왜 문제가 없다고 판단하는지도 알려줘

* 동기화 이슈들이 계속 발생하는데, streamlit이 애초에 이렇게 동기화가 깨지기 취약한 녀석인건가 아님 다른 이슈가 있는 건가?


---

# 버그 리스트
1. 날짜 슬라이더 변경시 화면 스크롤 최상단으로 이동
2. start date 입력값 변경시 1.번 문제 반복되는 것
3. 날짜 슬라이더 클릭시 새로 입력된 start date 무시하고 최초 start date 적용되는 것
4. 슬라이더 날짜 클릭시 2번에 1번꼴로 클릭된 위치가 아닌 이전 위치로 가는 문제
5. curve_id 변경하고 슬라이더 건드리면 chart에 예전 curve_id curve 가 그려지는 에러가 생겼네.
6. curve_id 변경하고 슬라이더 건드리면 두번에 한번 꼴로 chart에 예전 curve_id curve 가 그려지는 에러가 생겼네.

앞으론 테스트 할때 memo.md 에 있는 버그 리스트를 전부 테스트해줘

# 빈 프로젝트로 새로 시작하기 위한 프롬프트
이제 oracle db mmkt_rate에서 data를 가져와서 금리커브를 그릴건데. 
## INPUT:
*curve_name (혹은 curve_id) 을 인풋으로 받고 (예: KRWQ3L) 근데 입력창에 KRW 를 입력하면 풀다운 메뉴로 선택가능한 녀석이 뜨도록
*data range lable 아래 start date, end date 입력하도록 
*YYYYMMDD 형식으로 받거나 달력 클릭해서 달력에서 선택.

위 설정을 마치고 data_load 버튼을 누르면 
기간내의 curve_id , mid 값을 가져와서 cache로 가지고 있음.

## OUTPUT:
커브를 그려주는데 
*X축에  tenor_name_to_year_fraction 스케일로 나타내는데 명칭은 tenor_name 사용
*Y 축에는 MID 값을 나타내고
y축 최소, 최대값:  curve_name (curve_id?) 에 0.5% 버퍼를 둠
커브 아래에 y축과 동일한 길이인 date slider 가 있어서 일단은 end date 위치에 위치시키고 슬라이더 위에 날짜를 표시함
*수기로 슬라이더 이동시키면 해당 날짜의 커브가 chart에 표시되도록 한다

