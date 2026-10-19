# 인증·요청 흐름

## 구성 요소와 요청 순서
1. GitHub Actions의 `schedule`(매월 1일 00:17 UTC = 한국 시간 09:17) 또는 `workflow_dispatch`로 수집을 시작합니다.
2. `DART_API_KEY` Secret이 Python collector의 환경 변수로만 전달됩니다.
3. collector는 `/api/corpCode.xml`로 종목코드-기업고유번호를 확인하고, `/api/fnlttSinglAcntAll.json`을 기간별 요청합니다.
4. 연결재무제표(CFS)를 먼저 사용하고 데이터가 없으면 별도재무제표(OFS)를 요청합니다. 손익/현금흐름 누적값으로부터 분기값을 산출하고 비율을 계산합니다.
5. `data/financials.json`과 한섬 원자료 아카이브 `data/hansem_dart_reports.json`을 커밋합니다.
6. `GITHUB_TOKEN`으로 변경 사항을 저장하고, push가 GitHub Pages 배포 workflow를 실행합니다. 브라우저는 공개 JSON만 읽으며 DART 키에 접근하지 않습니다.

## Credentials and tokens
- **DART_API_KEY**: DART에서 발급. 저장소 Settings → Secrets and variables → Actions에서 이름을 `DART_API_KEY`로 만들어 저장합니다. 소스 코드, HTML/JavaScript, JSON 산출물, README, ZIP에 넣지 않습니다.
- **GITHUB_TOKEN**: GitHub Actions가 실행별로 제공하는 단기 토큰입니다. 데이터 workflow는 `contents: write`만 요청합니다. 개인용 PAT를 만들거나 프로젝트에 저장할 필요가 없습니다.
- **Pages 토큰 권한**: 배포 workflow는 `contents: read`, `pages: write`, `id-token: write`를 설정합니다.
- 이 채팅의 GitHub 연결 인증정보는 프로젝트 런타임으로 전달되지 않으며 workflow에서 재사용되지 않습니다.

## 오류 및 보안
API 키가 없거나 인증/호출 제한 오류가 발생하면 collector를 실패 처리하고 변경 사항을 커밋하지 않습니다. 로그에는 API 요청 URL 또는 키를 출력하지 않도록 합니다. 공개 Pages를 사용하는 경우 데이터 파일은 모두 공개될 수 있으므로 민감정보를 넣지 마세요.

## 공식 문서
- DART Open API: https://opendart.fss.or.kr/
- [기업고유번호 API](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019018)
- [단일회사 전체 재무제표](https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020)
- [GitHub Actions GITHUB_TOKEN](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
