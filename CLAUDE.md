# 결과지 제작 프로젝트 지침

무하유 HR SaaS 결과지 목업을 제작하는 프로젝트입니다.

---

## ⛔ 절대원칙 [예외 없음 - 코드 작성 전 반드시 확인]

아래 3가지는 협의나 상황에 따른 예외가 없는 절대 규칙이다. 위반 시 결과물로 간주하지 않는다.

**원칙 1. 한 페이지는 반드시 A4 사이즈로 구현한다**
- `.page` 클래스에 `width: 990px`, `height: 1399px`, `overflow: hidden` 고정
- `min-height` 사용 금지. 반드시 `height`로 고정
- `overflow: hidden`은 화면에서 넘침을 즉시 감지하기 위한 장치. 생략 불가
- `@page { size: A4; margin: 0; }` 및 `print-color-adjust: exact` 필수 포함

**원칙 2. 모든 페이지에 헤더와 푸터가 들어간다. 노출 내용은 동일하다**
- 예외 페이지 없음. 1페이지든 마지막 페이지든 동일하게 적용
- 헤더 높이 27px 고정 / 푸터 높이 34px 고정 / `flex-shrink: 0` 필수
- 페이지마다 헤더·푸터 HTML을 직접 작성한다 (공유 컴포넌트 없음)

**원칙 3. 페이지브레이크를 적용하되, 콘텐츠가 중간에 잘려서는 안 된다**
- 각 A4 페이지는 반드시 `<div class="page">` 단위로 분리
- 콘텐츠를 배치하기 전에 페이지 높이를 계산한다: `1399 - 27(헤더) - 34(푸터) = 1338px`
- 카드·테이블·문항 카드 등 하나의 블록은 페이지 안에서 잘리지 않게 배치
- `flex-shrink: 0`을 블록 단위 요소에 적용해 눌림 방지

---

## 편집디자인 원칙

결과지는 인쇄 기반 문서입니다. 수치 스펙을 적용하기 전에 아래 원칙을 이해하고 따를 것.

### 1. 판형과 타입 에리어

- 판형: A4 (210×297mm) = 990×1399px (120dpi 기준)
- 타입 에리어(실제 콘텐츠 영역): 좌우 각 24px 여백 제외한 942px
- 헤더(27px)와 푸터(34px)는 타입 에리어 밖 고정 영역. 콘텐츠가 침범하면 안 됨
- 1페이지 지원자 카드도 타입 에리어 내 최상단에 위치. 이후 콘텐츠는 카드 아래부터 시작

**HTML 페이지 단위 구조 [필수]**

각 A4 페이지는 반드시 `.page` div로 감싸야 한다. 이 구조 없이는 페이지 브레이크가 동작하지 않는다.

```html
<div class="page">
  <div class="page-doc-header">...</div>
  <!-- 콘텐츠 영역: 최대 높이 1338px -->
  <div class="page-footer">...</div>
</div>
<div class="page">
  <div class="page-doc-header">...</div>
  <!-- 다음 페이지 콘텐츠 -->
  <div class="page-footer">...</div>
</div>
```

**필수 CSS [이 코드 없이 작업 시작 불가]**

```css
@page {
  size: A4;
  margin: 0;
}

* {
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

body {
  margin: 0;
  padding: 0;
}

.page {
  width: 990px;
  height: 1399px;
  overflow: hidden;           /* 콘텐츠가 페이지 밖으로 넘치면 즉시 인지 가능 */
  position: relative;
  page-break-after: always;
  box-sizing: border-box;
}

.page:last-child {
  page-break-after: avoid;
}
```

> **경고**: `.page`에 `overflow: hidden`을 반드시 적용할 것. 콘텐츠가 1399px를 초과하면 브라우저에서는 스크롤로 보이지만 인쇄 시 잘린다. `overflow: hidden`이 있으면 목업 단계에서 넘침을 즉시 발견할 수 있다.

### 2. 타이포그래피 위계와 용도

타입 스케일은 크기 나열이 아닌 정보 위계를 표현하는 수단임. 아래 용도를 지켜야 함.

