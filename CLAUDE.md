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

### 0. 레이아웃 기초 원칙 (CRAP)

모든 레이아웃 결정은 아래 4가지 원칙을 기준으로 판단한다. 디자인이 어색하게 느껴질 때 이 원칙 중 어느 것이 깨졌는지 먼저 확인할 것.

**Contrast (대비)**
- 중요한 정보와 덜 중요한 정보는 시각적으로 확실히 달라야 한다
- 크기, 굵기, 색상 중 하나 이상으로 명확히 구분할 것
- 모든 요소가 비슷한 크기·굵기·색이면 아무것도 강조되지 않은 것과 같다
- 같은 페이지에서 강조 요소는 3개 이내로 제한. 그 이상이면 강조의 의미가 사라진다

**Repetition (반복)**
- 같은 역할의 요소는 항상 같은 모양으로 표현한다
- 예: 섹션 제목은 항상 같은 폰트·크기·색 / 배지는 항상 같은 형태
- 한 페이지 안에서 레이아웃 패턴이 중간에 바뀌면 안 된다
- 반복은 통일감을 만들고, 통일감은 문서의 신뢰감을 만든다

**Alignment (정렬)**
- 모든 요소는 보이지 않는 수직선 또는 수평선에 정렬되어야 한다
- 임의로 배치하거나 "대충 가운데"로 맞추지 않는다
- 같은 레벨의 정보는 반드시 같은 시작점(좌측 기준선)에서 출발한다
- 정렬이 맞지 않으면 레이아웃이 어수선하고 비전문적으로 보인다

**Proximity (근접)**
- 관련 있는 정보는 가까이, 관련 없는 정보는 멀리 배치한다
- 카드(섹션) 간 여백은 카드 내부 여백보다 반드시 커야 한다
- 여백이 없으면 정보 간 경계가 사라져 독자가 구조를 파악하지 못한다
- 여백은 "빈 공간"이 아니라 정보를 묶고 분리하는 디자인 요소다

---

### 0-1. 시각적 위계 (Visual Hierarchy)

페이지를 처음 봤을 때 "무엇이 가장 중요한가"가 즉시 보여야 한다.

- 가장 중요한 정보가 가장 크고 굵고 눈에 띄어야 한다
- 중요도에 따라 크기·굵기·색이 단계적으로 줄어들어야 한다
- 위계 단계는 최대 3단계. 그 이상은 구조가 복잡해 보인다
  - 예: 섹션 제목(대) > 항목명(중) > 보조 설명(소)
- 숫자(점수)는 텍스트보다 크게. 결과지에서 숫자가 핵심 정보다
- 같은 페이지에서 Bold 32px 이상 요소는 2개 이내로 제한

---

### 0-2. 그리드와 레이아웃 균형

- 이 결과지는 990px 너비, 좌우 24px 여백 기준 942px 타입 에리어를 사용한다
- 2단 레이아웃(좌/우 분할) 시 비율은 콘텐츠 양에 따라 결정한다
  - 정보량이 비슷하면 1:1 (약 50:50)
  - 한쪽이 많으면 2:1 또는 3:1로 조정. 억지로 같은 너비로 맞추지 않는다
- 카드 높이는 내용에 따라 자동 조정되어야 한다. 고정 높이로 인해 한쪽 카드에 과도한 여백이 생기면 안 된다
- 한 행에 카드가 3개 이상일 경우, 모든 카드의 정보 밀도가 비슷해야 한다. 한 카드만 내용이 많으면 행 분리를 검토한다
- 하단 마무리 카드 행은 상단 레이아웃 패턴과 일관성을 유지한다. 상단이 2단이면 하단도 2단 기준으로 구성한다

---

### 0-3. 게슈탈트 원리 적용

사람이 시각 정보를 인식하는 방식을 따른다.

- **근접성**: 가까운 요소는 하나의 그룹으로 인식된다. 의도적으로 묶거나 분리할 것
- **유사성**: 같은 모양·색·크기의 요소는 같은 종류로 인식된다. 다른 의미면 다르게 표현할 것
- **연속성**: 줄 맞춤이 되어 있으면 자연스럽게 시선이 흐른다. 정렬을 통해 읽기 흐름을 유도할 것
- **폐쇄성**: 테두리나 배경색으로 영역을 명확히 구분하면 독자가 구조를 빠르게 파악한다

---

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
- 프로토타입/목업 작업 시 `data/bp_evaluation_data.json` 파일의 데이터 구조를 참조할 것
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

> 프리즘 BP는 등급을 S/A/B/C/D 대신 **높음/중간/낮음/없음(파랑 계열)** 으로 표현한다 → 아래 '프리즘 BP 색상' 참조. (S/A/B/C/D 등급 색상은 다른 제품에서 사용)

### 프리즘 BP 색상
> **주 사용 제품:** 프리즘 BP (참고). 경고색·등급 표현이 달라 기존 토큰과 **공존**한다(기존 토큰을 덮어쓰지 말 것). 다른 제품에서도 필요하면 재사용 가능.

- 헤더·하드스킬 배경: #495E76
- 카드 경계(진): #C6C6C6 / 낮음·박스 배경: #F4F4F4
- 경고·검토: #D75D00 (다른 제품 경고색 #FF7A00과 별개)
- AI 작성 의심 강조: #F09000 (밑줄 `.gpk`, AI 비율 수치)
- 근거 문장 강조: rgba(0,117,255,0.10) (`.hl`)
- 등급 표현(높음/중간/낮음/없음, 파랑 계열): 높음 rgba(0,117,255,0.6) / 중간 #E9E9EA / 낮음 #F4F4F4 / 없음 #F4F4F4 (없음=낮음 동일색 통일 2026-06-17 / 텍스트색은 컴포넌트 상세 참조)
- 레이더 차트: 평균 영역 rgba(150,164,177,0.30)·선 #96A4B1 / 지원자 영역 rgba(0,117,255,0.28)·선 #2EA6FF

### 폰트
- 한국어: Noto Sans KR
- 영문·숫자: Noto Sans

### 타입 스케일
- 대제목: Bold 32px / 중제목: Bold 24px / 소제목: Bold 18px
- 본문 강조: Bold 16px / 본문: Regular 16px
- 캡션 강조: Bold 14px / 캡션: Regular 14px
- 극소: Regular 12px

---

## 제품군 표기 규칙 [참고 정보]

무하유 HR 결과지의 모든 제품(프리즘 BP·몬스터·역량검사·교차진단·피드백리포트)은 **하나의 패밀리 디자인 시스템을 공유**한다. 컴포넌트는 제품 간 자유롭게 재사용할 수 있으며, 궁극 목표는 **통합된 HR 제품 패밀리 디자인의 완성**이다.

각 컴포넌트에 적는 **`주 사용 제품`은 '현재 주로 쓰이거나 처음 도입된 제품'을 알려주는 참고 정보일 뿐, 사용 제한이 아니다.** 다른 제품에 가져다 써도 된다.

**제품군 목록** (향후 추가될 수 있음)

