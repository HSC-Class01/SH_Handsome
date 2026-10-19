[![대시보드 바로가기](https://img.shields.io/badge/🔗-대시보드%20바로가기-2563EB?style=for-the-badge)](https://hsc-class01.github.io/SH_Handsome/)

# 한섬(020000) 재무 분석 대시보드

DART Open API로 한섬과 국내 상장 패션·의류 비교기업(peer firms)의 공시 수치를 수집하고, 연간·반기·분기 실적 및 재무비율을 시각화하는 대시보드입니다.

> **실제 데이터 연결 전:** DART 인증키를 GitHub Actions Secret `DART_API_KEY`로 등록하고 Actions 탭에서 `DART 재무데이터 업데이트`를 실행해야 숫자가 채워집니다. 인증키 없이 임의의 재무 수치를 표시하지 않습니다.

## 빠른 링크

- **[🔗 대시보드 바로가기](https://hsc-class01.github.io/SH_Handsome/)**
- [DART Open API](https://opendart.fss.or.kr/)
- [인증 흐름·API 키·토큰 관리](docs/AUTHENTICATION.md)

## 기능

- DART 연결재무제표(CFS)를 우선 수집하고, 미제공 시 별도재무제표(OFS)를 시도
- 주요 수치: 매출액, 영업이익, 당기순이익, 자산·부채·자본, 유동자산·유동부채, 영업활동현금흐름
- 재무비율: 영업이익률, 순이익률, 부채비율, 유동비율, ROE
- Annual · Half-year · Quarterly 표를 각각 제공
- 매출액/영업이익 추세 그래프, 자산 구조 차트, peer firms 비교 표
- 매월 1일 KST 09:17 자동 갱신 및 Actions 수동 실행
- 원본 공시 계정 행을 `data/hansem_dart_reports.json`에 보관하고, 정규화 데이터는 `data/financials.json`에 저장

## API 키 등록 및 실행

1. [DART Open API](https://opendart.fss.or.kr/)에서 인증키를 발급받습니다.
2. 저장소 **Settings → Secrets and variables → Actions → New repository secret**로 이동합니다.
3. 이름은 `DART_API_KEY`, 값은 발급된 키로 설정합니다.
4. **Actions → DART 재무데이터 업데이트 → Run workflow**로 첫 실행을 합니다.
5. 성공하면 JSON 데이터가 커밋되고 대시보드가 갱신됩니다.

키를 소스 코드, HTML/JavaScript, README, JSON 산출물, ZIP 파일, Issue 또는 로그에 붙여 넣지 마세요.

## GitHub Pages 배포

**Settings → Pages → Build and deployment → Source**에서 **GitHub Actions**를 선택합니다. `main`에 push가 발생하면 Deploy workflow가 실행됩니다.

저장소는 현재 **비공개**입니다. GitHub Free의 비공개 저장소에서는 Pages 배포가 지원되지 않을 수 있습니다. 공개 대시보드가 필요하면 저장소 소유자/조직 정책을 확인한 뒤 공개 전환 또는 Pages를 지원하는 요금제·조직 설정을 선택해야 합니다. 저장소 접근 권한을 임의로 바꾸지는 않았습니다.

### About 섹션 링크

저장소 페이지 오른쪽 **About**의 톱니바퀴에서 **Website**에 다음 주소를 직접 입력하고 저장하세요.

`https://hsc-class01.github.io/SH_Handsome/`

배포 URL이 실제로 공개된 뒤 링크를 활성화하는 것이 좋습니다. 저장소 About 메타데이터를 수정하는 별도 API 작업은 이 연결에서 제공되지 않아 README와 문서에 수동 설정 단계를 남겼습니다.

## 로컬 실행

```bash
python -m pip install -r requirements.txt
# macOS / Linux
export DART_API_KEY="발급받은_키"
python scripts/update_financials.py
# Windows PowerShell:
# $env:DART_API_KEY="발급받은_키"
# python scripts/update_financials.py
```

## 국내 peer firms

| 종목코드 | 기업 | 비교 영역 |
|---:|---|---|
| 093050 | LF | 패션 브랜드·의류 유통 |
| 031430 | 신세계인터내셔날 | 패션 브랜드·수입 브랜드 유통 |
| 383220 | F&F | 패션 브랜드 운영 |
| 111770 | 영원무역 | 아웃도어·의류 제조 및 OEM |
| 105630 | 한세실업 | 글로벌 의류 OEM/ODM |
| 001460 | BYC | 내의·언더웨어 |

비교기업의 브랜드/유통/OEM 비중과 회계상 연결 범위가 서로 다르므로 단순 수익률 순위만으로 판단하지 마세요.

## 지표 기준

금액 단위는 억원입니다. 분기 손익과 현금흐름은 누적 공시액 차이로 산출하며, 분기 말 자산·부채·자본은 해당 보고서 잔액을 씁니다. 영업이익률 = 영업이익/매출액, 순이익률 = 순이익/매출액, 부채비율 = 부채총계/자본총계, 유동비율 = 유동자산/유동부채입니다. 반기·분기 ROE는 연환산 근사치입니다. 누락된 계정은 0이 아니라 `—`로 표시합니다.

이 대시보드는 교육·정보 정리용이며 투자 자문이 아닙니다.