| 스케일 | 용도 | 적용 위치 |
|--------|------|-----------|
| Bold 32px | 지원자 이름 | 지원자 카드 |
| Bold 48px | 종합 점수 숫자 | BP 카드 우측 |
| Bold 24px | 채용공고명, 섹션 대제목 | 카드 상단, 페이지 섹션 |
| Bold 18px | 직무명, 카드 내 소제목 | 카드, 역량 섹션 |
| Bold 16px | 본문 강조, 수치 강조 | 테이블 내 주요 셀 |
| Regular 16px | 일반 본문 | 설명 텍스트 |
| Bold 14px | 배지 레이블, 캡션 강조 | 배지, 요약 셀 |
| Regular 14px | 일반 캡션 | 보조 설명 |
| SemiBold 12px | 헤더/푸터 고정 텍스트, 레이블 | 헤더, 푸터, 카드 메타 |
| Regular 12px | 극소 보조 정보 | 타임스탬프, 주석 |

- 같은 페이지에서 Bold 32px 이상은 2개를 넘기지 않는다 (시각 혼란 방지)
- 숫자(점수, 비율 등)는 반드시 Noto Sans 적용 (Noto Sans KR과 혼용 금지)

### 3. 정보 밀도 기준

한 페이지(990×1399px)에서 콘텐츠가 차지할 수 있는 최대 높이는 타입 에리어 기준 **1338px** (1399 - 헤더 27 - 푸터 34).

- 섹션 간격은 20px 유지. 섹션을 압축해 한 페이지에 욱여넣지 말 것
- 카드 하나의 최소 패딩은 12px. 그 이하로 줄이면 인쇄 시 콘텐츠가 테두리에 붙어 보임
- 테이블 행 높이 32px는 인쇄 가독성 최솟값. 줄이지 말 것
- 차트(레이더 225×225px, 막대 18px)는 크기 고정. 임의 축소하면 라벨이 겹침

### 4. 페이지 브레이크 규칙

**이 규칙을 어기면 출력물이 깨진다. 예외 없음.**

HTML을 A4 페이지 단위로 쪼갤 때 아래를 반드시 지킬 것.

- 각 페이지는 `.page` div(990×1399px)로 분리. 콘텐츠를 div 하나에 쭉 이어 쓰는 방식 금지
- 섹션 제목과 첫 번째 콘텐츠 행은 반드시 같은 페이지에 위치 (제목만 혼자 남기지 않음)
- 테이블은 행 중간에서 나누지 않음. 테이블 전체가 한 페이지를 초과하면 다음 페이지로 이동
- 지원자 카드는 항상 1페이지에 위치. 2페이지 이후로 이동 불가
- 페이지 당 섹션은 최대 3개. 그 이상이면 레이아웃이 과밀해짐

**`page-break-inside: avoid` 필수 적용 대상**

```css
.ev-top-sec,           /* 지원자 카드 */
.metric-card,          /* 역량 카드 */
.question-detail-card, /* 문항 상세 카드 */
.evidence-group,       /* 근거문장 그룹 */
table,                 /* 모든 테이블 */
.overview-card,        /* 응시개요 카드 */
.report-info {         /* 마지막 페이지 안내사항 */
  page-break-inside: avoid;
  break-inside: avoid;
}
```

**페이지 높이 계산 방법**

콘텐츠를 배치하기 전에 각 페이지의 높이를 계산해야 한다.

```
사용 가능한 콘텐츠 높이 = 1399 - 헤더(27) - 푸터(34) = 1338px
1페이지 추가 차감: 지원자 카드 높이 + 카드 하단 여백(20px)
```

계산 결과가 1338px를 초과하면 콘텐츠를 다음 페이지로 분리해야 한다. 계산 없이 배치하는 것은 출력물 깨짐의 주원인이다.

### 5. 시각 요소 배치 원칙