| 제품군 | 설명 | 비고 |
|--------|------|------|
| 프리즘 BP | 자기소개서 기반 평가 | 현재 가장 완성도 높음. source of truth: `한일시멘트/template-bp42.html` |
| 몬스터 | AI 면접 (Ai Monster) | |
| 역량검사 | 역량검사 4.0 | |
| 교차진단 | 교차검증 진단 (프리즘 × 역량검사 / 몬스터 × 역량검사) | source of truth: 스토리북(index.html) 교차진단 컴포넌트 · Figma 「교차진단」 (2026-07-27 반영) · 몬×역: `교차검증/교차진단-몬x역-샘플-20260728.html` (2026-07-28) |
| 피드백리포트 | 피드백 리포트 | 디자인 토큰 정의 예정 |
| 리더십 진단 | 역량검사 4.0 기반 경영진 리더십 보고서 | source of truth: `리더십진단/leadership-디자인목업-20260614.html` |
| 공통 | 전 제품 공용 | 헤더·푸터 등 |

**표기 방법** — 각 컴포넌트 스펙 첫 줄에 다음을 적는다.

- `- **주 사용 제품:** 프리즘 BP` (단일)
- `- **주 사용 제품:** 프리즘 BP · 역량검사` (복수)
- `- **주 사용 제품:** 공통` (전 제품)

> **참고**: 같은 역할이라도 제품마다 표현이 다를 수 있다(예: 등급 — 프리즘 BP는 높음/중간/낮음/없음, 몬스터·역량검사는 S/A/B/C/D). 재사용할 땐 맥락에 맞는 변형을 고르면 된다 — 금지가 아니라 선택의 문제다.

---

## 프리즘 BP 페이지 구조와 네이밍
> **주 사용 제품:** 프리즘 BP / source of truth: `한일시멘트/template-bp42.html`

프리즘 BP 결과지는 **고정 3페이지 + 동적 상세 페이지(P4+)** 로 구성된다. CSS 클래스는 **페이지별 prefix**를 따른다.

**네이밍 컨벤션 (페이지별 prefix)**

| prefix | 페이지 | 용도 |
|--------|--------|------|
| `bp-` | P1 | 상단 헤더·종합점수 카드 |
| `summary-` `jma` `side-` `cbar` | P1 | 요약 카드, 직무적합도, 사이드 카드, 비교 막대 |
| `vp-` | P2 | 검증 포인트 카드 |
| `qtable` `qrow` | P2 | 문항별 검사 결과 테이블 |
| `p3-` | P3 | 자기소개서 분석 (근거 강조 `.hl` / AI 의심 `.gpk`) |
| `dt-` | P4+ | BP 평가 상세 (대분류·중분류·하드스킬) |
| `.num` | 전체 | 숫자(점수·비율)에 Noto Sans 적용용 클래스 |

**페이지 구성**

- **P1**: 문서 헤더 → BP 헤더/종합점수 카드(`bp-`) → 요약 카드(`summary-`) → 2열 콘텐츠(직무적합도 `jma` + 레이더 `chart-card` / 조직·지원동기 `side-card`) → 푸터
- **P2**: 문서 헤더 → 검증 포인트(`vp-`, 강점/검토 2카드) → 문항별 검사 결과 테이블(`qtable`) → 푸터
- **P3**: 문서 헤더 → 자기소개서 분석(`p3-` 카드들) → 푸터
- **P4+**: 문서 헤더 → BP 평가 상세(`dt-`) → 푸터. **콘텐츠 양에 따라 페이지 수 자동 결정**

**자동 페이지 분할 [프리즘 BP]**

P4+ 상세 평가는 JS가 각 블록 높이를 측정해 A4 가용 높이(1338px) 초과 시 자동으로 다음 페이지로 분할한다.

- 헤더·푸터를 페이지마다 복제
- 섹션 헤더(`dt-cat`/`dt-subcat`/`dt-hardcat`/`dt-sec-title`)가 페이지 끝에 고아로 남지 않도록 다음 블록과 함께 이동
- 연속 페이지 첫 행에 `dt-conttop`(상단 구분선) 부여
- 페이지 번호는 실제 `.page` 수에 맞춰 `n/total` 동적 할당

---

## 컴포넌트 스펙

### 문서 헤더 (모든 페이지 고정)
- **주 사용 제품:** 공통
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
- **주 사용 제품:** 공통 (제품별 변형: 몬스터·프리즘 BP·교차진단 — 교차진단 변형은 아래 '교차진단 컴포넌트' 참조)
- 1페이지 헤더 바로 아래 위치
- 모서리 반드시 둥글게: `border-radius: 8px` (생략 불가)
- 운영 클래스: `.ev-top-sec`

**공통 구조 (몬스터 기준)**
- 배경: #BBBABF / 모서리: 8px / 패딩: 32px
- 채용공고명: Bold 24px / 사진: 120×120px 원형 배경 #E9EBEB
- 직무명(.profile-job): Bold 18px / 이름(.profile-name): Bold 32px / 지원번호(.profile-id): Regular 16px

**프리즘 BP 구조 (사진 없음 변형)**
- 외부 컨테이너: bg #495e76, border-radius 8px, padding 24px
- 상단 바: 채용공고명 Bold 24px #fff / 제품명 SemiBold 12px #fff
- 카드 본체 외부 배경: #C6C6C6 (1px gap이 구분선 역할), border-radius 8px
- 좌측 카드(flex:1): bg white, height 128px, padding 24px/20px
  - 직무: Bold 18px / 이름: Bold 32px / 응시번호: Regular 16px / 평가일: Bold 12px (우하단)
- 우측 카드(width 420px): bg white, padding 32px/20px
  - "BP평가 점수" 레이블: Bold 18px
  - 점수 숫자: Bold 48px Noto Sans
  - 배지 `.bp-badges` (상위% + 합불) → 아래 '종합점수 배지 (bp-badge)' 참조

### 등급 배지
- **주 사용 제품:** (미확정)
- 높이: 26px / 모서리: 13px / Bold 14px / 패딩: 0 12px
- 등급별 배경·텍스트: 위 등급 색상 표 참조

### 상/중/하 배지
- **주 사용 제품:** (미확정)
- 너비: 40px / 높이: 18px / 모서리: 2px / Bold 12px
- 상: bg #0075FF / 중: rgba(0,117,255,0.6) white / 하: rgba(0,117,255,0.2) #041D30 / 없음: bg #E9E9EA #7D7D80

### 상태 알약 (Pills)
- **주 사용 제품:** (미확정)
- 높이: 22px / 모서리: 11px / Bold 12px / 패딩: 0 10px
- pill-red: bg #FFF5F5 / color #FF3B30 / border #FFCCCC
- pill-blue: bg #EBF4FF / color #0075FF / border #B3D4FF
- pill-default: bg #E9E9EA / color #7D7D80 / border #D0D0D0

### 역량 카드
- **주 사용 제품:** (미확정)
- 운영 클래스: `.metric-card` + `.back-S/A/B/C/D`
- 너비: 160px / 모서리: 8px / 테두리: 1px solid 등급색 / 패딩: 14px 16px

### 메트릭 카드 스트립
- **주 사용 제품:** (미확정)
- 운영 클래스: `.score-strip`
- 모서리: 8px / 패딩: 12px 14px
- 제목: 12px #7D7D80 / 점수: 18px Bold Noto Sans / 반영비율: 11px #7D7D80
- 배경: back-B=#FFF0DE / back-C=#FFE9F3 / back-D=#E9E9EA

### 테이블
- **주 사용 제품:** (미확정)
- 운영 클래스: 표준 `table` 요소
- 모서리: 없음 (`border-radius: 0` - rounded 적용 금지)
- 행 높이: 32px
- 헤더 배경: rgba(0,117,255,0.06)
- 푸터 배경: rgba(0,117,255,0.15)
- 상단/하단 테두리: 1px solid #041D30
- 행 구분: 1px solid #E3E3E3

