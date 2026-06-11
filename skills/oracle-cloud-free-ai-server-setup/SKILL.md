---
name: oracle-cloud-free-ai-server-setup
description: 이 스킬은 **Oracle Cloud Infrastructure**의 **Always Free** 티어를 활용하여 **24시간 구동되는 AI 서버 환경**을 구축하는 방법을 다룹니다. 복잡한 **네트워크 설정**과 **SSH 접속** 과정이 핵심입니다.
origin: content-lab
grade: S
difficulty: 고급
category: 개발
ai_tools: ["도구무관"]
sources:
  - https://oracleserverbyaduai.netlify.app/?fbclid=PAVERFWASJXnBleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeBx0OBKXkHoiVSotXm3MbmCk1vgJinL9v1XftySx8dZwgGK4w0vCcT150CWg_aem_k9xiu7z2YBb6S9KSm9VQLg
---

# 오라클 클라우드 무료 AI 서버 구축하기

💡 이 스킬은 **Oracle Cloud Infrastructure**의 **Always Free** 티어를 활용하여 **24시간 구동되는 AI 서버 환경**을 구축하는 방법을 다룹니다. 복잡한 **네트워크 설정**과 **SSH 접속** 과정이 핵심입니다.

## 이게 뭔가요?
헤르메스 같은 AI 에이전트, 텔레그램 봇, n8n, Claude Code 서버… 진짜 쓸모있게 굴리려면 **24시간 켜진 서버**가 필요해요. 맥북 꺼두면 다 멈추니까요.

근데 유료 VPS는 월 몇 만 원씩 나가잖아요. 그래서 **오라클 클라우드 Always Free**로 해결합니다. 스펙도 진짜 좋아요(4 OCPU / 24GB RAM!). 단, **이 세팅에 처음 도전하는 분들이 거의 똑같이 막히는 포인트가 7개** 있어요. 이 가이드엔 그 함정들을 다 정리해뒀어요. 미리 알고 가시면 같은 데서 안 막힙니다.

**✅ 무료 대안:** 오라클 클라우드 Always Free
**💰 유료 필요:** (해당 없음)

## 따라하기

### 1. 오라클 클라우드 계정 준비 및 리전 설정

1. 오라클 Cloud Free Tier 가입 페이지에 들어가서 가입하면 Home Region을 골라요. 한국 기준:
    * South Korea North: Chuncheon
    * South Korea Central: Seoul

⚠️ 가입 단계에서 서울이 안 보일 수 있어요. 그때 당황하지 말고 **일단 춘천으로 가입** → 나중에 서울 구독으로 옮기면 돼요.

Free Tier 그대로면 서울 구독·A1 배정이 제한적일 수 있어요. 그래서:
```
Free Tier 가입 → Pay As You Go로 업그레이드
→ 서울 리전 Subscribe → Always Free 한도 안에서 서버 생성
```

⚠️ **Pay As You Go 전환** = 유료 리소스 생성이 가능한 계정. **무료 한도 밖 리소스를 만들면 진짜 과금돼요.** 9번 비용 체크리스트 꼭 확인!

1. **Region Management**
    → South Korea Central (Seoul)
    → Subscribe

**⚠️ 주의:** 구독했다고 자동으로 서울로 바뀌는 게 아니에요. **화면 오른쪽 위 리전 드롭다운에서 직접 Seoul로 변경**해야 합니다.

### 2. VM 인스턴스 생성 (Compute)

1. **Instances** 페이지로 이동합니다. (검색창에 `Create VM`을 검색하면 안 나옴)
   정확한 경로: `Compute → Instances → Create instance`
   검색할 땐 `Create VM` 말고 **Instances**로 하세요. 👉 Compute Instances 페이지 바로가기

2. **Instance 설정:**
    * Name: `hermes-server`
    * Region: `South Korea Central, Seoul`
    * Image: `Canonical Ubuntu 22.04`
    * Shape: `Ampere → VM.Standard.A1.Flex` (OCPU: 4 / Memory: 24GB)
    * Primary network: `Select existing virtual cloud network`
    * VCN: `hermes-vcn`
    * Subnet: `public-subnet`
    * Public IPv4: `ON`
    * IPv6: `OFF` (경고 떠도 무시 OK)

3. **Boot Volume 설정:**
    * `Specify a custom boot volume size and performance setting`
    * Boot Volume Size: `200GB`
    * Volume Performance: `10 VPU`
    * In-transit encryption: `ON`
    * Customer-managed key: `OFF`

⚠️ **Attach block volume 누르지 마세요.** 추가 볼륨 만드는 거 아니고, Boot Volume 하나를 200GB로 키우는 거예요.

4. **SSH Key 생성 및 다운로드:**
    * `Generate a key pair for me → Save private key`
    * 다운로드 예: `ssh-key-2026-05-28.key`
    * ⚠️ **Private key는 절대 공유 X.**

5. **서버 접속 확인:**
    * 서버 상태가 `Running`이 되면 Details에서 Public IPv4 확인.