- 차트와 테이블은 텍스트 설명 뒤에 위치 (먼저 맥락, 그 다음 시각화)
- 배지는 단독 배치 금지. 반드시 레이블 텍스트 또는 수치와 함께 표시
- 색상 강조(등급 배지, 상태 알약)는 같은 페이지에서 3종 이상 동시에 사용하지 않음
- 막대 차트와 레이더 차트를 같은 섹션에 함께 쓰지 않음 (차트 중복은 정보 과잉)
- 근거문장 번호 원형(blue circle)은 한 페이지에 최대 10개. 초과 시 다음 페이지로 분리

### 6. 블리드 및 테두리 처리

- 이 결과지는 블리드(재단 여백) 없음. 페이지 가장자리까지 색상이 채워지는 디자인 금지
- 배경색 블록이 페이지 양 끝까지 닿아야 할 경우, 좌우 24px 여백 안쪽에서 끝낼 것
- 테이블은 `border-radius: 0` 필수. 카드·배지와 시각적으로 구분하기 위한 의도적 선택

---

## ⚠️ 작업 시작 전 필수 체크리스트 [모든 파일 생성/수정 시 반드시 실행]

HTML 결과지 파일을 만들거나 수정하기 전에 아래 순서를 반드시 따를 것. 하나라도 건너뛰면 작업 시작 불가.

**STEP 1. 스토리북 fetch**
- https://gongumi-sloth.github.io/HR_report/ 를 실제로 fetch하여 컴포넌트·색상·폰트 확인
- fetch 없이 기억이나 추정으로 작업 금지

**STEP 2. 더미 데이터 파일 확인**
- 프로토타입/목업 작업 시 `bp_evaluation_data.json` 파일의 데이터 구조를 참조할 것
- 점수(`scores`), 평가 항목(`evaluation`), 근거 문장(`evidence_sentences`), 자소서 문항(`essay_sections`) 등 JSON에 정의된 구조를 기준으로 콘텐츠를 채울 것
- JSON에 없는 항목(배지 레이블, 비교 수치, 코멘트 문구 등)은 기존 값을 유지하거나 임의로 설정 가능

**STEP 3. 아래 항목 전체 확인 후 코드 작성 시작**

페이지 구조 (가장 먼저 확인)
- [ ] 각 A4 페이지가 `<div class="page">` 단위로 분리되어 있음
- [ ] `.page` CSS에 `width: 990px`, `height: 1399px`, `overflow: hidden` 적용
- [ ] `@page { size: A4; margin: 0; }` CSS 포함
- [ ] `page-break-inside: avoid`가 카드·테이블·근거문장 그룹에 적용
- [ ] 각 페이지 콘텐츠 높이가 1338px 이내임을 계산으로 확인

헤더·푸터
- [ ] 모든 페이지에 헤더 포함 (높이 27px)
- [ ] 모든 페이지에 푸터 포함 (높이 34px, 로고+제품명+저작권+페이지번호)
- [ ] 1페이지 헤더 아래 지원자 카드 포함 (border-radius: 8px)

콘텐츠·스타일
- [ ] 마지막 페이지 최하단 저작권 정보 2줄 포함
- [ ] 스토리북에 없는 색상·폰트·컴포넌트 미사용
- [ ] 테이블 border-radius: 0
- [ ] 파일명 규칙 준수 ([제품명]-[지원자명]-[날짜].html)

---

## 디자인 기준
- 모든 결과지는 아래 스토리북의 디자인 시스템을 따릅니다
- 스토리북 URL: https://gongumi-sloth.github.io/HR_report/
- 스토리북에 없는 색상, 폰트, 컴포넌트 임의 사용 금지

## 페이지 레이아웃 규칙
- 구조: 헤더(고정) + 지원자 카드(1페이지만) + 콘텐츠 + 푸터(고정)
- 출력 형식: A4 PDF (CSS `@page { size: A4; }` 반드시 포함)
- 페이지 크기: 990×1399px (A4 기준 120dpi)
- 좌우 여백: 24px
- 섹션 간격: 20px
- 카드 내부 여백: 12~20px
- 기본 테두리: 1px solid #E3E3E3

