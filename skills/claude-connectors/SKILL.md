---
name: claude-connectors
description: 클로드 AI의 **공식 커넥터 및 MCP**를 활용하여 Notion, Slack, Canva 등 9,000개 이상의 앱과 연동하는 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude"]
sources:
  - https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149
---

# 클로드 연동 16가지

💡 클로드 AI의 **공식 커넥터 및 MCP**를 활용하여 Notion, Slack, Canva 등 9,000개 이상의 앱과 연동하는 스킬입니다.

## 이게 뭔가요?

클로드(Claude) AI는 다양한 외부 서비스와 연동할 수 있는 커넥터 및 MCP(My Custom Persona) 기능을 제공합니다. 이를 통해 사용자는 Notion, Slack, Canva, Gmail, Google Drive 등 자주 사용하는 앱을 클로드 내에서 직접 조작하고 자동화할 수 있습니다. 특히, Zapier MCP를 활용하면 9,000개 이상의 앱과 연동하여 복잡한 워크플로우를 구축할 수 있습니다. 모든 커넥터 및 MCP 기능은 클로드 유료 플랜(Pro $20/월 이상)에서 사용 가능합니다.


## 따라하기

### ✅ 바로 가능 (공식 커넥터 / 전용 MCP)

#### 1. 힉스필드 → 초 고퀄 AI 영상 연동 제작
1.  **준비물:** Higgsfield 계정(무료 크레딧), Claude PRO 모델 이상 추천
2.  **설정:** Claude 설정(Settings) → 커넥터(Connectors) → '커스텀 커넥터 추가(Add custom connector)'
3.  **입력:** 이름 `Higgsfield`, 서버 URL `https://mcp.higgsfield.ai`
4.  **연결:** Higgsfield 계정 로그인/인증, 필요 시 '항상 허용(Always Allow)'
5.  **예시 명령:** "Higgsfield로 '밤거리를 걷는 네온 고양이' 5초짜리 4K 영상 만들어줘"
6.  **한계:** 최대 4K·15초, 생성 시 크레딧 소모. 무료 소진 후 유료 플랜 필요.

#### 8. 노션 → 문서 자동 작성
1.  **준비물:** 유료 Claude 플랜 + Notion 계정
2.  **설정:** Claude 설정 → 커넥터 → '찾아보기(Browse connectors)'에서 Notion 선택 → 연결(Connect)
3.  **인증:** Notion 워크스페이스 선택 및 인증
4.  **활성화:** (데스크톱 앱) 채팅창 '+'에서 Notion 토글 ON
5.  **예시 명령:** "회의록 페이지 새로 만들고 오늘 액션 아이템 정리해서 넣어줘"
6.  **한계:** 읽기·검색·생성·업데이트 가능, 삭제는 불가. 처음엔 특정 페이지/DB로 범위 좁혀 연결 권장.

#### 11. 슬랙 → 팀 메시지 자동화
1.  **준비물:** 유료 Claude 플랜 + Slack 계정
2.  **설정:** Claude 설정 → 커넥터 → '찾아보기'에서 Slack 선택 → 연결(Connect)
3.  **인증:** Slack 워크스페이스 선택 후 허용(Allow)
4.  **활성화:** 채팅창 '+'에서 Slack 토글 ON
5.  **예시 명령:** "#마케팅 채널 이번 주 중요한 논의 요약하고 결정사항 정리해서 올려줘"
6.  **한계:** 읽기·검색·게시·답글 지원. 본인 권한 범위 채널만. 각 작업은 사용자 승인 필요.

#### 12. 캔바 → 디자인 자동 생성
1.  **준비물:** 유료 Claude 플랜 + Canva 계정
2.  **설정:** Claude 설정 → 커넥터 → '찾아보기'에서 Canva 검색 → '+'(연결) 클릭
3.  **인증:** Canva 인증 화면에서 허용(Allow)
4.  **권한 설정:** 'search designs', 'generate designs with AI' 등 개별 설정 → 채팅창 '+'에서 Canva 토글 ON
5.  **예시 명령:** "이 카피로 인스타용 카드뉴스 디자인 초안 만들고 PNG로 내보내줘"
6.  **한계:** 검색·생성·내보내기 지원(인라인 미리보기). AI 생성 등 일부 기능은 권한 개별 승인 필요.

#### 16. 재피어 → 9,000개 앱 연결
1.  **준비물:** Zapier 계정(무료 포함), Claude 유료 플랜
2.  **설정:** `mcp.zapier.com` → "+ New MCP Server" → Claude 선택, 서버 이름 입력, "Create MCP Server"
3.  **도구 추가:** "Configure" 탭 → "+ Add tool" → 앱 검색, 액션 선택, 계정 인증 → Save
4.  **연결:** "Connect" 탭의 서버 URL 복사 → Claude 설정에서 새 커넥터로 추가
5.  **예시 명령:** "내 Zapier에 연결된 앱들로 지금 뭘 할 수 있는지 알려줘"
6.  **한계:** 서버 URL=비밀번호(유출 주의), 호출마다 task 2개 소모, 추가한 액션만 사용 가능.

