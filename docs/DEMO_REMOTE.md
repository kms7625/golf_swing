# 발표 시연 — Mac에서 실행, 학교 PC에서 주소로 접속

이 Mac이 분석 서버·웹을 모두 띄우고, ngrok이 인터넷 주소(https) 하나를 만든다.
학교 PC는 브라우저로 그 주소만 열면 된다(설치 없음).

## Mac에서 (터미널 3개)
```bash
# 1) 분석 서버
cd ~/PycharmProjects/golf_swing/server && ../.venv/bin/uvicorn main:app --port 8010

# 2) 웹 (분석 요청을 /api 로 보내도록 빌드 → vite가 8010으로 넘김)
cd ~/PycharmProjects/golf_swing/web && VITE_API_BASE=/api npm run build && npx vite preview --port 4173

# 3) 외부 주소 + 잠자기 방지
caffeinate -dis ngrok http 4173
```
3번 화면의 `Forwarding https://….ngrok-free.app` 주소를 학교 PC에서 연다.

## 학교 PC에서
- 주소 열기 → ngrok 안내 화면이 나오면 **Visit Site** 한 번 클릭
- https 주소라서 실시간 캠(카메라 권한)도 동작

## 체크리스트
- Mac 전원 연결, 뚜껑 열어 두기(`caffeinate`가 잠자기 방지)
- 학교 네트워크가 ngrok을 막으면 → Mac을 휴대폰 핫스팟에 연결해 다시 시도
- 그래도 안 되면 → 학교 PC 대신 Mac 화면을 직접 연결, 또는 '샘플 데이터 보기'·슬라이드 캡처로 대체
- 주소는 ngrok을 다시 켤 때마다 바뀔 수 있음 → 발표 직전에 켜고 주소 확인
- 시연이 끝나면 ngrok 창에서 Ctrl+C (주소를 아는 누구나 접속 가능하므로)

## 평소 개발
변경 없음: `npm run dev`(5173) + 서버 8010 그대로. `/api` 중계는 `vite preview`에서만 쓴다.
