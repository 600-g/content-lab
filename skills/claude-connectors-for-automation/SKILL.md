---
name: claude-connectors-for-automation
description: Claude에 **16가지 AI 도구**를 연결하여 **업무 자동화**를 강화하는 스킬입니다.
origin: content-lab
grade: A
difficulty: 중급
category: 자동화
ai_tools: ["Claude"]
sources:
  - https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149
---

# 클로드에 16가지 AI 도구 연결하기

💡 Claude에 **16가지 AI 도구**를 연결하여 **업무 자동화**를 강화하는 스킬입니다.

## 이게 뭔가요?

Claude의 공식 커넥터 기능과 Zapier 연동을 활용하여 다양한 외부 AI 도구 및 서비스와 Claude를 연결하는 방법을 다룹니다. 이를 통해 단순한 텍스트 생성을 넘어, 영상 제작, 문서 자동화, 디자인 생성, 커뮤니티 관리 등 다채로운 업무를 Claude를 통해 수행할 수 있습니다.

주요 연결 도구로는 **Higgsfield (영상 제작)**, **Notion (문서 자동화)**, **Slack (팀 메시지)**, **Canva (디자인)**, **Zapier (9,000개 앱 연결)** 등이 있으며, 이 외에도 Gmail, Google Drive, Google Calendar 등 Google Workspace 연동 기능도 제공합니다. 일부 기능은 Claude 유료 플랜(Pro $20/월 이상)이 필요하며, 특히 Zapier 연동(MCP)은 다른 커넥터들의 고급 기능을 활성화하는 데 핵심적인 역할을 합니다.

💰 유료 필요: Claude Pro 이상 (일부 기능)
✅ 무료 대안: Gemini, ChatGPT 등 다른 AI 도구 활용 (기능 제한적)

## 따라하기

**1. 힉스필드 (Higgsfield) → 초 고퀄 AI 영상 연동 제작**
1.  **준비물**: Higgsfield 계정 (무료 크레딧 제공), Claude PRO 모델 이상 추천.
2.  **설정**: Claude 웹/데스크톱/모바일 → 설정(Settings) → 커넥터(Connectors) → "커스텀 커넥터 추가(Add custom connector)".
3.  **이름**: Higgsfield
4.  **서버 URL**: `https://mcp.higgsfield.ai`
5.  **연결**: Higgsfield 계정 로그인/인증.
6.  **권한**: 필요 시 "항상 허용(Always Allow)" 설정.
7.  **예시 명령**: "Higgsfield로 '밤거리를 걷는 네온 고양이' 5초짜리 4K 영상 만들어줘"
8.  **한계**: 최대 4K·15초, 생성 시 크레딧 소모 (무료 소진 후 유료 플랜 필요).

**8. 노션 (Notion) → 문서 자동 작성**
1.  **준비물**: 유료 Claude 플랜 + Notion 계정.
2.  **설정**: Claude 웹 → 설정 → 커넥터. (데스크톱: Customize → Connectors).
3.  **찾기**: "찾아보기(Browse connectors)"에서 Notion 선택 → 연결(Connect).
4.  **인증**: Notion 인증 페이지에서 워크스페이스 선택 → 계속(Continue).
5.  **(데스크톱)** 앱 재시작 후 채팅창 "+"에서 Notion 토글 ON.
6.  **예시 명령**: "회의록 페이지 새로 만들고 오늘 액션 아이템 정리해서 넣어줘"
7.  **한계**: 읽기·검색·생성·업데이트 가능, 삭제는 차단. 처음엔 특정 페이지/DB로 범위 좁혀 연결 권장.

**11. 슬랙 (Slack) → 팀 메시지 자동화**
1.  **준비물**: 유료 Claude 플랜 + Slack 워크스페이스 계정 (조직은 관리자 권한 필요).
2.  **설정**: Claude 웹 → 설정 → 커넥터.
3.  **찾기**: "찾아보기"에서 Slack 선택 → 연결(Connect).
4.  **인증**: Slack 인증 화면에서 워크스페이스 선택 후 허용(Allow).
5.  채팅창 "+"에서 Slack 토글 ON.
6.  **예시 명령**: "#마케팅 채널 이번 주 중요한 논의 요약하고 결정사항 정리해서 올려줘"
7.  **한계**: 읽기·검색·게시·답글 지원, 본인 권한 범위 채널만. 각 작업은 사용자 승인 필요.