### 🟡 공식 커넥터지만 "읽기+생성"까지만 (수정·정리는 Zapier 보완)

#### 2. Gmail → 메일 읽기·초안 작성
1.  **준비물:** 유료 Claude 플랜 + Google 계정
2.  **설정:** Claude 설정 → 커넥터 → '찾아보기'에서 Gmail 선택 → 연결(Connect)
3.  **인증:** Google 로그인 후 권한 허용
4.  **활성화:** 채팅창 '+'에서 Gmail 토글 ON
5.  **예시 명령:** "지난주 거래처 메일 찾아 요약하고 회신 초안 작성해줘"
6.  **한계:** 읽기 + 초안 생성만. 발송·삭제·이동·라벨분류 불가. 수정 작업은 Zapier MCP 필요.

#### 5. 구글 드라이브 → 파일 검색·읽기·저장
1.  **준비물:** Google 계정(무료 Claude 포함 가능)
2.  **설정:** Claude 설정 → 커넥터 → '찾아보기'에서 Google Drive 선택 → 연결(Connect)
3.  **인증:** Google 로그인 후 권한 허용
4.  **활성화:** 채팅창 '+'에서 Google Drive 토글 ON
5.  **예시 명령:** "내 드라이브에서 '6월 보고서' 찾아 핵심 내용 정리해줘"
6.  **한계:** 검색·읽기·업로드·폴더생성만(텍스트만 추출). 이동·이름변경·삭제 불가. 정리는 Zapier 필요.

#### 9. 구글 캘린더 → 일정 확인·생성
1.  **준비물:** 유료 Claude 플랜 + Google 계정
2.  **설정:** Claude 설정 → 커넥터 → '찾아보기'에서 Google Calendar 선택 → 연결(Connect)
3.  **인증:** Google 로그인 후 권한 허용
4.  **활성화:** 채팅창 '+'에서 Google Calendar 토글 ON
5.  **예시 명령:** "다음 주 빈 시간 찾아 화요일 오후에 1시간 회의 잡아줘"
6.  **한계:** 확인 + 새 일정 생성만 안정적. 기존 일정 수정·삭제는 Zapier 권장.

### 🟡 Zapier/봇토큰 설정하면 가능

#### 10. 구글 시트 → 숫자 자동 집계 (16번 먼저 필요)
1.  **준비물:** 16번 Zapier MCP 완료 + Google 계정
2.  **설정:** Zapier MCP 서버 "Configure" 탭 → "+ Add tool" → "Google Sheets" 검색
3.  **액션 선택:** "Create Spreadsheet Row"(여러 행은 "Create Multiple Spreadsheet Rows") 선택, Google 계정 인증 → 대상 시트/워크시트 지정 후 Save (읽기 필요 시 "Lookup Spreadsheet Row"도 추가)
4.  **예시 명령:** "오늘 리드 3명을 'Leads' 시트에 이름·이메일·날짜로 한 줄씩 추가해줘"
5.  **한계:** 추가 행은 헤더 바로 아래 삽입, 헤더(컬럼) 미리 정의돼 있어야 매핑 가능.

#### 13. 유튜브 → 채널 자동 관리 (16번 먼저 필요)
1.  **준비물:** 16번 Zapier MCP 완료 + YouTube 채널 + (업로드 시) 채널 전화번호 인증 설정
2.  **설정:** "Configure" 탭 → "+ Add tool" → "YouTube" 검색
3.  **액션 선택:** 용도별 액션(Find Video, Upload Video, Update Video Thumbnail, Get Report) 선택, YouTube 계정 인증 후 Save
4.  **예시 명령:** "내 채널 최근 30일 조회수 리포트 가져오고, 새 영상 'AI 카드뉴스 만들기' 업로드해줘"
5.  **한계:** 업로드·썸네일은 전화번호 인증 필요. 비공개 분석은 본인 소유 채널만.

#### 15. 줌 → 회의록 자동 정리 (16번 먼저 필요)
1.  **준비물:** 16번 Zapier MCP 완료 + Zoom 계정 + (녹화·전사는) Zoom 유료(Pro 이상, 자동 전사 트리거는 Business 이상)
2.  **설정:** "Configure" 탭 → "+ Add tool" → "Zoom" 검색
3.  **액션 선택:** 용도별 액션(Create Meeting, Find Recording and Download, Get Meeting Summary) 선택, Zoom 계정 OAuth 인증 후 Save
4.  **예시 명령:** "내일 3시 '주간 회의' 만들고, 지난 회의 클라우드 녹화 전사본 가져와 요약해줘"
5.  **한계:** 클라우드 녹화·전사는 Zoom 유료 필수. 본인이 호스트인 미팅만.