## 기본 지침 [필수]
- **모든 페이지에 헤더와 푸터를 반드시 포함** (생략 불가, 위반 시 디자인 시스템 위반으로 간주)
- 적용 범위: 모든 제품(Ai Monster · 역량검사 · 교차진단 · 프리즘 BP) 전 페이지

---

## 디자인 토큰

### 기본 색상
- 주 텍스트: #041D30
- 보조 텍스트: #7D7D80
- 비활성: #6E777C
- 중립 배경: #E9E9EA
- 테두리(진): #BBBABF / 테두리(연): #E3E3E3 / 테두리(중): #A9A8AA

### 기능 색상
- Primary Blue: #0075FF
- 위험/FAIL: #FF3B30
- 경고/주의: #FF7A00
- 통과/PASS: #20AA40

### 등급 색상 (텍스트 + 배경 세트)
| 등급 | 텍스트 | 배경 |
|------|--------|------|
| S | #9330FF | #F3E8FF |
| A | #20AA40 | #E7FFEC |
| B | #F09000 | #FFF0DE |
| C | #FF006B | #FFE9F3 |
| D | #696969 | #E9E9EA |

### 폰트
- 한국어: Noto Sans KR
- 영문·숫자: Noto Sans

### 타입 스케일
- 대제목: Bold 32px / 중제목: Bold 24px / 소제목: Bold 18px
- 본문 강조: Bold 16px / 본문: Regular 16px
- 캡션 강조: Bold 14px / 캡션: Regular 14px
- 극소: Regular 12px

---

## 컴포넌트 스펙

### 문서 헤더 (모든 페이지 고정)
- 운영 클래스: `.page-doc-header`
- 높이: 27px / 패딩: 8px 24px
- 하단 테두리: 1px solid #939395
- 좌측(채용공고명): SemiBold 12px #041D30
- 우측(지원자명 + 구분선 + 지원번호): SemiBold 12px / 구분선 1×11px #939395 / 번호 Light 12px

```html
<div class="page-doc-header">
  <span class="doc-header-title">채용공고 이름</span>
  <div class="doc-header-info">
    <span class="doc-header-name">지원자 이름</span>
    <span class="doc-header-divider"></span>
    <span class="doc-header-num">지원번호</span>
  </div>
</div>
```

### 지원자 카드 [필수 - 1페이지만]
- 1페이지 헤더 바로 아래 위치
- 모서리 반드시 둥글게: `border-radius: 8px` (생략 불가)
- 운영 클래스: `.ev-top-sec`

**공통 구조 (몬스터 기준)**
- 배경: #BBBABF / 모서리: 8px / 패딩: 32px
- 채용공고명: Bold 24px / 사진: 120×120px 원형 배경 #E9EBEB
- 직무명(.profile-job): Bold 18px / 이름(.profile-name): Bold 32px / 지원번호(.profile-id): Regular 16px

**프리즘 BP 전용 구조 (사진 없음)**
- 외부 컨테이너: bg #495e76, border-radius 8px, padding 24px
- 상단 바: 채용공고명 Bold 24px #fff / 제품명 SemiBold 12px #fff
- 카드 본체 외부 배경: #C6C6C6 (1px gap이 구분선 역할), border-radius 8px
- 좌측 카드(flex:1): bg white, height 128px, padding 24px/20px
  - 직무: Bold 18px / 이름: Bold 32px / 응시번호: Regular 16px / 평가일: Bold 12px (우하단)
- 우측 카드(width 420px): bg white, padding 32px/20px
  - "종합 점수" 레이블: Bold 18px
  - 점수 숫자: Bold 48px Noto Sans
  - 상위% 배지: border 1px #0075FF, color #0075FF, Bold 14px, border-radius 17px
  - 합불 배지: bg #e0f3ff, border 1px #0075FF, color #0075FF, Bold 14px, border-radius 17px

### 등급 배지
- 높이: 26px / 모서리: 13px / Bold 14px / 패딩: 0 12px
- 등급별 배경·텍스트: 위 등급 색상 표 참조