**12. 캔바 (Canva) → 디자인 자동 생성**
1.  **준비물**: 유료 Claude 플랜(Pro $20/월~) + Canva 계정.
2.  **설정**: Claude 웹 → 설정 → 커넥터.
3.  **찾기**: "찾아보기"에서 Canva 검색 → 카드의 "+"(연결) 클릭.
4.  **인증**: Canva 인증 화면에서 허용(Allow).
5.  **권한 설정**: "구성(Configure)"에서 'search designs', 'generate designs with AI' 등 권한 개별 설정 → 채팅창 "+"에서 Canva 토글 ON.
6.  **예시 명령**: "이 카피로 인스타용 카드뉴스 디자인 초안 만들고 PNG로 내보내줘"
7.  **한계**: 검색·생성·내보내기 지원 (인라인 미리보기). AI 생성 등 일부 기능은 권한 개별 승인 필요.

**16. 재피어 (Zapier) → 9,000개 앱 연결 (만능 다리)**
1.  **준비물**: Zapier 계정 (무료 포함, 호출 1회당 task 2개 차감) + MCP 추가 가능한 유료 Claude 플랜.
2.  **MCP 서버 생성**: `mcp.zapier.com` → "+ New MCP Server" → Claude 선택 → 서버 이름 입력 → "Create MCP Server".
3.  **도구 추가**: "Configure" 탭 → "+ Add tool" → 앱 검색 → 액션 선택 (또는 "Add all tools") → 계정 인증 → Save.
4.  **Claude 연결**: "Connect" 탭의 서버 URL 복사 → Claude 설정에서 새 커넥터로 추가.
5.  **예시 명령**: "내 Zapier에 연결된 앱들로 지금 뭘 할 수 있는지 알려줘"
6.  **한계**: 서버 URL=비밀번호 (유출 주의), 호출마다 task 2개 소모, 추가한 액션만 사용 가능.

**2. Gmail → 메일 읽기·초안 작성**
1.  **준비물**: 유료 Claude 플랜 + Google 계정.
2.  **설정**: Claude 웹 → 설정 → 커넥터.
3.  **찾기**: "찾아보기"에서 Gmail 선택 → 연결(Connect).
4.  **인증**: Google 로그인 창에서 계정 선택 후 권한 허용.
5.  채팅창 "+"에서 Gmail 토글 ON.
6.  **예시 명령**: "지난주 거래처 메일 찾아 요약하고 회신 초안 작성해줘"
7.  **한계**: 읽기 + 초안 생성만. 발송·삭제·이동·라벨분류 불가 (수정 작업은 Zapier MCP 필요).

**5. 구글 드라이브 (Google Drive) → 파일 검색·읽기·저장**
1.  **준비물**: Google 계정 (무료 Claude 포함 가능).
2.  **설정**: Claude 웹 → 설정 → 커넥터.
3.  **찾기**: "찾아보기"에서 Google Drive 선택 → 연결(Connect).
4.  **인증**: Google 로그인 후 권한 허용.
5.  채팅창 "+"에서 Google Drive 토글 ON.
6.  **예시 명령**: "내 드라이브에서 '6월 보고서' 찾아 핵심 내용 정리해줘"
7.  **한계**: 검색·읽기·업로드·폴더생성만 (텍스트만 추출). 이동·이름변경·삭제 불가 (정리는 Zapier 필요).

**9. 구글 캘린더 (Google Calendar) → 일정 확인·생성**
1.  **준비물**: 유료 Claude 플랜 + Google 계정.
2.  **설정**: Claude 웹 → 설정 → 커넥터.
3.  **찾기**: "찾아보기"에서 Google Calendar 선택 → 연결(Connect).
4.  **인증**: Google 로그인 후 권한 허용.
5.  채팅창 "+"에서 Google Calendar 토글 ON.
6.  **예시 명령**: "다음 주 빈 시간 찾아 화요일 오후에 1시간 회의 잡아줘"
7.  **한계**: 확인 + 새 일정 생성만 안정적. 기존 일정 수정·삭제는 Zapier 권장.

**10. 구글 시트 (Google Sheets) → 숫자 자동 집계 (16번 먼저 필요)**
1.  **준비물**: 16번 Zapier MCP 완료 + Google 계정.
2.  **설정**: Zapier MCP 서버 "Configure" 탭 → "+ Add tool" → "Google Sheets" 검색.
3.  **액션 선택**: "Create Spreadsheet Row" (여러 행: "Create Multiple Spreadsheet Rows"). (읽기 필요 시 "Lookup Spreadsheet Row"도 추가).
4.  **인증**: Google 계정 인증 → 대상 시트/워크시트 지정 후 Save.
5.  **예시 명령**: "오늘 리드 3명을 'Leads' 시트에 이름·이메일·날짜로 한 줄씩 추가해줘"
6.  **한계**: 추가 행은 헤더 바로 아래 삽입, 헤더(컬럼) 미리 정의돼 있어야 매핑 가능.

