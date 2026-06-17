# -*- coding: utf-8 -*-
"""
한일시멘트 BP 4.2 — 고객사 실제 검사결과 반영 데이터셋 생성기 (2026-06-16)
  입력: data/raw/applicantN.html (prism 결과지 서버렌더 원문) + 기존 dataset-응시자N.json(meta/scores/benchmarks)
  처리: 실측 점수/벤치마크/메타는 기존값 유지, 그 외 전부 실제 자소서·등급·근거로 교체.
        - evaluation 등급/체계/근거ID = URL 실측, 코멘트 = 실제 자소서 근거 요약(직접 작성)
        - essay 원문(문항 제목·문장 hl) = URL 실측, evidence_sentences = URL 근거문장 마스터
        - verification·summary·hard_skills·completeness = 실제 자소서에 맞춰 재작성(더미 성격 유지)
  주의: □(U+25A1, app1 깨진 문자) → ℃ 복원, HTML 엔티티 디코딩. detected/answer_fit/ai_rate 규칙은 본문 주석 참조.
  사용: python3 data/gen_datasets.py
"""
import re, json, os, html as htmlmod
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))           # .../한일시멘트/data
RAW  = os.path.join(BASE, 'raw')
GMAP = {'high': '상', 'mid': '중', 'low': '하', 'none': '없음'}

# 직무역량 하위 요인 순서(URL 공통)
SUBS = ['실행력', '원칙준수', '책임감']
ORG  = ['리더십역량', '협상력', '갈등관리역량', '팀워크역량', '의사소통역량', '대인관계역량']


def clean(t):
    t = t.replace('□', '℃')                  # app1 깨진 문자 복원(반응 온도를 1℃ 단위로)
    t = htmlmod.unescape(t)                    # &ne;→≠, &quot;→", &nbsp; 등
    t = t.replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t).strip()


def norm(name):
    return name.replace(' ', '')


def segment(body_html):
    """문항 본문을 [연결문장 / 근거문장(hl,id)] 순서 세그먼트로 분할."""
    segs, pos = [], 0
    for m in re.finditer(r"<b no=['\"](\d+)['\"]>(.*?)</b>", body_html, re.S):
        pre = clean(BeautifulSoup(body_html[pos:m.start()], 'html.parser').get_text(' '))
        if pre:
            segs.append({'hl': False, 'gpk': False, 'text': pre})
        inner = re.sub(r"<sub>.*?</sub>", "", m.group(2))
        segs.append({'id': int(m.group(1)), 'hl': True, 'gpk': False,
                     'text': clean(BeautifulSoup(inner, 'html.parser').get_text(' '))})
        pos = m.end()
    tail = clean(BeautifulSoup(body_html[pos:], 'html.parser').get_text(' '))
    if tail:
        segs.append({'hl': False, 'gpk': False, 'text': tail})
    return segs


def parse_raw(n):
    """URL 원문에서 등급/근거/자소서 구조를 실측 추출."""
    soup = BeautifulSoup(open(os.path.join(RAW, f'applicant{n}.html'), encoding='utf-8').read(), 'html.parser')
    # 역량 테이블: {영역: {factorname: (grade, [evid...])}}, 직무역량 subs 별도
    metrics = {}
    sub_ev = {}                       # 직무역량 하위 요인 근거
    jma_sub_parent_grade = None
    for h2 in soup.find_all('h2'):
        title = h2.find(class_='metric-title')
        if not title:
            continue
        area = title.get_text(strip=True)
        tbl = h2.find_next('table', class_='metric-factor')
        fac = {}
        for tr in tbl.find_all('tr'):
            th = tr.find('th'); gtd = tr.find('td', class_='grade'); std = tr.find('td', class_='sent')
            name = norm(th.get_text(strip=True))
            grade = GMAP[[c for c in gtd.get('class') if c != 'grade'][0]] if gtd else None
            ul = std.find('ul') if std else None
            if ul:                    # 직무역량(하위 리스트)
                jma_sub_parent_grade = grade
                for li in ul.find_all('li'):
                    lab = norm(li.find('label').get_text(strip=True))
                    sub_ev[lab] = [int(s.get('no')) for s in li.find_all('span', attrs={'no': True})]
                fac[name] = (grade, [])   # 직무역량 subcat-header 등급
            else:
                ev = [int(s.get('no')) for s in std.find_all('span', attrs={'no': True})] if std else []
                fac[name] = (grade, ev)
        metrics[area] = fac
    # 자소서
    rc = soup.find(class_='right-container')
    questions = []
    for h1 in rc.find_all('h1'):
        q = clean(h1.get_text())
        title = re.sub(r'^\[문항\s*\d+\]\s*', '', q)
        body = h1.find_next(class_='body')
        segs = segment(body.decode_contents())
        questions.append({'title': title, 'segs': segs,
                          'ev_nums': sorted(s['id'] for s in segs if s['hl'])})
    return metrics, sub_ev, jma_sub_parent_grade, questions