### 상/중/하 배지
- 너비: 40px / 높이: 18px / 모서리: 2px / Bold 12px
- 상: bg #0075FF / 중: rgba(0,117,255,0.6) white / 하: rgba(0,117,255,0.2) #041D30 / 없음: bg #E9E9EA #7D7D80

### 상태 알약 (Pills)
- 높이: 22px / 모서리: 11px / Bold 12px / 패딩: 0 10px
- pill-red: bg #FFF5F5 / color #FF3B30 / border #FFCCCC
- pill-blue: bg #EBF4FF / color #0075FF / border #B3D4FF
- pill-default: bg #E9E9EA / color #7D7D80 / border #D0D0D0

### 역량 카드
- 운영 클래스: `.metric-card` + `.back-S/A/B/C/D`
- 너비: 160px / 모서리: 8px / 테두리: 1px solid 등급색 / 패딩: 14px 16px

### 메트릭 카드 스트립
- 운영 클래스: `.score-strip`
- 모서리: 8px / 패딩: 12px 14px
- 제목: 12px #7D7D80 / 점수: 18px Bold Noto Sans / 반영비율: 11px #7D7D80
- 배경: back-B=#FFF0DE / back-C=#FFE9F3 / back-D=#E9E9EA

### 테이블
- 운영 클래스: 표준 `table` 요소
- 모서리: 없음 (`border-radius: 0` - rounded 적용 금지)
- 행 높이: 32px
- 헤더 배경: rgba(0,117,255,0.06)
- 푸터 배경: rgba(0,117,255,0.15)
- 상단/하단 테두리: 1px solid #041D30
- 행 구분: 1px solid #E3E3E3

### 가로 막대 차트
- 막대 높이: 18px / 모서리: 2px
- 트랙 배경: #E9E9EA

### 레이더 차트
- 구현: Chart.js radar type
- canvas id: `metric4RadarChart` / 크기: 225×225px
- 그리드: #E3E3E3 / 평균선: #96A4B1
- 지원자 영역: rgba(0,117,255,0.28) / 선: #2EA6FF

### Factor 점수 표시
- 운영 클래스: `.factor-line` / `.factor-grade.none/.low/.mid/.high`
- 크기: 36×20px / 모서리: 2px / Bold 11px
- 없음: bg #E9E9EA color #7D7D80
- 하: rgba(0,117,255,0.2) color #041D30
- 중: rgba(0,117,255,0.6) color #fff
- 상: bg #0075FF color #fff

### 근거문장
- 운영 클래스: `.evidence-group` / `.evidence-factor` / `.evidence-sentence` / `.sentence-no`
- 번호 원형: 20px bg #0075FF white Bold 10px
- 근거 문장 강조: bg rgba(0,117,255,0.08)
- 빈 항목 텍스트: Regular 12px #A9A8AA

### 문항 상세 카드
- 운영 클래스: `.question-detail-card`
- 문항 헤더(.question-head-comp): 배경 #F8F9FA / 패딩 12px 16px
- 개요(.question-summary-comp): 5열 균등 분할 / 각 셀 패딩 10px 12px
- 답변 요약: 배경 #F8F9FA / 모서리 6px / 패딩 10px 14px
- 질문 유형 태그: 기본 bg #EBF4FF color #0075FF / 꼬리 bg #F0F0F0 color #696969 / 높이 18px 모서리 3px

### 종합평가 패널
- 운영 클래스: `aside.ev-sec.sec-score` / `.total-card` / `.trust-box`
- 점수 숫자: Noto Sans Bold 36px
- 신뢰불가: #FF3B30 / 통과: #20AA40 / 확인필요: #E9E9EA

### 응시개요 카드
- 운영 클래스: `.overview-card` / `.overview-grid`
- 4열 grid / 셀 패딩: 10px 14px
- 레이블: 11px #7D7D80 / 값: 13px Bold #041D30
- 구분선: 1px solid #E3E3E3 (가로/세로)

---

## 제품별 색상 테마
- 몬스터: #6B1FCC → #9330FF (그라디언트)
- 역량검사: #08174A (Figma 추정값, 정확한 코드는 개발팀 확인 필요)
- 교차진단: #004FCC → #0075FF (그라디언트)
- 프리즘 BP: #0A47A0 → #0F71E3 (그라디언트)

