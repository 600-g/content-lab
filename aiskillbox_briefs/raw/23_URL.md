# HyperFrames × Claude 가이드

- URL: https://resonant-frog-df5.notion.site/HyperFrames-Claude-3503a1a3234380b685bddfa2931f3665
- source_type: notion
- length: 1627 chars
- scraped_at: 2026-05-27 01:04:10
- elapsed: 5s
- ok: True
- error: 

---

▎ 웹사이트 URL 하나면 AI가 광고 영상까지 뚝딱 만들어줌

🤔 이게 뭔데?

HTML → MP4 변환 프레임워크. Claude한테 웹사이트 주소 던지면 디자인 분석부터 영상 완성까지 자동으로 다 해줌.

🎯 만들 수 있는 것들

종류 | 길이 | 포맷 |
|---|---|---|
인스타 릴스 / 스토리 | 10~15초 | 1080 × 1920 세로 |
틱톡 광고 | 10~15초 | 1080 × 1920 세로 |
제품 소개 영상 | 30~60초 | 1920 × 1080 가로 |
브랜드 광고 | 15~30초 | 원하는 포맷 |

🤖 쓰는 법 (이게 전부)

Claude에게 해당 깃헙 링크(하단에 있습니다.)를 주며, 적용하게 셋팅해달라고 한다.

아래 내용으로 진행

Claude Code 에서 이렇게만 치면 됨:

/website-to-hyperframes https://원하는사이트.com 15초짜리 인스타 광고 만들어줘

Claude가 프리뷰 URL 주면 브라우저에서 열면 됨:

⛑️ 제가 쓴 프롬프트
/hyperframes 사용해서 영산 만들어줘.
제품 : claudeasy
설명 : 클로드가 어려운 분들이 요즘 유행하는 것들을 사용하고, 개발을 몰라도 알아서 척척 자동화 혹은 개발을 만들어주는 웹앱.
핵심 기능 : 200개 넘는 하네스 임베드, 추가로 없는 하네스는 알아서 만들어줌. 내가 대답할 필요 없이 오케스트레이션이 알아서 대답해줌. 나는 개발요청만 하면됨. 깃헙 트렌드를 실시간으로 볼 수 있고, 내 프로젝트에 어떻게 적용하면 좋을지 바로 인사이트 줌.
타겟 : 비전공자 / 클로드가 어려운 초보.
길이 : 15초.
프로젝트 path: ~~~

📥 MP4로 저장

Claude 가 만들어준 웹페이지에서 Export → 다운받기 누르시면 됩니다.

🔗 링크

🎵Suno AI로 배경음악 만들기

▎ 가사도 장르도 텍스트로 입력하면 AI가 노래로 만들어줌. 무료로 하루 5곡까지 가능.

사이트: https://suno.com

만드는 법

사이트 접속 후 로그인
구글 계정으로 바로 가입 가능

Create 버튼 클릭

Custom Mode 켜기
Custom Mode를 켜야 장르, 분위기를 세밀하게 설정할 수 있음

항목 입력

Lyrics → 가사 입력 (또는 Instrumental 체크하면 가사 없는 순수 음악)

Style of Music → 원하는 분위기 입력

예시: cinematic, ambient, minimal, emotional

예시: upbeat, electronic, korean pop

Title → 곡 제목

Create 클릭 → 2곡 생성됨
마음에 드는 걸 고르면 됨

영상에 쓸 배경음악 만들 때 추천 프롬프트

cinematic ambient, minimal piano, no vocals, soft, premium feel, 30 seconds

upbeat electronic, corporate, motivational, no lyrics, clean

💎 저는 suno 를 사용해서 유투브에 Playlist 를 만들고 있습니다! 관심 있으신 분들이 있다면, 해당 노래 만드는 파이프라인 개발 방법도 영상으로 올릴게요!
(파이프라인 노래 참고 영상 : http://youtube.com/watch?v=OSe17yfmUNo&t=753s)