### 가로 막대 차트
- **주 사용 제품:** (미확정)
- 막대 높이: 18px / 모서리: 2px
- 트랙 배경: #E9E9EA

### 레이더 차트
- **주 사용 제품:** (미확정)
- 구현: Chart.js radar type
- canvas id: `metric4RadarChart` / 크기: 225×225px
- 그리드: #E3E3E3 / 평균선: #96A4B1
- 지원자 영역: rgba(0,117,255,0.28) / 선: #2EA6FF

### Factor 점수 표시
- **주 사용 제품:** (미확정)
- 운영 클래스: `.factor-line` / `.factor-grade.none/.low/.mid/.high`
- 크기: 36×20px / 모서리: 2px / Bold 11px
- 없음: bg #E9E9EA color #7D7D80
- 하: rgba(0,117,255,0.2) color #041D30
- 중: rgba(0,117,255,0.6) color #fff
- 상: bg #0075FF color #fff

### 근거문장
- **주 사용 제품:** (미확정)
- 운영 클래스: `.evidence-group` / `.evidence-factor` / `.evidence-sentence` / `.sentence-no`
- 번호 원형: 20px bg #0075FF white Bold 10px
- 근거 문장 강조: bg rgba(0,117,255,0.08)
- 빈 항목 텍스트: Regular 12px #A9A8AA

### 문항 상세 카드
- **주 사용 제품:** (미확정)
- 운영 클래스: `.question-detail-card`
- 문항 헤더(.question-head-comp): 배경 #F8F9FA / 패딩 12px 16px
- 개요(.question-summary-comp): 5열 균등 분할 / 각 셀 패딩 10px 12px
- 답변 요약: 배경 #F8F9FA / 모서리 6px / 패딩 10px 14px
- 질문 유형 태그: 기본 bg #EBF4FF color #0075FF / 꼬리 bg #F0F0F0 color #696969 / 높이 18px 모서리 3px

### 종합평가 패널
- **주 사용 제품:** (미확정)
- 운영 클래스: `aside.ev-sec.sec-score` / `.total-card` / `.trust-box`
- 점수 숫자: Noto Sans Bold 36px
- 신뢰불가: #FF3B30 / 통과: #20AA40 / 확인필요: #E9E9EA

### 응시개요 카드
- **주 사용 제품:** (미확정)
- 운영 클래스: `.overview-card` / `.overview-grid`
- 4열 grid / 셀 패딩: 10px 14px
- 레이블: 11px #7D7D80 / 값: 13px Bold #041D30
- 구분선: 1px solid #E3E3E3 (가로/세로)