---

## 푸터 규칙 [필수 - 모든 페이지]
- 높이: 34px / 상단 테두리: 1px solid #7D7D80 / 패딩: 0 24px
- 좌측: 제품 로고 이미지 + 제품명 텍스트 (SemiBold 12px #041D30, gap 6px)
- 중앙: 저작권 문구 (SemiBold 7px #6E777C)
- 우측: 페이지 번호 (SemiBold 12px #041D30)

### 로고 파일 및 표시 크기
| 제품 | 로고 파일 | 표시 높이 |
|------|-----------|-----------|
| 몬스터·역량검사 | logo/logo_aimonster.png | height: 10px |
| 교차진단·프리즘 BP | logo/logo_prism.png | height: 16px |
| 교차진단 | logo/logo_prism.png + logo/logo_aimonster.png (둘 다) | - |

### 저작권 문구 (푸터 중앙)
> Copyright © 2026 muhayu Inc. All rights reserved.
> 본 결과의 평가 기준, 문항, 분석 내용 등 모든 지적재산권은 ㈜무하유에 귀속됩니다. 무단 복제 및 재배포를 금합니다.

---

## 마지막 페이지 안내사항 [필수]
- 운영 클래스: `.report-info` / `.report-info-item` / `.help-icon` + `.report-info-text`
- 위치: 마지막 페이지 하단
- 카드 배경: #FFFFFF / 모서리: 8px / 패딩: 24px 28px
- 항목 간격: 16px
- 아이콘: 원형 20px 테두리 ⓘ
- 텍스트: Regular 13px #041D30 / 행간: 1.7
- 항목 2줄 구성 (ⓘ 아이콘 각 줄 앞에 배치)

**1번째 줄 (제품별)**
- 프리즘 BP: 본 리포트는 AI 기술을 활용하여 자기소개서 내 텍스트의 구조적 특성과 기준 충족 여부를 분석한 참고 자료입니다. 본 결과는 자동으로 합격/불합격을 결정하지 않으며, 채용과 관련된 모든 최종 판단은 사람의 검토를 통해 이루어집니다. AI 분석에는 기술적 한계가 존재할 수 있으며, 단일 결과에 의존하지 않고 종합적인 판단 자료로 활용하시기 바랍니다.
- Ai monster·역량검사: 본 리포트는 AI 기술을 활용하여 면접 답변 내 텍스트의 구조적 특성과 기준 충족 여부를 분석한 참고 자료입니다. 본 결과는 자동으로 합격/불합격을 결정하지 않으며, 채용과 관련된 모든 최종 판단은 사람의 검토를 통해 이루어집니다. AI 분석에는 기술적 한계가 존재할 수 있으며, 단일 결과에 의존하지 않고 종합적인 판단 자료로 활용하시기 바랍니다.

**2번째 줄 (모든 제품 동일)**
> 본 문서에 포함된 개인정보는 「개인정보보호법」 및 「채용절차의 공정화에 관한 법률」에 따라 처리되며, 채용 이외의 목적으로 사용하거나 제3자에게 제공할 수 없습니다.

---

## 목업 전용 UI 안내 [열람자 주의]
- HTML 프로토타입 최상단에 [◀ 이전 / 다음 ▶] 페이지 이동 버튼이 표시됨
- 이는 브라우저에서 다중 페이지를 한 장씩 확인하기 위한 **목업 전용 UI**
- **실제 구현(PDF 출력 또는 서버 렌더링) 시에는 출력되지 않음**
- 기획자·열람자에게 혼동을 줄 수 있으므로 공유 시 반드시 이 점을 안내할 것

---

## 파일 규칙
- 파일명: [제품명]-[지원자명]-[날짜].html
  - 예: monster-홍길동-20260525.html
- 한 파일 = 한 지원자의 결과지
- 결과지는 단일 HTML 파일로 제작 (외부 CSS/JS 파일 분리 금지)