# ─────────────────────────────────────────────────────────────────────────
# 실제 자소서 근거에 맞춰 직접 작성한 코멘트류 (더미 성격 유지, 자소서와 정합)
#  - eval: 영역별 factor 코멘트(근거문장 요약 1줄). '없음'/근거 0 항목은 자동 빈문구 → 미기재
#  - verify: 강점2/검토2 (factor·등급·pct·comment·면접질문)
#  - summary: 헤드라인(≤54자)·불릿(≤4,≤29자)
#  - completeness: 답변적합도/구체성/본인소개 1줄(점수대·문체 정합)
#  - hard: 직무 관련 하드스킬 검출/미검출(자소서 근거 기반, evidence는 실측 문장ID)
# ─────────────────────────────────────────────────────────────────────────
AUTH = {
1: {
  'eval': {
    '직무경험': '석사 과정 폴리이미드 접착강도 향상·Scale-up 공정 최적화 등 직무 직결 연구 경험이 풍부함.',
    '직무지식': '분자 구조 설계, 반응 변수 제어, 데이터 기반 분석 등 공정 화학 지식을 깊이 있게 보유함.',
    '직무동기.직무적합도': '공정 최적화 경험에서 직무 관심이 형성되었으나 장기 경력 비전 서술은 일반적 수준.',
    '실행력': '다단계 적하 방식 적용·반복 실험으로 최적 공정 조건을 도출한 실행 경험 확인.',
    '책임감': '국책 과제에서 통합 데이터 시트를 도입해 목표 대비 160% 성과까지 완수한 책임감 확인.',
    '팀워크역량': '국책 과제에서 통합 데이터 시트로 팀원 간 실험 중복을 조율한 협업 사례 1건 확인.',
    '직무동기.지원동기': '공정 최적화 경험에 기반한 직무 관심은 뚜렷하나 구체적 입사 후 계획은 보통 수준.',
    '회사동기': '단양공장 생산팀에서의 기여 방향을 제시했으나 회사 고유 강점에 대한 언급은 제한적.',
  },
  'verify': {
    'strengths': [
      {'factor': '직무경험', 'grade': '상', 'pct': '상위 12%',
       'comment': '폴리이미드 접착강도 향상·Scale-up 공정 최적화 등 직무 직결 연구 경험이 풍부함.',
       'interview_question': '석사 연구의 공정 최적화 경험 중 시멘트 생산 공정에 바로 적용할 수 있는 부분을 질문해보세요.'},
      {'factor': '직무지식', 'grade': '상', 'pct': '상위 15%',
       'comment': '분자 구조 설계·공정 변수 제어 등 공정 화학 지식을 실험으로 검증한 깊이가 확인됨.',
       'interview_question': '반응 변수 제어 지식을 시멘트 소성·분쇄 공정의 품질 변동 관리에 어떻게 활용할지 질문해보세요.'},
    ],
    'reviews': [
      {'factor': '갈등관리역량', 'grade': '없음', 'pct': '하위 7%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '팀 내 의견 충돌을 경험한 사례와 본인의 조정 방식을 질문해보세요.'},
      {'factor': '의사소통역량', 'grade': '없음', 'pct': '하위 9%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '여러 부서·교대 근무자와 정보를 공유하고 협업한 경험이 있는지 질문해보세요.'},
    ],
  },
  'summary': {
    'headline': '공정 최적화 직무 역량은 우수하나 조직 적합성은 추가 검증이 필요합니다',
    'bullets': [
      '석사 공정 최적화 연구로 직무 경험 풍부',
      '협업·소통 등 조직 역량 서술 거의 없음',
      '수치 중심 구체적 서술로 신뢰도 높음',
      '두 문항 모두 AI 작성 의심 탐지됨',
    ],
  },
  'completeness': {
    '답변적합도': '문항 의도를 대체로 반영하여 답변함',
    '구체성': '수치·실험 조건 중심의 구체적 서술',
    '본인소개': '본인 주어 중심의 명확한 서술',
  },
  'hard': [
    {'name': '공정 데이터 분석', 'status': '검출',
     'summary': '아두이노 기반 실시간 데이터 수집 시스템 구축, AI 도구로 노이즈를 개선해 측정 정확도를 높임.',
     'evidence_ids': [11, 12]},
    {'name': '공정 변수 분석·최적화(SPC)', 'status': '검출',
     'summary': '투입 순서·교반 속도·온도를 변수화하고 반복 실험으로 최적 조건을 도출, 변동성을 30% 이상 절감.',
     'evidence_ids': [9, 10]},
    {'name': 'PLC 운용', 'status': '미검출', 'summary': '', 'evidence_ids': []},
    {'name': '설비 정비·보전', 'status': '미검출', 'summary': '', 'evidence_ids': []},
  ],
},
2: {
  'eval': {
    '직무경험': '인턴십 품질 대응과 PET병 검사기 오검출 개선 등 생산 현장 경험을 보유함.',
    '직무지식': 'SPC를 활용한 공정 변동·이상 패턴 분석 등 품질관리 지식을 일부 보유함.',
    '직무동기.직무적합도': '현장 문제 해결 경험에서 직무 관심이 드러나나 직무 이해의 심화 수준은 보통.',
    '실행력': '편광필터 적용 아이디어를 제안·시범 적용해 오검출 빈도를 낮춘 실행 경험 확인.',
    '책임감': '결과 이면의 원인과 조건까지 끝까지 살피려는 태도가 품질 대응 사례에서 확인됨.',
    '직무동기.지원동기': '문제의 구조를 이해하려는 태도가 직무 관심으로 이어지나 입사 후 계획은 일반적.',
    '회사동기': '폐플라스틱 순환자원 대체 등 산업 흐름과 전공을 연결했으나 회사 동기는 다소 포괄적.',
  },
  'verify': {
    'strengths': [
      {'factor': '직무경험', 'grade': '중', 'pct': '상위 38%',
       'comment': '인턴십 품질 대응·검사기 오검출 개선 등 생산 현장 문제 해결 경험을 보유함.',
       'interview_question': '검사기 오검출 개선 과제에서 본인이 직접 주도한 부분과 한계를 구체적으로 질문해보세요.'},
      {'factor': '직무동기', 'grade': '중', 'pct': '상위 41%',
       'comment': '제약 조건 속에서 현실적 최적안을 찾는 엔지니어상을 직무 동기로 제시함.',
       'interview_question': '이론적 최적값과 현장 제약이 충돌한 경험에서 어떤 기준으로 절충했는지 질문해보세요.'},
    ],
    'reviews': [
      {'factor': '리더십역량', 'grade': '없음', 'pct': '하위 5%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '팀이나 과제를 주도적으로 이끈 경험이 있는지 질문해보세요.'},
      {'factor': '갈등관리역량', 'grade': '없음', 'pct': '하위 6%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '이해관계가 다른 동료와 의견 차이를 조율한 경험을 질문해보세요.'},
    ],
  },
  'summary': {
    'headline': '현장 문제 해결 경험은 있으나 조직 역량 서술이 전무합니다',
    'bullets': [
      '인턴십 품질 대응·검사 개선 경험 보유',
      '협업·리더십 등 조직 역량 서술 없음',
      '제약 속 현실적 대안 모색 태도 강점',
      '두 문항 모두 AI 작성 의심 탐지됨',
    ],
  },
  'completeness': {
    '답변적합도': '문항 의도를 대체로 반영하여 답변함',
    '구체성': '경험 서술에 일부 추상적 표현 혼재',
    '본인소개': '본인 중심 서술이 대체로 유지됨',
  },
  'hard': [
    {'name': '통계적 공정관리(SPC)', 'status': '검출',
     'summary': 'SPC 지식으로 공정 변동성과 이상 패턴을 분석해 사전 예방 관점의 개선안을 검토함.',
     'evidence_ids': [5]},
    {'name': '품질 검사·불량 대응', 'status': '검출',
     'summary': '검사기 오검출 원인을 분석하고 편광필터 적용으로 오검출 빈도를 일부 줄인 경험 확인.',
     'evidence_ids': [4, 6, 7]},
    {'name': 'PLC 운용', 'status': '미검출', 'summary': '', 'evidence_ids': []},
    {'name': '설비 자동화', 'status': '미검출', 'summary': '', 'evidence_ids': []},
  ],
},
3: {
  'eval': {
    '직무경험': '종합 설계 박막 분석 프로젝트와 배관 제작 공장 검사 근무 등 현장 경험을 보유함.',
    '직무지식': '공정 조건과 데이터의 관계를 해석하는 분석적 접근과 품질 검사 지식을 갖춤.',
    '직무동기.직무적합도': '원인 파악·개선 지향 태도에서 직무 관심이 드러나나 직무 이해 깊이는 보통.',
    '실행력': '도면 대조 검사 등 맡은 작업을 정확히 수행한 실행 경험 확인.',
    '원칙준수': '도면 기준 적합 여부 확인 등 품질 기준을 준수하려는 태도가 확인됨.',
    '책임감': '작은 차이도 품질에 영향을 준다는 인식 아래 검사 책임을 수행한 경험 확인.',
    '리더십역량': '동아리 총무·감독을 맡아 운영진과 함께 팀 운영을 이끈 경험이 확인됨.',
    '갈등관리역량': '선수 선발·연습 방식 갈등을 객관적 기록 기반 평가 기준 도입으로 조정한 경험 확인.',
    '팀워크역량': '팀원들과 함께 공정 조건이 결과에 미치는 영향을 확인해 나간 협업 경험 확인.',
    '의사소통역량': '구성원의 이야기를 먼저 듣고 방향을 맞추는 소통 태도가 운영 경험에서 드러남.',
    '대인관계역량': '후배·운영진에게 조언과 의견을 전하는 선임 역할 경험이 확인됨.',
    '직무동기.지원동기': '공정 안정화·품질 향상에 기여하려는 직무 관심은 뚜렷하나 입사 후 계획은 보통.',
    '회사동기': '더 큰 현장에 도전하려는 동기는 있으나 한일시멘트 고유 강점에 대한 언급이 부족함.',
  },
  'verify': {
    'strengths': [
      {'factor': '리더십역량', 'grade': '중', 'pct': '상위 22%',
       'comment': '동아리 총무·감독으로 운영진과 함께 팀을 이끌고 운영 방식을 개선한 경험 보유.',
       'interview_question': '팀 운영에서 기록 기반 평가 기준을 도입한 과정과 구성원 설득 방법을 질문해보세요.'},
      {'factor': '갈등관리역량', 'grade': '중', 'pct': '상위 27%',
       'comment': '선수 선발·연습 방식 갈등을 객관적 기록 기반 기준으로 조정한 경험이 확인됨.',
       'interview_question': '혼자 판단의 한계를 느낀 뒤 합의를 끌어낸 구체적 사례를 질문해보세요.'},
    ],
    'reviews': [
      {'factor': '회사동기', 'grade': '하', 'pct': '하위 32%',
       'comment': '더 큰 현장 도전 의지는 있으나 한일시멘트를 선택한 구체적 이유 서술이 부족함.',
       'interview_question': '여러 생산 기업 중 한일시멘트에 지원한 구체적 이유를 질문해보세요.'},
      {'factor': '협상력', 'grade': '없음', 'pct': '하위 9%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '이해관계가 다른 상대와 조건을 협의해 합의점을 찾은 경험을 질문해보세요.'},
    ],
  },
  'summary': {
    'headline': '조직·협업 역량은 우수하나 구체적 직무 성과 서술이 부족합니다',
    'bullets': [
      '동아리 운영 경험으로 조직 역량 우수',
      '소통·갈등관리 등 협업 강점 뚜렷',
      '직무 경험의 정량적 근거는 다소 부족',
      '회사 지원 동기 서술이 구체적이지 않음',
    ],
  },
  'completeness': {
    '답변적합도': '문항 의도를 대체로 반영하여 답변함',
    '구체성': '서술이 다소 일반적이고 수치 근거 부족',
    '본인소개': '본인 경험 중심으로 서술됨',
  },
  'hard': [
    {'name': '재료·데이터 분석', 'status': '검출',
     'summary': '박막 특성 분석에서 공정 조건 변화와 스펙트럼 패턴의 관계를 데이터로 비교·해석함.',
     'evidence_ids': [9, 10, 11]},
    {'name': '품질 검사', 'status': '검출',
     'summary': '배관이 도면대로 제작되었는지 확인하는 검사 업무를 수행하며 품질 기준을 적용함.',
     'evidence_ids': [14, 15]},
    {'name': '통계적 공정관리(SPC)', 'status': '미검출', 'summary': '', 'evidence_ids': []},
    {'name': 'PLC 운용', 'status': '미검출', 'summary': '', 'evidence_ids': []},
  ],
},
4: {
  'eval': {
    '직무경험': '학부연구생·생산기술연구원 인턴, 열분해 공정 설계 등 공학 직무 경험이 풍부함.',
    '직무지식': '경제성 평가, BET 분석, 수소 재사용 PSA 공정 등 공정·분석 지식을 폭넓게 보유함.',
    '직무동기.직무적합도': '공정에 투입되어 안정화에 기여하려는 직무 관심이 드러나나 표현은 다소 거침.',
    '실행력': '열분해 공정도 작성, PSA 공정으로 수소 사용량 30% 절감 등 설계를 끝까지 구현함.',
    '책임감': '특허를 참고해 단양공장 시멘트를 미리 학습하는 등 준비에 책임감을 보임.',
    '갈등관리역량': '카메라 검수 공정의 병목을 타 부서와 소통해 해결한 경험 1건 확인.',
    '팀워크역량': '경진대회에서 학부연구생들에게 협력을 요청해 함께 프로젝트를 수행한 경험 확인.',
    '의사소통역량': '병목 해결을 위해 타 부서와 소통한 사례에서 의사소통 경험이 일부 확인됨.',
    '대인관계역량': '동료의 일까지 살피는 사람을 에이스로 본다는 인식은 있으나 본인 사례는 제한적.',
    '직무동기.지원동기': '공정 안정화 기여 의지는 뚜렷하나 입사 후 계획의 구체성은 보통.',
    '회사동기': '단양공장 시멘트를 학습한 노력은 있으나 회사 선택 이유 서술은 부족함.',
  },
  'verify': {
    'strengths': [
      {'factor': '직무경험', 'grade': '상', 'pct': '상위 9%',
       'comment': '열분해 공정 설계·경제성 평가 등 정량적 성과를 갖춘 공학 직무 경험이 풍부함.',
       'interview_question': '열분해 공정 설계에서 사용한 경제성·수소 절감 계산의 가정과 검증 방법을 질문해보세요.'},
      {'factor': '직무지식', 'grade': '상', 'pct': '상위 11%',
       'comment': 'BET 분석·PSA 공정·경제성 평가 등 공정 설계 전반의 지식을 폭넓게 보유함.',
       'interview_question': 'BET 분석으로 흡착 효율을 정량화한 경험을 시멘트 품질 분석에 어떻게 적용할지 질문해보세요.'},
    ],
    'reviews': [
      {'factor': '회사동기', 'grade': '하', 'pct': '하위 28%',
       'comment': '단양공장 학습 노력은 있으나 한일시멘트를 선택한 구체적 이유 서술이 부족함.',
       'interview_question': '여러 화학·소재 기업 중 한일시멘트 생산직에 지원한 이유를 질문해보세요.'},
      {'factor': '협상력', 'grade': '없음', 'pct': '하위 10%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '이해관계가 다른 상대와 조건을 협의해 합의에 이른 경험을 질문해보세요.'},
    ],
  },
  'summary': {
    'headline': '정량적 직무 역량은 매우 우수하나 본인 중심 서술이 부족합니다',
    'bullets': [
      '열분해 공정 설계 등 직무 경험 풍부',
      '경제성·수치 근거로 구체성 매우 높음',
      '문장 구성·본인 주어 서술은 다소 약함',
      'AI 작성 의심은 탐지되지 않음',
    ],
  },
  'completeness': {
    '답변적합도': '문항 의도에 부합하게 답변함',
    '구체성': '수치·계산 근거가 풍부해 밀도 높음',
    '본인소개': '외부 상황 서술이 일부 혼재함',
  },
  'hard': [
    {'name': '공정 설계', 'status': '검출',
     'summary': '열분해 공정을 설계하고 공정도를 작성, PSA 공정으로 수소 사용량을 30% 수준으로 절감함.',
     'evidence_ids': [8, 9]},
    {'name': '화학 분석(BET)', 'status': '검출',
     'summary': '분쇄·활성화·소성을 거쳐 흡착제를 제조하고 BET 분석으로 흡착 효율을 정량화함.',
     'evidence_ids': [6]},
    {'name': 'PLC 운용', 'status': '미검출', 'summary': '', 'evidence_ids': []},
    {'name': '품질관리(QC) 실무', 'status': '미검출', 'summary': '', 'evidence_ids': []},
  ],
},
5: {
  'eval': {
    '직무경험': '주조 인턴에서 전기전도도 측정·편석 분석·밀링 최적화 등 직무 직결 경험이 풍부함.',
    '직무지식': '공정 메커니즘 이해 기반의 데이터 해석과 LOT 비교 분석 등 분석 지식을 보유함.',
    '직무동기.직무적합도': '현장 데이터로 이상 신호를 조기 차단하려는 직무 관심이 명확함.',
    '실행력': '샘플 두께 우선 측정 방식으로 전환해 측정 리드타임을 30% 단축한 실행력 확인.',
    '책임감': '미달 LOT를 신속히 보고해 공정 리스크를 조기에 차단한 책임감이 확인됨.',
    '팀워크역량': '임직원·협력사 담당자의 협조를 이끌어 성과를 낸 협업 경험이 확인됨.',
    '의사소통역량': '사수에게 작업 의미를 확인하고 관계자와 긴밀히 소통한 경험이 확인됨.',
    '대인관계역량': '인턴 초반 소극적이던 시기를 조언 요청으로 극복한 관계 형성 경험 확인.',
    '직무동기.지원동기': '이상 신호 조기 차단·관계자 조율이라는 직무 본질을 명확히 인식함.',
    '회사동기': '생산엔지니어로서 납기·품질을 함께 지키려는 동기는 있으나 회사 고유 강점 언급은 보통.',
  },
  'verify': {
    'strengths': [
      {'factor': '직무경험', 'grade': '상', 'pct': '상위 8%',
       'comment': '주조 인턴에서 전기전도도 측정·편석 분석·밀링 최적화 등 직무 직결 경험이 풍부함.',
       'interview_question': '밀링 방식 전환으로 리드타임을 30% 단축한 과정과 데이터 근거를 구체적으로 질문해보세요.'},
      {'factor': '직무지식', 'grade': '상', 'pct': '상위 13%',
       'comment': '공정 메커니즘 이해를 바탕으로 LOT별 데이터를 비교해 편차 패턴을 도출하는 지식을 갖춤.',
       'interview_question': '편석 분포와 전도도 편차의 관계를 시멘트 품질 변동 분석에 어떻게 적용할지 질문해보세요.'},
    ],
    'reviews': [
      {'factor': '리더십역량', 'grade': '없음', 'pct': '하위 8%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '팀이나 과제를 앞장서서 이끈 경험이 있는지 질문해보세요.'},
      {'factor': '협상력', 'grade': '없음', 'pct': '하위 10%',
       'comment': '해당 역량을 확인할 수 없음',
       'interview_question': '협력사·타 부서와 이해관계가 다른 사안을 협의해 합의한 경험을 질문해보세요.'},
    ],
  },
  'summary': {
    'headline': '직무 역량과 자기 서술이 모두 우수하나 조직 역량은 부분적입니다',
    'bullets': [
      '주조 인턴 공정 분석 경험으로 직무 우수',
      '먼저 행동하는 주도성 일관되게 드러남',
      '협력사 소통 등 협업 경험 일부 확인',
      '두 문항 모두 AI 작성 의심 탐지됨',
    ],
  },
  'completeness': {
    '답변적합도': '문항 의도에 부합하게 답변함',
    '구체성': '수치·공정 맥락 중심의 구체적 서술',
    '본인소개': '본인 주어 중심의 명확한 서술',
  },
  'hard': [
    {'name': '공정 데이터 분석', 'status': '검출',
     'summary': '전기전도도 측정·LOT 비교로 샘플 두께와 전도도 편차의 패턴을 도출해 분석에 활용함.',
     'evidence_ids': [13, 14]},
    {'name': '품질 검사·측정', 'status': '검출',
     'summary': '설비별 샘플을 수집해 밀링·전기전도도 측정을 수행하고 미달 LOT를 선별·보고함.',
     'evidence_ids': [9, 15]},
    {'name': '공정 설계', 'status': '미검출', 'summary': '', 'evidence_ids': []},
    {'name': 'PLC 운용', 'status': '미검출', 'summary': '', 'evidence_ids': []},
  ],
},
}


def build_eval(area, fac_grades, sub_ev, jma_parent, auth_eval):
    """영역별 evaluation.항목 리스트 생성."""
    def summ(key, grade, ev):
        if grade == '없음' or not ev:
            return '', []
        return auth_eval.get(key, ''), ev

    items = []
    if area == '직무적합도':
        for name in ['직무경험', '직무지식', '직무동기']:
            g, ev = fac_grades[name]
            s, e = summ(name if name != '직무동기' else '직무동기.직무적합도', g, ev)
            items.append({'name': name, 'level': 'factor', 'grade': g, 'summary': s, 'evidence_ids': e})
        items.append({'name': '직무역량', 'level': 'subcat-header', 'grade': jma_parent})
        for sub in SUBS:
            ev = sub_ev.get(sub, [])
            g = jma_parent if ev else '없음'        # 하위 등급: 근거 있으면 모분류 등급 상속, 없으면 판단불가
            s, e = summ(sub, g, ev)
            items.append({'name': sub, 'level': 'sub', 'grade': g, 'summary': s, 'evidence_ids': e})
    elif area == '조직적합도':
        for name in ORG:
            g, ev = fac_grades[name]
            s, e = summ(name, g, ev)
            items.append({'name': name, 'level': 'sub', 'grade': g, 'summary': s, 'evidence_ids': e})
    elif area == '지원동기':
        for name in ['직무동기', '회사동기']:
            g, ev = fac_grades[name]
            s, e = summ(name if name != '직무동기' else '직무동기.지원동기', g, ev)
            items.append({'name': name, 'level': 'factor', 'grade': g, 'summary': s, 'evidence_ids': e})
    return items


def derive_detected(questions, fac_global):
    """문항별 검출 역량(metrics 등급칩) + 검출 역량분자(factors 태그) 파생.
       fac_global: {name: (grade, evidence_set)} — 주요 factor + 하위 요인."""
    MAIN = ['직무경험', '직무지식', '직무동기', '회사동기'] + ORG
    out = []
    for q in questions:
        qn = set(q['ev_nums'])
        # metrics: 주요 factor 중 해당 문항에 근거가 있는 것, 근거수 desc, 상위 3
        scored = []
        for name in MAIN:
            if name not in fac_global:
                continue
            g, evset = fac_global[name]
            if g == '없음':
                continue
            c = len(qn & evset)
            if c:
                scored.append((c, name, g))
        scored.sort(key=lambda x: -x[0])
        metrics = [{'name': nm, 'grade': g} for _, nm, g in scored[:3]]
        # factors: 직무역량 하위 요인 중 해당 문항 근거 보유 → 태그
        tags = [s for s in SUBS if s in fac_global and (qn & fac_global[s][1])]
        if len(tags) < 2:                      # 부족하면 주요 factor명으로 보충
            for _, nm, _ in scored:
                if nm not in tags:
                    tags.append(nm)
                if len(tags) >= 3:
                    break
        out.append((metrics, tags[:4]))
    return out


def cohort_benchmarks():
    """평균은 임의로 상정하지 않고 '전형 전체(=이 5명)' 실측 평균을 계산해 사용(2026-06-16 보완).
       SDS 비교집단 정의: 공채형 = 해당 전형 전체. 본 샘플 전형 = 응시자 5명.
       반환: avg{total+6메트릭}, radar_avg[6] (레이더 축 순서)."""
    keys = ['직무적합도', '조직적합도', '지원동기', '답변적합도', '구체성', '본인소개']
    totals, per = [], {k: [] for k in keys}
    for n in range(1, 6):
        sc = json.load(open(os.path.join(BASE, f'dataset-응시자{n}.json'), encoding='utf-8'))['scores']
        totals.append(sc['total'])
        for k in keys:
            per[k].append(sc[k])
    avg = {'total': round(sum(totals) / len(totals), 2)}
    for k in keys:
        avg[k] = round(sum(per[k]) / len(per[k]), 2)
    radar = [avg[k] for k in keys]            # 레이더 축: 직무/조직/지원동기/답변완성도/구체성/자기소개
    return avg, radar


def main():
    coh_avg, coh_radar = cohort_benchmarks()
    print(f"[평균(전형 5명 실측)] total={coh_avg['total']} " +
          ' '.join(f"{k}={coh_avg[k]}" for k in ['직무적합도', '조직적합도', '지원동기', '답변적합도', '구체성', '본인소개']))
    for n in range(1, 6):
        metrics, sub_ev, jma_parent, questions = parse_raw(n)
        auth = AUTH[n]
        old = json.load(open(os.path.join(BASE, f'dataset-응시자{n}.json'), encoding='utf-8'))

        # evaluation
        evaluation = {
            '직무적합도': {'항목': build_eval('직무적합도', metrics['직무적합도'], sub_ev, jma_parent, auth['eval'])},
            '조직적합도': {'항목': build_eval('조직적합도', metrics['조직적합도'], sub_ev, jma_parent, auth['eval'])},
            '지원동기':   {'항목': build_eval('지원동기',   metrics['지원동기'],   sub_ev, jma_parent, auth['eval'])},
        }

        # evidence_sentences 마스터 (모든 근거문장 id→원문)
        evidence_sentences = {}
        for q in questions:
            for s in q['segs']:
                if s['hl']:
                    evidence_sentences[str(s['id'])] = s['text']

        # 전역 factor 근거맵 (detected 파생용)
        fac_global = {}
        for area in ['직무적합도', '조직적합도', '지원동기']:
            for name, (g, ev) in metrics[area].items():
                if name == '직무역량':
                    continue
                fac_global.setdefault(name, (g, set()))
                fac_global[name] = (g, fac_global[name][1] | set(ev))
        for sub, ev in sub_ev.items():
            g = jma_parent if ev else '없음'
            fac_global[sub] = (g, set(ev))
        detected = derive_detected(questions, fac_global)

        # essay (기존 answer_fit·ai_rate 유지 — GPK 정합 더미)
        essay_q = []
        for i, q in enumerate(questions):
            sents = []
            for s in q['segs']:
                d = {'text': s['text'], 'hl': s['hl'], 'gpk': False}
                if 'id' in s:
                    d['id'] = s['id']
                sents.append(d)
            oldq = old['essay']['questions'][i]
            m, t = detected[i]
            essay_q.append({
                'no': i + 1,
                'title': q['title'],
                'answer_fit': oldq['answer_fit'],
                'ai_rate': oldq['ai_rate'],
                'sentences': sents,
                'detected': {'metrics': m, 'factors': t},
            })

        bm = dict(old['benchmarks'])
        bm['avg'] = coh_avg                    # 보완(2026-06-16): 평균은 전형 5명 실측 평균을 계산 사용
        bm['radar_avg'] = coh_radar

        d = {
            '_comment': f"한일시멘트 BP 4.2 — 응시자{n} (고객사 실제 검사결과 반영, 2026-06-16). "
                        f"점수/meta는 통합결과표·prism URL 실측, evaluation 등급·근거ID·자소서 원문·근거문장은 prism 결과지 URL 실측. "
                        f"benchmarks.avg·radar_avg는 전형 5명 실측 평균 계산값(cohort_benchmarks). "
                        f"하드스킬은 [JD→추출프롬프트→자소서 검출판단] 워크플로우 출력처(현재 INTERIM 수작업, JD·프롬프트 수령 시 교체). "
                        f"summary(헤드라인·불릿)는 PAC(자소서 요약 결과) 연동 슬롯(현재 INTERIM 수작업, PAC 수령 시 교체). "
                        f"evaluation.summary·verification·면접질문은 처리방안 후속 — 현재 실제 자소서 기반 생성 코멘트(BP 엔진 산출 아님). "
                        f"□(U+25A1)→℃ 복원, HTML 엔티티 디코딩.",
            '_dummy_fields': [
                'benchmarks.top10·cut·percentile (5명 소표본 derived/가정 — 정책 확인 대기)',
                'meta.pass_badge (3배수 가정)',
                'summary.headline·bullets (INTERIM 수작업 — PAC 자소서 요약 결과로 교체 예정)',
                'hard_skills.항목 (INTERIM 수작업 — JD 추출 하드스킬 + 자소서 검출판단 워크플로우로 교체 예정)',
                'evaluation.항목[].summary (근거문장 요약 — 실제 자소서 기반 생성, 처리방안 후속)',
                'evaluation 직무역량 하위 등급 (근거 있으면 모분류 상속, 없으면 없음 — 파생)',
                'completeness.*.short_text (생성, 처리방안 후속)',
                'verification.* (강점/검토 선별·pct·코멘트·면접질문 — 생성, 처리방안 후속)',
                'essay.questions[].answer_fit (문항별 분산 샘플)·ai_rate (GPT 탐지여부 정합 샘플)',
                'essay.questions[].detected (근거-문항 매핑 파생)',
            ],
            'meta': old['meta'],
            'scores': old['scores'],
            'benchmarks': bm,
            'summary': auth['summary'],
            'evaluation': evaluation,
            'completeness': {k: {'short_text': v} for k, v in auth['completeness'].items()},
            'verification': auth['verify'],
            'essay': {'questions': essay_q},
            'hard_skills': {'항목': auth['hard']},
            'evidence_sentences': evidence_sentences,
        }

        # 길이 가드(빌드와 동일 기준 선검사)
        assert len(d['summary']['headline']) <= 54, f"app{n} headline {len(d['summary']['headline'])}자"
        for b in d['summary']['bullets']:
            assert len(b) <= 29, f"app{n} bullet {len(b)}자: {b}"
        # 무결성: evidence_ids ⊆ evidence_sentences
        ids = set(int(k) for k in evidence_sentences)
        ref = set()
        for area in evaluation.values():
            for it in area['항목']:
                ref |= set(it.get('evidence_ids', []))
        for h in d['hard_skills']['항목']:
            ref |= set(h['evidence_ids'])
        miss = ref - ids
        assert not miss, f"app{n} evidence 누락 {miss}"

        json.dump(d, open(os.path.join(BASE, f'dataset-응시자{n}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        nq = len(essay_q); nev = len(evidence_sentences)
        print(f"app{n}: 저장 OK  근거문장 {nev}개  문항 {nq}  detected {[len(m) for m,_ in detected]}  ref⊆ids ✓")


if __name__ == '__main__':
    main()