### 가이드 안내문 (guide-note)
- **주 사용 제품:** 공통 (교차진단 '역량별 체크포인트'에서 도입 — 섹션·블록의 분류 기준/해석/읽는 법 등 가이드 텍스트 공용)
- 구조: icon_info.svg (20px / #939395 / `../icons/`) + 본문 Regular 14px #7D7D80 / line-height 1.6 / gap 10px / 좌우 패딩 2px / 아이콘은 첫 줄 상단 정렬(align-items flex-start)
- 줄 구성: 1~2줄 권장 — 1줄 = 분류 기준·규칙 정의 / 2줄 = 해석·권장. 본문 강조는 Bold 14 (색 변경 금지)
- ⚠ 마지막 페이지 '안내사항'(법무 고정 문구 · 카드 박스 · Regular 16)과는 **별개 컴포넌트 — 혼용 금지**

---

> ## ── 이하 프리즘 BP 컴포넌트 ──
> 아래는 프리즘 BP에서 도입한 컴포넌트(**주 사용 제품: 프리즘 BP**, 참고). 다른 제품에서도 재사용할 수 있다. source of truth: `한일시멘트/template-bp42.html`.
> 배치·네이밍은 위 '프리즘 BP 페이지 구조와 네이밍' 참조.

### 종합점수 배지 (bp-badge) — P1 종합점수 카드
- **주 사용 제품:** 프리즘 BP
- 컨테이너 `.bp-badges`: flex column / gap 8px (종합점수 카드 우측, 점수 아래)
- 공통 `.bp-badge`: border 1px #0075FF / border-radius 17px / padding 4px 12px / Bold 14px / #0075FF / text-align center / nowrap
- **outline `.bp-badge` (직군 내 위치)**: 예) "생산직 상위 50%" — 비교집단 내 상위 % (공채형=전형 전체 / 수시형=준거집단)
- **fill `.bp-badge.fill` (합불 표현)**: width 132px. **두 기준 중 택1** (접수 단계에서 선택, 미선택 시 결과지에 미표시). **긍정=파랑 `.fill`(bg #E0F3FF·#0075FF), 부정=주황 `.fill.over`(bg rgba(215,93,0,0.1)·border·텍스트 #D75D00 = '확인되지 않은 하드스킬'색)**:
  - ① n배수 기준: `n배수 이내`(파랑) / `n배수 초과`(주황) — 순위가 n배수 컷을 초과
  - ② 점수 기준: `권장`(파랑, 50점 이상) / `검토 필요`(주황, 50점 미만)
  - ※ AI기본법상 '적격/부적격' 직접 표현을 피하기 위한 대체 표현 (추천/보류·권장/검토 필요) — SDS r25. 부정 케이스 주황 톤 통일(2026-06-16)
- 검증포인트의 상위%/하위% 배지는 `.vp-badge`(아래 검증 포인트) 참조

### 요약 카드 (P1)
- **주 사용 제품:** 프리즘 BP
- 운영 클래스: `.summary`(외곽) / `.summary-card`(본체)
- 외곽 `.summary`: bg #E3E3E3 / padding 24px / border-radius 0 0 8px 8px (상단 종합점수 카드와 이어지는 하단 모서리)
- 본체 `.summary-card`: bg #fff / border 1px #E3E3E3 / border-radius 8px / padding 20px 24px / flex column / gap 12px
- 상단 텍스트 `.summary-txt`: 좌(제목)·우(불릿) 양끝 정렬. **불릿 시작점 = 응시자 카드 좌/우 분할선(우측 점수카드 좌측 x546)에 정렬**(CH-024)
  - 제목 `.summary-headline`: Bold 18px / **line-height 1.3 / width 470px** (행간 압축·폭으로 불릿과 정렬·간격 확보)
  - 불릿 `.summary-bullets`(=PAC 자소서 요약): Regular **12px / width 395px / 1열** / li line-height 1.4. **응시자별 4~5개 권장**. PAC 불릿이 5개 초과/장문이면 폰트·행간·열수 재조정(CH-024). 출처: PAC(자소서 요약 결과), '내용 변경 없이' 적용이 원칙이나 슬롯 초과 시 압축 협의
- 구분선 `.summary-divider`: height 1px / bg #E3E3E3
- 위치 표시 `.summary-pos`: flex / align-center / gap 24px / margin-top 8px
  - 소제목 `.summary-pos-title`: Bold 16px / letter-spacing 0.024px
  - 점수 `.summary-pos-score`: Bold 32px Noto Sans(`.num`) / line-height 1.25
  - 막대 영역 `.summary-pos-bars`: flex 1 / column / gap 12px → 비교막대(`cbar`) 사용

#### 비교 막대 (cbar)
- 운영 클래스: `.metric-bar`(래퍼) / `.cbar`(막대) / `.cbar.mini`(소형)
- 막대 `.cbar`: height 16px (mini 14px) / position relative
- 트랙 `.cbar-track`: bg #E9E9EA / border-radius 4px / inset 0
- 채움 `.cbar-fill`: height 16px / border-radius 4px / 채움색은 등급별 파랑 계열(inline 지정)
- 위치 점 `.cbar-dot`: 12×12px 원형 (지원자 위치 표시)
- 범례 `.cbar-legend`: flex wrap / gap 6px 16px / 14px #7D7D80 / 스와치 `.sw` 12×12px 원형

#### 등급 칩 (g-*) — 프리즘 BP 등급 표현
- 운영 클래스: `.grade` + `.g-high/.g-mid/.g-low/.g-none`
- 크기: 20×20px / border-radius 4px / Bold (테이블 셀 내에선 12~14px)
- 칩 안 표시 글자: 높음 `상` / 중간 `중` / 낮음 `하` / 없음 `-`
- 높음 `.g-high`: bg rgba(0,117,255,0.6) / #fff
- 중간 `.g-mid`: bg #E9E9EA / #041D30
- 낮음 `.g-low`: bg #F4F4F4 / #7D7D80
- 없음 `.g-none`: bg #F4F4F4 / #7D7D80 (판단불가 — 낮음과 동일색 통일 2026-06-17)

### 직무적합도 카드 (P1)
- **주 사용 제품:** 프리즘 BP
- 운영 클래스: `.card.jma` (P1 좌측 메인 열 `.col-main` 내부)
- 카드 베이스 `.card`: border 1px #C6C6C6 / border-radius 8px
- `.jma`: height 444px(고정, Figma) / padding 20px 24px / flex column / gap 12px
- 구성(위→아래): 제목 → 점수+비교 → 비교막대 → 등급 2열 테이블 → 하드스킬(하단 고정)
  - 제목 `.card-title`: Medium 16px / letter-spacing 0.024px / #041D30
  - 점수 행 `.side-head`: `.metric-score.num`(Bold 24px / line-height 1.4) + `.metric-cmp`(Bold 14px #7D7D80)
  - 막대: 비교막대(`cbar`) → ① 요약 카드 참조

#### 등급 2열 테이블 (grade-cols)
- 래퍼 `.grade-cols`: flex / border-top 1px #C6C6C6
- 좌측 `.gc-left`(flex 1): 대분류 행 `.grow` — flex space-between / padding 4px 12px / border-bottom 1px #C6C6C6 / 라벨 `.lbl` Bold 14px + 등급칩 `.grade` 14px
- 우측 `.gc-right`(flex 1 / border-left 1px #C6C6C6): 헤드 `.gc-right-head`(라벨 Bold 14px / border-bottom 1px #C6C6C6) + `.sub-wrap`(flex wrap / padding-left 12px)
  - 세부 행 `.srow`: flex space-between / padding 4px 12px / border-bottom 1px #E3E3E3 / **width 136px**(좁은 가용폭에 2열 수납) / 라벨 `.lbl` Regular 12px + 등급칩 `.grade` 12px
- 변형 `.grade-wrap` + `.wrow`(width 128px): 분할 헤드 없이 wrap으로 배치할 때
- 등급칩(`.grade.g-*`)은 ① 요약 카드 참조 (상/중/하/-)

#### 하드스킬 (hardskill)
- `.hardskill`: margin-top auto(카드 하단 고정) / border-top 1px #C6C6C6 / padding-top 18px / flex column / gap 8px
- 행 `.hs-row`: flex / gap 8px / align-center
  - 라벨 `.hs-label`(Bold 14px / nowrap): 확인됨 `.hs-yes` #0075FF / 미확인 `.hs-no` #D75D00
  - 값 `.hs-val`: Regular 14px #041D30 (쉼표 구분 스킬 목록)

### 조직적합도 · 지원동기 카드 (P1)
- **주 사용 제품:** 프리즘 BP
- 운영 클래스: `.row2` > `.card.card-pad` ×2 (좌측 메인 열 하단, 직무적합도 카드 아래 나란히 2개)
- `.row2`: flex / gap 12px / flex 1
- `.card-pad`: padding 20px / flex column / gap 12px / flex 1
- 구성: 제목 `.card-title`(Medium 16px) → 점수 `.side-head`(`.metric-score.num` Bold 24px + `.metric-cmp` Bold 14px #7D7D80) → 비교막대(`cbar`, 좁은 카드라 `.row2 .cbar-legend` gap 압축) → 등급 `.grade-wrap`(`.wrow` 128px)
- 직무적합도 카드(②)와 동일 패턴이며, 좁은 카드용 `wrow`(128px)를 사용

### 사이드 카드 (P1 우측)
- **주 사용 제품:** 프리즘 BP
- 운영 클래스: `.card.side-card` (P1 우측 열 `.col-side`, 레이더 카드 아래)
- `.side-card`: flex 1 / flex column
- 박스 `.side-box`(`.first` 변형: padding-bottom 24px): padding 20px 24px / flex column / gap 8px
- 헤드 `.side-head`(flex space-between): 이름 `.side-name`(Medium 16px / letter-spacing 0.024px) + 점수 `.side-score.num`(Bold 24px / line-height 20px)
- 코멘트 `.side-cmt`: Regular 14px / #7D7D80 / padding-top 6px
- 구분선 `.side-divider`: height 1px / bg #E3E3E3 / margin 0 24px
- 점수 옆 경고배지 동반 시: `.side-head .frame`(flex 1 / margin-left 12px / space-between)로 점수+배지를 묶음

### 경고 배지 (warn-badge)
- **주 사용 제품:** 프리즘 BP
- 운영 클래스: `.warn-badge`
- bg rgba(215,93,0,0.1) / border 1px #D75D00 / border-radius 12px / padding 2px 8px / Bold 14px / #D75D00
- 용도: 검토 필요·기준 미달 항목 강조

### 프리즘 BP 레이더 차트 (chart-card)
- **주 사용 제품:** 프리즘 BP (위 '레이더 차트'의 프리즘 BP 변형 — canvas id·크기·배치가 다름)
- 카드 `.card.chart-card`: width 310px / height 444px(고정) / padding 20px 24px 32px / flex column / align-center / justify space-between (P1 우측 열 `.col-side` 상단)
- 제목 `.card-title`(width 100%): "자기소개서 분석 프로파일"
- 차트 박스 `.chart-box`: 262×300px / position relative / `<canvas id="radarChart">`
- 구현: Chart.js `type:'radar'` / responsive / maintainAspectRatio:false
- 데이터셋: 직무별 평균(fill rgba(150,164,177,0.30) / 선 #96A4B1 / borderWidth 1 / order 2) · 지원자(fill rgba(0,117,255,0.28) / 선 #2EA6FF / borderWidth 1.5 / order 1) — 둘 다 pointRadius 0
- 스케일 r: min 0 / max 100 / ticks stepSize 25, 색 #A9A8AA 9px · grid·angleLines #E3E3E3 · pointLabels #041D30 Noto Sans KR 11px Bold
- 범례: 하단 / pointStyle circle / boxWidth 8 / 11px #7D7D80 / 정렬 평균→지원자

### 섹션 제목 (sec-title) — P2~P4 공통
- **주 사용 제품:** 프리즘 BP
- `.sec-title-wrap`: height 48px / flex align-center / flex-shrink 0
- `.sec-title`: position relative / inline-flex / padding-left 16px / `::before` 파란 바(width 4px / height 22.3px / #0075FF / left 0 / top 2.4px)
- `.sec-title h2`: Bold 24px / line-height 1 / letter-spacing 0.036px

### 검증 포인트 (vp-) — P2
- **주 사용 제품:** 프리즘 BP
- 래퍼 `.vp-wrap`: flex / gap 24px / align-stretch (강점·검토 2카드)
- 카드 `.vp-card`: flex 1 / border 1px #C6C6C6 / border-radius 8px / flex column / space-between / overflow hidden
- 헤드 `.vp-head`(height 48px / gap 8px / padding 0 20px): 아이콘 24px + `.htitle`(라벨 `.lbl` Bold 18px + 부제 `.sub` 14px #7D7D80)
  - `.good`: bg rgba(0,117,255,0.1) / 라벨 #0075FF (강점, icon_grow) · `.warn`: bg rgba(255,122,0,0.1) / 라벨 #D75D00 (검토, icon_warning)
- 항목 `.vp-item`(padding 0 24px 12px / gap 8px):
  - `.vp-item-top`(flex space-between): 좌 `.vp-cat`(카테고리 `.cat` Bold 14px #7D7D80 + `.vp-name-row` 이름 `.nm` Bold 18px + 등급 `.vp-grade`) / 우 배지 `.vp-badge`
  - 등급 `.vp-grade`(height 24px / min-width 24px / radius 4px / Bold 16px): high rgba(0,117,255,0.6)·#fff / mid #E9E9EA·#041D30 / low·none #F4F4F4·#A9A8AA
  - 배지 `.vp-badge`(radius 17px / padding 4px 12px / Bold 14px): up border 1px rgba(0,117,255,0.5)·#0075FF / down border 1px #C6C6C6·#7D7D80
  - 요약 `.vp-sum`: Regular 16px / line-height 1.6 / letter-spacing -0.16px
  - 팁 `.vp-tip`(bg #F4F4F4 / radius 4px / padding 8px 12px / gap 12px / Bold 14px): 라벨 `.tlbl` #7D7D80 + 본문 `.ttxt` #041D30
- 하단 `.vp-bottom`(border-top 1px #E3E3E3 / min-height 85px / padding 12px 20px): 라벨 `.blbl` Bold 16px(good #0075FF / warn #D75D00) + `.chips` 14px (하드스킬 목록)

### 문항별 검사 결과 테이블 (qtable) — P2
- **주 사용 제품:** 프리즘 BP
- `.qtable`: width 100% / border-top·bottom 1px #C6C6C6 (둥근 모서리 없음)
- 행 `.qrow`: **min-height 48px(가변 — 긴 문항 2줄 시 자동 확장, CH-022)** / flex align-center / padding 10px 24px / gap 16px / border-bottom 1px #E3E3E3 (마지막 행 제외). 문항번호 `.qno` flex-shrink:0·nowrap, 컬럼 플렉서블(고정 높이 의존 금지)
- 우측 지표 라벨은 **'AI 작성률'**(베이스라인 일치, CH-033에서 'AI 작성 의심'→환원). 값은 실제 % 미확보로 **GPK 탐지/미탐지**(이진값) 유지 — 탐지 #F09000 / 미탐지 #7D7D80(`.nd`). (% 확보 시 수치 전환 가능)
- 좌측 `.qleft`(flex 0 0 440px / gap 12px / 16px): 번호 `.qno` Bold + 질문 `.qtext` Medium
- 우측 `.qright`(flex 1 / align-center): 지표 `.qmetric`(flex 1 / 16px #041D30 / gap 6px) ×N — 값 `.v.num` / **AI 작성률**(라벨) `.pct` 탐지(#F09000)·미탐지(#7D7D80 `.nd`) — 값은 GPK 이진값(% 미확보, 라벨 환원 CH-033)

### 자기소개서 분석 (p3-) — P3
- **주 사용 제품:** 프리즘 BP
- 래퍼 `.p3-wrap`(flex column / padding 24px) — 상단 `.p3-title-top`(height 48px / space-between): 제목 `.p3-title-bar`(파란 바 `::before` 4×22.3px / h2 Bold 24px) + 범례 `.p3-legend`
  - 범례 `.p3-legend-hl`: bg rgba(0,117,255,0.10) / 16px / padding 2px 6px (근거문장) · `.p3-legend-ai`: border-bottom 2px #F09000 (AI 작성 의심 문장)
- 카드 묶음 `.p3-cards-wrap`(gap 24px) > 카드 `.p3-qcard`(border 1px #C6C6C6 / radius 8px / overflow hidden)
  - 헤드 `.p3-qhead`: bg #F4F4F4 / **min-height 52px(가변 — 긴 질문 줄바꿈 시 자동 확장, CH-027)** / gap 12px / padding 10px 24px / Bold 18px / line-height 1.4 (문항번호+질문). 문항번호 `span:first-child` flex-shrink:0(한 줄 유지). `white-space:nowrap` 금지(질문 잘림 방지)
  - 지표 `.p3-metric`(gap 12px / padding 10px 24px): `.p3-metric-group`(이름 `.p3-metric-name` Bold 16px + 점수 `.p3-metric-score` **Regular 16px(`.num`)**). **노출 규칙(CH-034)**: 상단=**6개 메트릭(직무적합도·조직적합도·지원동기·답변적합도·구체성·본인소개) + 점수**를 고정 순서로, 해당 문항에 **그 메트릭 영역의 factor가 하나라도 검출되면**(rollup) 표시. 답변적합도·구체성·본인소개는 factor 근거가 없어 미출현. **메트릭은 점수만 있고 상/중/하 등급이 없으므로 등급칩 대신 점수 표기**(원본에 없는 등급 임의부여 금지). `직무역량`(집계)은 컨테이너라 상단에 단독 표기 안 함 — 그 8개 분자가 검출되면 상위 메트릭 `직무적합도`가 대신 뜸
  - 본문 `.p3-body`(border-top·bottom 1px #E3E3E3 / padding 12px 24px / Regular 16px / line-height 1.6): 근거 강조 `.hl`(bg rgba(0,117,255,0.10)) / AI 의심 `.gpk`(border-bottom 2px #F09000)
  - 푸터 `.p3-qfooter`(align-items flex-start / space-between / gap 16px / padding 8px 24px): 좌 `.p3-skills`(flex-wrap / 라벨 `.p3-skills-label` Bold 14px #7D7D80 + 태그 `.p3-skill-tag` Bold 14px #041D30 **white-space nowrap**) **= 검출된 factor 전부 표시(개수 제한 없음, CH-034)** — 직무역량 집계는 컨테이너라 제외 / 우 `.p3-ai-rate`(flex-shrink 0 / 라벨 `.p3-ai-lbl` "AI 작성률" + 값 `.p3-ai-val` 탐지(#F09000)·미탐지(#7D7D80 `.nd`) 16px — GPK 이진값, 라벨 환원 CH-033)

### BP 평가 상세 (dt-) — P4+ (자동 페이지네이션)
- **주 사용 제품:** 프리즘 BP
- 소스 `#dt-source`(display:none)의 `.blk` 블록을 JS가 높이 측정해 A4 가용 높이(1338px) 초과 시 다음 `.page`로 분할 (위 '프리즘 BP 페이지 구조와 네이밍'의 자동 페이지 분할 참조). 래퍼 `.dt-wrap`: flex column / padding 24px
- 섹션 제목 `.dt-sec-title`(height 48px / `::before` 파란 바 4×22.3px / h2 Bold 24px) — 첫 상세 페이지 1회
- 대분류 `.dt-cat`(height 40px / padding 0 12px / bg #E3E3E3 / 상하 border 1px #7D7D80): 이름 `.nm` Bold 20px + 점수 `.score.num` Regular 18px
- 항목 행 `.dt-row`(flex / gap 12px / align-flex-start / padding 8px 0 12px / border-bottom 1px #E3E3E3)
  - 제목 `.dt-row-title`(width 210px / space-between / padding 0 12px): 이름 `.nm` Bold 18px (중분류 하위 항목은 `.dt-tag` Bold 14px) + 등급 `.dt-badge`(margin-top 6.8px)
  - 등급 `.dt-badge`(height 24px / min-width 24px / radius 4px / Bold 16px): high rgba(0,117,255,0.6)·#fff / mid #E9E9EA·#041D30 / low #F4F4F4·#A9A8AA / none #F4F4F4·#A9A8AA (없음=낮음 동일색 2026-06-17)
  - 본문 `.dt-row-body`(flex 1): 코멘트 `.dt-comment`(Medium 16px / line-height 1.6) + 근거 라벨 `.dt-srclabel`(Bold 14px #939395 "자기소개서 내용") + 근거 리스트 `.dt-list`(li 14px / gap 12px) / 빈 항목 `.dt-empty`(14px #A9A8AA)
- 중분류 `.dt-subcat`(padding 8px 0 / border-bottom 1px #E3E3E3): 헤드 `.dt-subcat-head`(width 210px): 이름 `.nm` Bold 18px + `.dt-badge` (하위 항목은 `.dt-row`+`.dt-tag`)
- 코멘트 전용 행 `.dt-commentrow`: min-height 70.5px / padding 10px 12px / Medium 16px
- 하드스킬 대분류 `.dt-hardcat`(bg #495E76 / padding 10px 12px): 이름 `.nm` Bold 20px #fff
  - 하드스킬 행 `.dt-hardrow`(padding 8px 0 12px / border-bottom 1px #E3E3E3): 제목 `.dt-hardrow-title`(width 226px): 스킬명 `.skn` Bold 14px(width 140px) + 감지 `.dt-detect`(min-width 55px / height 24px / radius 12px / Bold 14px) — 검출 `.yes` #0075FF / 미검출 `.no` #D75D00
  - 본문 `.dt-hardrow-body`(근거 라벨+리스트) / 근거 없음 `.dt-hardrow-empty`(min-height 40px / 14px #7D7D80 "관련 근거 문장 없음.")
- 연속 페이지 첫 행 `.dt-conttop`(border-top 1px #E3E3E3)

---

> ## ── 이하 교차진단 컴포넌트 ──
> 아래는 교차진단(프리즘 × 역량검사)에서 도입한 컴포넌트(**주 사용 제품: 교차진단**, 참고). 다른 제품에서도 재사용할 수 있다. source of truth: 스토리북(index.html) 교차진단 섹션 · Figma 「교차진단」 (2026-07-27 반영). **몬×역 변형**의 source는 `교차검증/교차진단-몬x역-샘플-20260728.html` (2026-07-28 확정, 각 컴포넌트의 '몬×역 변형' 항목 참조).

### 지원자 카드 (교차진단 변형)
- **주 사용 제품:** 교차진단
- 외곽 컨테이너: bg **#495E76 (프리즘과 동일)**, border-radius 8px, padding 24px, flex column, gap 24px
- 상단 바: 채용공고명 Bold 24px #fff / 우측 「프리즘 × 역량검사 교차진단」 Noto Sans SemiBold 12px #fff
- 카드 본체: bg #C6C6C6 + 1px gap 분할(radius 8px, overflow hidden) — 상단 행(① 인적정보+② 진단 신뢰도 | ③ 교차 유형 카드) + 하단 행(④ 다음 전형 확인 역량)
- ① 인적정보 (높이 128px 기준 — min-height로 적용, 우측 유형 카드가 더 높으면 ①·②가 세로로 채움(하단 빈 띠 금지) / 패딩 좌우 24px / gap 6px): 직무 Bold 18px / 이름(마스킹) Bold 32px / 응시번호 Regular 16px
- ② 진단 신뢰도 영역 (①과 같은 흰 셀 안, 분할선 없음 / 패딩 20px 32px / gap 24px): bg `linear-gradient(270deg, #EEF6FF 0%, #FFF 100%)`
  - 제품 행 ×2 (프리즘/역량검사): 라벨 Bold 16px(64px 고정) + 「진단 가능」 배지 — 표준 알약 outline (**w80 고정** / h30 / r17 / border 1px #0075FF / Bold 14px #0075FF)
  - 코멘트: Bold 12px #041D30, 우측 정렬(w160), 핵심 구절만 #0075FF (예: "모두 신뢰도 있게 확보")
- ③ 교차 유형 카드 (우측 고정폭 364px = 콘텐츠 300 + 패딩 32/20): 교차 유형명 Bold 24px (예: 숨은 실력자형) + 해설 Regular 14px (상단 8px 간격)
- ④ 하단 행 (패딩 20px 24px): 라벨 「다음 전형에서 확인할 역량」 Regular 14px #7D7D80 (w188) + 역량 태그 wrap (gap 8px 4px)
  - 역량 태그: h24 / r16 / 패딩 2px 8px / bg #F4F4F4 / Regular 14px #7D7D80
- ※ 점수·합불 배지 없음 — 교차진단 1P 판정은 교차 유형 텍스트가 담당
- **1P 배치: 문서 헤더 바로 아래 전폭(990px) 배치 — 좌우·상단 여백 0** (블리드 규칙 예외, radius 8 유지 — 2026-07-28 몬×역 시안 확정). 이후 콘텐츠는 타입 에리어(패딩 24) 안에서 시작
- ② 진단 신뢰도 배지의 상태 3단계는 아래 '근거칩' 참조

### 근거칩 (진단 신뢰도 배지)
- **주 사용 제품:** 교차진단 (지원자 카드 ② 진단 신뢰도 영역)
- 형태: 표준 알약 — h30 / r17 / 패딩 4px 12px / Bold 14px · 앞에 제품 라벨(Bold 16px, w64) + gap 6px
- 상태 3단계 (제품별 문구 ×2):
  - **정상**: outline — border 1px #0075FF / 텍스트 #0075FF / bg #fff — 몬스터 「평가 근거 충분」 / 역량검사 「응답 신뢰 양호」 (프리즘×역검 조합은 「진단 가능」 w80)
  - **주의(불성실 답변)**: fill — bg #F09000 / 텍스트 #fff — 「평가 근거 부족」 / 「응답 신뢰 주의」
  - **불가(부정행위 의심)**: fill — bg #FF3B30 / 텍스트 #fff — 「평가 근거 없음」 / 「응답 신뢰 불가」
- ⚠ #FF3B30(위험/FAIL)·#F09000(AI 작성률) 토큰 재사용 — 근거칩 한정 용법, 기존 토큰 의미 덮어쓰기 아님

### 페이지 타이틀 (교차진단 변형)
- **주 사용 제품:** 교차진단
- 프리즘 BP `sec-title`과 동일 위계 — **바 색·간격만 다름**: 좌측 바 4px **#939395** / 높이 24px / 텍스트 좌 8px / Bold 24px #041D30
- 여백(몬×역 확정 2026-07-28): **렌더 기준 위 24px / 아래 12px (위=아래의 2배)** — 페이지 첫 위치는 margin-top 4px(+콘텐츠 영역 패딩 20), 중간 위치는 margin-top 24px / 앞에 블록이 온 타이틀(예: 기타 역량)은 위 48px

### 교차진단 매트릭스 표
- **주 사용 제품:** 교차진단 (고유 — 역량 행 단위로 프리즘·역량검사 등급을 대조)
- 표: 상·하단 1px #041D30 / radius 0 / 좌우 보더 없음 / **4열 균등 분할** (역량 · 프리즘 · 역량검사 · 교차 패턴) — 「역량」 열만 좌측 정렬(패딩 0 12px), 나머지 중앙
- 헤더: h36 / bg #F4F4F4 / 하단 1px #A9A8AA / Medium 16px #041D30
- 행: h40 기준 / 행 구분 1px #E3E3E3 (마지막 행 제외) / 역량명 Medium 16px #041D30
- 등급 표기 (프리즘·역량검사 열): **칩 없이 텍스트 Bold 16px #041D30 + 불투명도** — 상 100% / 중 60% / 하 50% / 없음 30% (표기 영역 48×20px)
- 핵심역량 행: bg rgba(255,243,219,0.3) 강조 + 역량명 옆 태그 (bg #FFF3DB / r4 / 패딩 4~5px / Bold 12px #F09000, 높이 약 20px)
- 교차 패턴 열: 아래 '교차패턴 칩' (표 안에서 w140 고정)
- 표가 한 페이지를 넘으면 행 단위로 분할하고 헤더 행을 다음 페이지에 복제
- **몬×역 변형(2026-07-28)**: **5열**(역량 분류 rowspan 병합 · 역량 · 몬스터 · 역량검사 · 교차 패턴) / 행 높이 48px / 교차 패턴은 **칩 없이 텍스트 Bold 14 + 3색**(배경·보더 없음) — 역량 신뢰 가능 #20AA40 / 검증 필요 #F09000 / 집중 검증 필요 #FF006B / ⚠ border-collapse에서 분류 병합셀의 하단 보더(#E3E3E3)가 표 하단선(#041D30)을 덮으므로 **마지막 그룹 병합셀은 border-bottom #041D30 지정** / 매트릭스 가이드 안내문은 볼드 없이 일반체

### 교차패턴 칩
- **주 사용 제품:** 교차진단
- 형태: h24 / r12 / bg #fff / border 1px #E3E3E3 / Bold 14px — 매트릭스 표 안 w140 고정, 밖에서는 가변폭
- 5종 텍스트 색: 일치 **#20AA40** / 부분 불일치 **#F09000** / 과장의심 **#FF006B** / 숨겨진 강점 **#704AD9** / 미기재 **#7D7D80**
- 의미: 일치=두 등급 동일 · 부분 불일치=1단계 차이 · 과장의심=서류 우위(프리즘 상·역검 하) · 숨겨진 강점=역검 우위(프리즘 없음·역검 상) · 미기재=프리즘 없음·역검 하 — 경계 조합 판정은 제품 정책 기준
- **몬×역 변형은 칩 미사용** — 패턴을 텍스트형으로 표기 (위 '교차진단 매트릭스 표'의 몬×역 변형 참조)

### 기타역량 컬러칩 (상/중/하/없음)
- **주 사용 제품:** 교차진단 (역량별 체크포인트 '기타 역량' 등급 대조 행 · 차트 보조 표기)
- 크기: 32×16px / r2 / Bold 10px
- 상 bg #0075FF·#fff / 중 bg rgba(0,117,255,0.6)·#fff / 하 bg **#FF006B**·#fff / 없음 bg #E9E9EA·#7D7D80
- ⚠ 프리즘 BP 등급 칩(g-*)·표준 등급 색상과 **별개 체계로 공존** (기존 토큰 덮어쓰기 금지). 하 #FF006B는 리스크 시인성 강조용(프×역)
- **몬×역 변형(gpill, 2026-07-28)**: 동일 크기(32×16 / r2 / Bold 10) — 상 #0075FF·#fff / 중 rgba(0,117,255,0.6)·#fff / **하·없음 동일 #E9E9EA·#7D7D80** (하 #FF006B 미사용 — 참고 표기 성격, 구분은 글자로만)

### 역량별 체크포인트 (checkpoint) — 블록 5종
- **주 사용 제품:** 교차진단 (매트릭스 뒤에 오는 역량별 상세 — 면접 체크포인트)
- 자기소개서(프리즘) × 역량검사 등급 조합으로 역량을 5개 블록으로 분류. **매트릭스 교차 패턴 칩과 별개 분류 체계** (블록 = 등급 조합 구간)
- **블록 공통 구조**: 타이틀 바 → 분류 안내문 → 행 리스트 / 타이틀-콘텐츠 gap 8 / 콘텐츠 패딩 8 / 안내문-리스트 gap 20 / 행 간 16
- **타이틀 바**: h36 / 패딩 0 8 / 하단 1px #C6C6C6 / 좌: 아이콘 24px + 블록명 Bold 18 (gap 8) / 우: 등급 요약 Regular 14 + 등급 원형칩. 기타 역량은 칩 없이 「**중등급 포함** 또는 **진단불가**」 Bold 강조 텍스트
- **블록 5종** (타이틀 bg / 아이콘(icons/) / 등급 조합):

| 블록 | 타이틀 bg | 아이콘 | 등급 조합 (자소서 · 역검) |
|------|-----------|--------|--------------------------|
| 검증된 역량 | rgba(0,117,255,0.05) | icon_verified.svg #0075FF | 상 · 상 |
| 잠재된 역량 | rgba(124,82,241,0.1) | icon_potential.svg #7C52F1 | 없음·하 · 상 |
| 확인할 역량 | rgba(255,213,231,0.3) | icon_check.svg #FF006B | 상 · 하 |
| 취약한 역량 | #E3E3E3 | icon_weak.svg #041D30 | 하 · 하 |
| 기타 역량 | #F4F4F4 | icon_etc.svg #939395 | 중등급 포함 또는 진단불가 |

- **등급 원형칩**: 24×24 / r12 / bg #fff / Bold 14 #041D30 — 「없음」 2글자는 min-width 24 가로 확장
- **분류 안내문**: 공통 '가이드 안내문(guide-note)' 컴포넌트 사용 (위 컴포넌트 스펙 참조) — 1줄 분류 기준 정의 · 2줄 해석/권장
- **역량명 칩(metrix)**: w126 / bg #F4F4F4 / r8 / 패딩 0 8 / Regular 14 #041D30 중앙 — 해설형·대조형 h26, 질문형은 행 높이 세로 스트레치
- **행 유형 3종**:
  - ① 해설형 (검증된): 칩 + 해설 Regular 14 #041D30 (행 내부 gap 12)
  - ② 질문형 (잠재된·확인할): 칩 + 「Q.」+질문 Bold 16(tracking 0.024) + 근거 박스(1px #E3E3E3 / r8 / 패딩 12 — 「자기소개서 | 」 Regular 14 #7D7D80 + 내용 #041D30), Q행-박스 gap 8
  - ③ 등급 대조형 (기타): 칩 + 「프리즘/역량검사」 Regular 14 #939395 + 기타역량 컬러칩 32×16 — 라벨-칩 gap 12 / 프리즘-역량검사 쌍 gap 32 / 2열 wrap (justify-between, row-gap 16)
- 기타 역량 블록: 서브 타이틀 Bold 16 「보통 역량」/「진단불가 역량」 2개 서브섹션 (각각 안내문+대조 리스트)
- **빈 상태**: 리스트 생략, 안내문 2줄째를 「…확인되지 않습니다」로 대체 (블록 자체는 유지 — 5블록 순서 고정 노출)
- 아이콘 SVG는 루트 `icons/` 폴더 참조 (결과지 폴더에서 `../icons/`)
- 블록 단위 page-break-inside: avoid — 행이 많아 한 페이지를 넘으면 행 단위 분할 + 타이틀 바를 다음 페이지에 복제

**체크포인트 몬×역 변형 (2026-07-28 확정)**

- 블록 구성: sec-head 타이틀 바(bg 5종 동일, 여백 위 32/아래 16) → ⓘ 안내문 → (등급 조합이 복수인 블록은) **그룹 서브타이틀** → 역량 카드
- **그룹 서브타이틀 (cp-sub)**: 좌 라벨 Bold 16 #041D30 — 「점검 대상 역량」(AI 상·역검 하) / 「탐색 대상 역량」(AI 하·없음·역검 상) + 우 등급 조합 텍스트(라벨 Regular 14 #7D7D80 + 등급만 Bold 14 #041D30) / flex space-between / padding 6px 2px / border-bottom 1px #E3E3E3 / margin 16px 0 12px. **역량 카드 헤더의 등급 텍스트는 제거**(조합 표기는 서브타이틀 전담)
- **역량 카드(cp-card)**: border 1px #C6C6C6 / r8 / padding 16 20 / 카드 간 12px / 핵심역량 카드 bg rgba(255,243,219,0.3) / 헤더 = 역량명 Bold 18 + 핵심역량 태그(이름 옆)
- **코멘트 라벨**: 「AI 인터뷰 | 」 — 라벨 Regular #7D7D80, 구분 기호 ' | ' **전후 공백 1칸**
- **답변 예시**: 둥근 박스 없이 불렛 — 「바람직한 답변 | 」「부족한 답변 | 」 라벨 Regular·검정
- **역량 행 텍스트형** (검증된·기타 역량 리스트 — 회색 칩 폐기): 역량명 **Bold 14(설명과 동일 크기)** #041D30 + 핵심역량 태그 이름 옆 / 이름 열 고정폭(해설형 172px·등급 대조형 140px)으로 설명 시작점 정렬 / **행 좌우 8px 인셋**(핵심역량 연노랑 행 bg가 영역 안에 담김 — 마이너스 마진 금지) / 행 사이 구분선 1px #E3E3E3(마지막 행 제외, 2열 그리드는 홀수 개수 보정 셀렉터) / 행 간격 12px+패딩
- **범례 패널 (core-guide)**: 핵심 역량 섹션 **맨 뒤** — bg #F4F4F4 / r8 / padding 16 18 / margin 16 0 / **1단 리스트** = 카드 칩(catchip, min-width 128 중앙정렬) + 설명 Regular 14 #041D30 한 줄. ⓘ 안내문은 섹션 타이틀 바로 아래 별도 배치
- **안내문 볼드 금지**: 가이드 안내문(guide·cp-sec-desc·cls-desc) 본문은 전부 일반체 (공통 guide-note의 'Bold 14 강조' 옵션은 몬×역 미사용)

---

## 제품별 색상 테마
> 제품군 정의는 위 '제품군 표기 규칙' 참조.

- 몬스터: #6B1FCC → #9330FF (그라디언트)
- 역량검사: #08174A (Figma 추정값, 정확한 코드는 개발팀 확인 필요)
- 교차진단: 지원자 카드 외곽 **#495E76 — 프리즘과 동일** (2026-07 Figma 확정 / 구 그라디언트 표기 #004FCC → #0075FF 폐기)
- 프리즘 BP: #0A47A0 → #0F71E3 (그라디언트)
- 피드백리포트: 정의 예정 (디자인 토큰 미확정)
- 리더십 진단: #08174A → #133161 (네이비 그라디언트, 역량검사 4.0 계열) / 강조색은 패밀리 기본 #0075FF

---

## 푸터 규칙 [필수 - 모든 페이지]
- **주 사용 제품:** 공통 (로고만 제품별 상이)
- 높이: 34px / 상단 테두리: 1px solid #7D7D80 / 패딩: 0 24px
- 좌측: 제품 로고 이미지 + 제품명 텍스트 (SemiBold 12px #041D30, gap 6px)
- 중앙: 저작권 문구 (SemiBold 7px #6E777C)
- 우측: 페이지 번호 (SemiBold 12px #041D30)

### 로고 파일 및 표시 크기
| 제품 | 로고 파일 | 표시 높이 |
|------|-----------|-----------|
| 몬스터·역량검사 | ../logo/logo_monster.png | height: 10px |
| 교차진단·프리즘 BP | ../logo/logo_prism.png | height: 16px |
| 교차진단(프×역) | ../logo/logo_prism.png + ../logo/logo_monster.png (둘 다) | - |
| 교차진단(몬×역) | ../logo/logo_monster.png 단독 + 「교차진단」 텍스트 | height: 10px |

### 저작권 문구 (푸터 중앙)
> Copyright © 2026 muhayu Inc. All rights reserved.
> 본 결과의 평가 기준, 문항, 분석 내용 등 모든 지적재산권은 ㈜무하유에 귀속됩니다. 무단 복제 및 재배포를 금합니다.

---

## 마지막 페이지 안내사항 [필수]
- **주 사용 제품:** 공통 (1번째 줄 문구만 제품별 상이)
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
- 교차진단(몬×역): 본 리포트는 AI 기술을 활용하여 **AI 인터뷰** 답변 내 텍스트의 구조적 특성과 기준 충족 여부를 분석한 참고 자료입니다. 본 결과는 자동으로 합격/불합격을 결정하지 않으며, 채용과 관련된 모든 최종 판단은 사람의 검토를 통해 이루어집니다. AI 분석에는 기술적 한계가 존재할 수 있으며, 단일 결과에 의존하지 않고 종합적인 판단 자료로 활용하시기 바랍니다.

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
- **디자인 시스템을 활용한 실제 작업물(제품 목업·고객사 결과지 등)은 제품/프로젝트별 전용 폴더를 만들어 저장한다** (예: `한일시멘트/`, `리더십진단/`). 결과지 HTML·더미 데이터·빌드 스크립트 등 관련 산출물을 그 폴더에 함께 모은다.
- 단발성 샘플·실험용 목업만 `output/` 폴더에 둘 수 있다.
- 파일명: [제품명]-[지원자명]-[날짜].html
  - 예: `리더십진단/leadership-디자인목업-20260614.html`, `한일시멘트/prism-한일시멘트-지원자1-20260616.html`
- 한 파일 = 한 지원자의 결과지 / 결과지는 단일 HTML 파일로 제작 (외부 CSS/JS 파일 분리 금지)
- 로고·아이콘 에셋은 루트의 `logo/`, `icons/` 폴더를 상대 경로(`../logo/`, `../icons/`)로 참조 → 작업 폴더는 **루트 바로 아래 1단계 깊이**로 유지(상대경로 일관성)