### 3. 네트워크 구성 (VCN, Subnet, Gateway, Route Rule)

**⚠️ 초보자가 가장 많이 막히는 부분이에요. VM 스펙보다 네트워크가 어려워요. VCN → Subnet → Internet Gateway → Route Rule → Public IPv4, 이 5개가 다 맞아야 SSH가 돼요.**

1. **VCN 생성:**
    * `Networking → Virtual Cloud Networks → Create VCN`
    * VCN Name: `hermes-vcn`
    * Compartment: `(root)`
    * IPv4 CIDR: `10.0.0.0/16`
    * DNS hostnames: `ON`
    * DNS label: `hermesvcn`
    * IPv6는 사용 안 함.

2. **Subnet 생성:**
    * `hermes-vcn → Subnets → Create Subnet`
    * Name: `public-subnet`
    * Subnet Type: `Regional`
    * IPv4 CIDR: `10.0.1.0/24`
    * Route Table: `Default Route Table for hermes-vcn`
    * Subnet Access ⭐: **Public Subnet**
    * DNS Label: `public`
    * DHCP Options: `Default`
    * Security List: `Default`

3. **Internet Gateway 생성:**
    * `hermes-vcn → Gateways → Internet Gateways → Create Internet Gateway`
    * Name: `hermes-igw`
    * Compartment: `(root)`
    * Enabled: `ON`
    * ⚠️ **Advanced options 건드리지 마세요.**

4. **Route Rule 추가:**
    * `hermes-vcn → Routing → Route Tables`
    * `Default Route Table` 선택 → `Add Route Rules`
    * Target Type: `Internet Gateway`
    * Destination Type: `CIDR Block`
    * Destination CIDR Block: `0.0.0.0/0`
    * Target Internet Gateway: `hermes-igw`

### 4. SSH 접속

**OS별 접속 명령어:**

**Linux/macOS:**
```
chmod 600 ~/Downloads/ssh-key-2026-05-28.key
ssh -i ~/Downloads/ssh-key-2026-05-28.key ubuntu@YOUR_PUBLIC_IP
```

**Windows (PowerShell):**
```
$keyPath = "$HOME	extbackslash Downloads	extbackslash ssh-key-2026-05-28.key"
icacls $keyPath /inheritance:r
icacls $keyPath /grant:r "$($env:USERNAME):(R)"
ssh -i $HOME	extbackslash Downloads	extbackslash ssh-key-2026-05-28.key ubuntu@YOUR_PUBLIC_IP
```

* **주의:** `YOUR_PUBLIC_IP`는 실제 IP 숫자로 대체하고, `@` 뒤 공백 제거. 홈 경로는 `$HOME` 또는 `C:\[사용자명]` 사용.

**접속 후 확인:**
```
whoami # → ubuntu
df -h # 디스크 확인
free -h # 메모리 확인
exit # 서버에서 나가기
```

## 활용 예시

* **24시간 AI 에이전트 구동:** 헤르메스 같은 AI 에이전트를 24시간 구동하여 지속적인 데이터 처리나 봇 운영에 활용할 수 있습니다.
* **개인 개발 서버:** 웹 애플리케이션이나 테스트 환경을 구축하여 외부 인터넷에 노출시키고 테스트할 수 있습니다.

## 주의사항

* **네트워크 설정의 중요성:** VM 스펙보다 **VCN, Public Subnet, Internet Gateway, Route Rule, Public IPv4** 5가지 네트워크 설정이 SSH 접속의 핵심입니다.
* **Private Key 보안:** Private key는 서버 접속의 열쇠 그 자체이므로 **절대 공유해서는 안 됩니다.**
* **비용 주의:** `Pay As You Go` 전환 후 **Always Free 한도**를 초과하는 리소스를 만들면 **실제 과금**됩니다.
* **재고 문제:** `Out of host capacity` 에러는 오라클 측의 리소스 부족일 수 있습니다. 이 경우 다른 리전이나 Shape을 확인해야 합니다.

## 출처
[🖥️Oracle Cloud 무료로 24시간 AI 서버 만들기 (초보자가 막히는 7가지 포함)](https://oracleserverbyaduai.netlify.app/?fbclid=PAVERFWASJXnBleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeBx0OBKXkHoiVSotXm3MbmCk1vgJinL9v1XftySx8dZwgGK4w0vCcT150CWg_aem_k9xiu7z2YBb6S9KSm9VQLg

## 출처

- [https://oracleserverbyaduai.netlify.app/?fbclid=PAVERFWASJXnBleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeBx0OBKXkHoiVSotXm3MbmCk1vgJinL9v1XftySx8dZwgGK4w0vCcT150CWg_aem_k9xiu7z2YBb6S9KSm9VQLg](https://oracleserverbyaduai.netlify.app/?fbclid=PAVERFWASJXnBleHRuA2FlbQIxMABzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeBx0OBKXkHoiVSotXm3MbmCk1vgJinL9v1XftySx8dZwgGK4w0vCcT150CWg_aem_k9xiu7z2YBb6S9KSm9VQLg)