**13. 유튜브 (YouTube) → 채널 자동 관리 (16번 먼저 필요)**
1.  **준비물**: 16번 Zapier MCP 완료 + YouTube(Google) 채널 + (업로드 시) 채널 전화번호 인증 설정.
2.  **설정**: "Configure" 탭 → "+ Add tool" → "YouTube" 검색.
3.  **액션 선택**: "Find Video", "Upload Video", "Update Video Thumbnail", "Get Report" 등.
4.  **인증**: YouTube 계정 인증 후 Save.
5.  **예시 명령**: "내 채널 최근 30일 조회수 리포트 가져오고, 새 영상 'AI 카드뉴스 만들기' 업로드해줘"
6.  **한계**: 업로드·썸네일은 전화번호 인증 필요. 비공개 분석은 본인 소유 채널만 ("Get Report").

**15. 줌 (Zoom) → 회의록 자동 정리 (16번 먼저 필요)**
1.  **준비물**: 16번 Zapier MCP 완료 + Zoom 계정 + (녹화·전사는) Zoom 유료 (Pro 이상, 자동 전사 트리거는 Business 이상).
2.  **설정**: "Configure" 탭 → "+ Add tool" → "Zoom" 검색.
3.  **액션 선택**: "Create Meeting", "Find Recording and Download", "Get Meeting Summary" 등.
4.  **인증**: Zoom 계정 OAuth 인증 후 Save.
5.  **예시 명령**: "내일 3시 '주간 회의' 만들고, 지난 회의 클라우드 녹화 전사본 가져와 요약해줘"
6.  **한계**: 클라우드 녹화·전사는 Zoom 유료 필수 (무료는 로컬녹화라 불가). 본인이 호스트인 미팅만.

**4. 텔레그램 (Telegram) → 나만의 비서**
1.  **준비물**: Telegram 계정 + BotFather 봇 토큰 + MCP/Zapier 설정.
2.  **봇 생성**: Telegram @BotFather → /newbot → 봇 이름/사용자명 입력 → 발급된 HTTP API 토큰 복사.
3.  **연동**: 토큰을 텔레그램 MCP 서버 설정 또는 Zapier Telegram 연동에 입력 → Claude 연결.
4.  **예시 명령**: "내 텔레그램 봇으로 '오늘 카드뉴스 업로드 완료' 메시지 보내줘"
5.  **한계**: 봇과 먼저 대화를 시작한 사용자/봇이 속한 그룹에만 전송 가능. 토큰 유출 시 봇 탈취.

**14. 디스코드 (Discord) → 커뮤니티 봇**
1.  **준비물**: Discord 계정 + 관리 권한 서버 + Developer Portal 봇 토큰.
2.  **봇 생성**: Discord Developer Portal → New Application → 이름 입력 → Create → Bot 탭 → Reset Token으로 봇 토큰 발급/복사.
3.  **봇 초대**: Installation 탭 → Guild Install → Scopes에 'bot' 추가 + 권한 지정 → 생성된 Install Link로 봇 초대.
4.  **연동**: 토큰을 MCP/Zapier Discord 연동에 입력.
5.  **예시 명령**: "디스코드 #공지 채널에 '신규 카드뉴스 발행됨' 올려줘"
6.  **한계**: 초대된 서버·권한 채널만. 토큰 유출 시 재발급. 일부 동작은 Privileged Intents 필요.

**3. 인스타그램 (Instagram) → 계정 분석 (조회만)**
1.  **준비물**: Facebook 페이지에 연결된 인스타 비즈니스/크리에이터 계정 + Windsor.ai 계정.
2.  **설정**: onboard.windsor.ai 로그인 → 데이터 소스에서 "Instagram Insights" 선택.
3.  **인증**: Facebook 인증 → 연결할 인스타 프로필 선택.
4.  **Claude 연결**: Claude에서 Windsor.ai 커넥터(MCP) 연결 → 권한 "항상 허용".
5.  **예시 명령**: "최근 14일간 공유율이 가장 높았던 릴스 알려줘"
6.  **한계**: 읽기 전용 (게시·수정·댓글·DM 불가). 개인 계정 불가. Windsor.ai는 외부 유료 서비스.