#### 4. 텔레그램 → 나만의 비서
1.  **준비물:** Telegram 계정 + BotFather 봇 토큰 + MCP/Zapier 설정
2.  **봇 생성:** Telegram @BotFather → /newbot → 봇 이름·사용자명 입력, 발급된 HTTP API 토큰 복사
3.  **연동:** 토큰을 텔레그램 MCP 서버 설정 또는 Zapier Telegram 연동에 입력 → Claude 연결
4.  **예시 명령:** "내 텔레그램 봇으로 '오늘 카드뉴스 업로드 완료' 메시지 보내줘"
5.  **한계:** 봇과 먼저 대화를 시작한 사용자/봇이 속한 그룹에만 전송 가능. 토큰 유출 시 봇 탈취.

#### 14. 디스코드 → 커뮤니티 봇
1.  **준비물:** Discord 계정 + 관리 권한 서버 + Developer Portal 봇 토큰
2.  **봇 생성:** Discord Developer Portal → New Application → Bot 탭 → Token 발급·복사
3.  **서버 추가:** Installation 탭 → Guild Install → Scopes에 `bot` 추가, 권한 지정 → Install Link로 봇을 내 서버에 추가
4.  **연동:** 토큰을 MCP/Zapier Discord 연동에 입력
5.  **예시 명령:** "디스코드 #공지 채널에 '신규 카드뉴스 발행됨' 올려줘"
6.  **한계:** 초대된 서버·권한 채널만. 토큰 유출 시 재발급. 일부 동작은 Privileged Intents 필요.

### 🟠 제약 있음 (조건부·개발 필요)

#### 3. 인스타그램 → 계정 분석 (조회만)
1.  **준비물:** Facebook 페이지에 연결된 인스타 비즈니스/크리에이터 계정 + Windsor.ai 계정
2.  **설정:** `onboard.windsor.ai` → 데이터 소스 "Instagram Insights" 선택 → Facebook 인증, 인스타 프로필 선택
3.  **연동:** Claude에서 Windsor.ai 커넥터(MCP) 연결 → 권한 "항상 허용"
4.  **예시 명령:** "최근 14일간 공유율이 가장 높았던 릴스 알려줘"
5.  **한계:** 읽기 전용(분석)만. 게시·수정·댓글·DM 불가. 개인 계정 불가. Windsor.ai는 외부 유료 서비스.

#### 6. 카카오톡 → 나에게 알림 (메모 API)
1.  **준비물:** 카카오 계정 + Kakao Developers 앱 + REST API 키 + 카카오 로그인 OAuth(talk_message 동의)
2.  **설정:** `developers.kakao.com` → 내 애플리케이션 → 애플리케이션 추가 → [요약 정보]에서 앱 키 확인, [카카오 로그인] 활성화 및 Redirect URI 등록, [동의항목]에서 "카카오톡 메시지 전송(talk_message)" 설정
3.  **연동:** OAuth로 access token 발급 → `POST https://kapi.kakao.com/v2/api/talk/memo/default/send` 호출
4.  **예시 명령:** "오늘 할 일 요약본을 내 카카오톡으로 보내줘" (자동화는 Make의 Kakao 모듈로)
5.  **한계:** 나에게 보내기(메모)만 가능. 친구/타인 전송은 별도 심사·승인 필요. 공식 커넥터 없음.

#### 7. 네이버 → 일정·메일 (직접 개발 필요)
1.  **준비물:** 네이버 계정 + Naver Developers 앱 + Client ID/Secret + 네이버 로그인 access token
2.  **설정:** `developers.naver.com` → Application → 애플리케이션 등록 → 사용 API "네이버 로그인" 선택, 서비스 URL·Callback URL 등록
3.  **연동:** 발급된 Client ID/Secret 확인, OAuth로 token 발급 후 캘린더 API 직접 호출 / 메일은 IMAP·SMTP 사용
4.  **예시 명령:** "다음 주 회의를 네이버 캘린더에 추가해줘" (직접 만든 연동 스크립트/MCP 필요)
5.  **한계:** 원클릭 커넥터·공식 통합 없음. 개발자가 OAuth·API 직접 구현. 메일은 REST API 없어 IMAP/SMTP만. 비개발자는 구글 캘린더 권장.

## 출처

[클로드를 비서처럼 쓰는 16가지](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149)

## 출처

- [https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149)
