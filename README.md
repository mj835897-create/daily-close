# 국내 주식 대시보드

평일 장 마감 후 GitHub Actions가 시세·PER·PBR·배당수익률을 받아 `docs/data.json`을 갱신하고,
`docs/index.html`이 그 파일을 읽어 보여 줍니다. (GitHub Pages로 공개)

## 설정
1. 이 폴더를 새 public 저장소로 올립니다.
2. `stocks.txt`에서 종목을 수정합니다. (종목코드 6자리 + 이름)
3. Settings → Pages → Branch: `main`, Folder: `/docs` → Save
4. Actions 탭 → `update-data` → Run workflow (처음 한 번 수동 실행)
5. `https://<아이디>.github.io/<저장소>/` 로 접속

시세는 야후 파이낸스 기준이며 지연될 수 있고, 투자 판단의 근거로 쓰지 마세요.
API 키나 비밀값은 사용하지 않으니 저장소를 public으로 올려도 됩니다.