**6. 카카오톡 → 나에게 알림 (메모 API)**
1.  **준비물**: 카카오 계정 + Kakao Developers 앱 + REST API 키 + 카카오 로그인 OAuth (talk_message 동의).
2.  **설정**: developers.kakao.com → 내 애플리케이션 → 애플리케이션 추가 → [요약 정보]에서 앱 키 확인. [카카오 로그인] 활성화 + Redirect URI 등록. [동의항목]에서 "카카오톡 메시지 전송(talk_message)" 설정.
3.  **호출**: OAuth로 access token 발급 → `POST https://kapi.kakao.com/v2/api/talk/memo/default/send` 호출.
4.  **예시 명령**: "오늘 할 일 요약을 내 카카오톡으로 보내줘" (자동화는 Make의 Kakao 모듈).
5.  **한계**: 나에게 보내기 (메모)만 가능. 친구/타인 전송은 별도 심사/승인 필요. 공식 커넥터 없음.

**7. 네이버 → 일정·메일 (직접 개발 필요)**
1.  **준비물**: 네이버 계정 + Naver Developers 앱 + Client ID/Secret + 네이버 로그인 access token.
2.  **설정**: developers.naver.com → Application → 애플리케이션 등록 → 사용 API에서 "네이버 로그인" 선택. 서비스 URL/Callback URL 등록.
3.  **발급**: Client ID/Secret 확인. OAuth로 token 발급 후 캘린더 API 직접 호출 / 메일은 IMAP·SMTP.
4.  **예시 명령**: "다음 주 회의를 네이버 캘린더에 추가해줘" (직접 만든 연동 스크립트/MCP 필요).
5.  **한계**: 원클릭 커넥터·공식 통합 없음 (개발자 필요). 메일은 REST API 없어 IMAP/SMTP만.

## 활용 예시

1.  **콘텐츠 제작 자동화**: **Higgsfield** 커넥터를 사용하여 "'AI 활용법' 주제로 30초짜리 홍보 영상 만들어줘"와 같이 요청하면, Claude가 영상을 생성해주는 시나리오.
2.  **업무 보고 자동화**: **Notion** 커넥터와 **Slack** 커넥터를 함께 사용하여, "주간 회의록을 Notion에 저장하고 주요 결정사항을 Slack #general 채널에 공유해줘"와 같은 명령으로 업무 효율 증대.
3.  **데이터 관리**: **Google Sheets** 커넥터와 **Zapier**를 연동하여, "오늘 접수된 신규 고객 5명의 정보를 '고객 리드' 시트에 자동으로 추가해줘"와 같이 데이터베이스 관리를 간소화.

## 💡 아이디어

-   **개인 맞춤형 뉴스레터 생성**: 사용자가 관심 있는 키워드를 입력하면, **Gmail** 또는 **RSS 피드** (Zapier 연동)를 통해 관련 기사를 수집하고 Claude가 요약하여 **Telegram** 또는 **Email**로 보내주는 시스템 구축.
-   **AI 기반 영상 콘텐츠 제작 파이프라인**: **Higgsfield**로 영상을 생성하고, **YouTube** 커넥터를 통해 직접 업로드하며, **Canva**로 썸네일을 제작하는 일련의 과정을 Claude에게 맡기는 워크플로우 설계.

## 주의사항

-   **Zapier MCP 서버 URL은 비밀번호처럼 다뤄야 하며, 유출에 주의해야 합니다.**
-   **대부분의 강력한 기능은 Claude 유료 플랜 (Pro $20/월 이상)을 요구합니다.**
-   **10, 13, 15번 기능(Google Sheets, YouTube, Zoom)은 16번 Zapier MCP를 먼저 설정해야 작동합니다.**
-   **일부 서비스(예: Instagram Insights)는 외부 유료 서비스를 연동해야 하거나, 특정 계정 유형(비즈니스/크리에이터)만 지원합니다.**
-   **카카오톡 메시지 전송은 공식 커넥터가 없으며, 일반 사용자는 개인 메모 기능 외에 타인에게 메시지를 보내는 것이 사실상 불가능합니다.**

## 출처

[클로드를 비서처럼 쓰는 16가지](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149)

## 출처

- [https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149](https://yongk.notion.site/16-37f47642a71380a48581d7fff9063e2d?pvs=149)
