# -*- coding: utf-8 -*-
"""한일시멘트 BP 4.1 정본 — 5명 데이터셋 생성기 (2026-06-16)
  입력: /tmp/parsed41.json(PDF 추출) + 기존 dataset(meta) + 본 파일 AUTH41(판단부)
  처리: 점수·등급(8분자)·근거·자소서는 4.1 PDF 실측, benchmarks는 5명 4.1 재계산.
        PAC→summary 불릿, JD 하드스킬 7개 응시자별 검출, 코멘트(eval/verify/completeness)는 4.1 근거 기반 작성.
  사용: python3 data/parse_pdf41.py && python3 data/gen_datasets_v41.py && python3 build_reports.py
"""
import re, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open('/tmp/parsed41.json', encoding='utf-8'))
SUBS = ['전략적사고', '실행력', '문제해결력', '발전가능성', '주도성', '원칙준수', '성실성', '책임감']
BP_OVERRIDE = {}  # app1은 PDF 실측 68.07(=가중합 절사)이 정본. 65.55는 시스템 산출오류로 확인·환원(2026-06-17)
ORG = ['리더십역량', '협상력', '갈등관리역량', '팀워크역량', '의사소통역량', '대인관계역량']

# ── JD 추출 하드스킬 7종 (공통) ──
JD_HARD = ['시멘트 생산 계획·실적 관리', '공정 설계·개선', '공정 안정화·품질관리',
           '화공·고분자·신소재 전공 지식', '생산·제조 실무 경험', '동종업계 경력', '직무 관련 자격증']

# ── 응시자별 판단부 (PAC=사용자 제공 그대로 / 나머지=4.1 근거 기반 작성) ──
AUTH = {
1: {
 'headline': '공정 최적화 직무 역량은 우수하나 조직 적합성은 보통 수준입니다',
 'pac': ['폴리이미드 접착강도 30배 향상 연구 경험', '공정 변수 분석으로 변동성 30% 이상 감소', '아두이노·AI 도구로 데이터 기반 문제 해결', '통합 데이터 관리로 목표 대비 160% 성과'],
 'eval': {
   '직무경험':'폴리이미드 접착강도 향상·Scale-up 공정 최적화·국책과제 등 직무 직결 연구 경험이 풍부함.',
   '직무지식':'분자 구조 설계·공정 변수 제어·데이터 기반 분석 등 공정 화학 지식을 깊이 보유함.',
   '직무동기jma':'공정 최적화 경험에서 직무 관심이 뚜렷하나 입사 후 계획 서술은 일반적 수준.',
   '전략적사고':'투입 순서·교반 변수화 등 단계적 접근은 있으나 공정 전체 관점은 제한적.',
   '실행력':'반복 실험·데이터 수집 시스템 구축 등 계획을 실행으로 옮긴 경험 확인.',
   '문제해결력':'품질 불균일·센서 노이즈 문제를 변수 제어·AI 도구로 해결한 경험 확인.',
   '발전가능성':'데이터 수집 시스템 구축·재현성 확보 등 자기주도 학습·개선 경험 확인.',
   '주도성':'통합 데이터 관리 시스템 도입을 먼저 제안·실행한 주도성 확인.',
   '성실성':'6개월간 반응 온도를 정밀 조절하며 반복 실험을 지속한 성실성이 확인됨.',
   '팀워크역량':'국책 과제에서 통합 데이터 시트로 팀원 간 실험 중복을 조율한 협업 경험 확인.',
   '의사소통역량':'통합 데이터 시트 공유로 팀 내 정보 전달을 시도한 경험이 확인됨.',
   '직무동기mot':'공정 최적화 경험 기반 직무 관심은 뚜렷하나 구체적 입사 후 계획은 보통.',
   '회사동기':'한일시멘트 단양공장 생산팀 기여 방향과 공정 설계 개선 비전을 제시함.'},
 'verify': {'strengths':[('직무경험','상위 18%','폴리이미드 접착강도 향상·Scale-up 공정 최적화 등 직무 직결 연구 경험이 풍부함.','석사 공정 최적화 경험 중 시멘트 생산 공정에 바로 적용할 부분을 질문해보세요.'),
                         ('직무지식','상위 22%','분자 구조 설계·공정 변수 제어 지식을 실험으로 검증한 깊이가 확인됨.','반응 변수 제어 지식을 시멘트 소성·분쇄 품질 변동 관리에 어떻게 쓸지 질문해보세요.')],
            'reviews':[('리더십역량','하위 12%','해당 역량을 확인할 수 없음','팀이나 과제를 앞장서 이끈 경험이 있는지 질문해보세요.'),
                       ('협상력','하위 9%','해당 역량을 확인할 수 없음','이해관계가 다른 상대와 합의점을 찾은 경험을 질문해보세요.')]},
 'completeness': {'답변적합도':'문항 의도를 대체로 반영하여 답변함','구체성':'수치·실험 조건 중심의 구체적 서술','본인소개':'본인 주어 중심의 명확한 서술'},
 'hard': {'공정 설계·개선':[3,10,11,16],'공정 안정화·품질관리':[7,8,13],'화공·고분자·신소재 전공 지식':[1,2,6,9]},
 'hard_summ': {'공정 설계·개선':'투입 순서·교반 변수화와 다단계 적하 방식으로 공정 변동성을 30% 이상 줄인 공정 개선 경험 확인.',
               '공정 안정화·품질관리':'공정 변수를 분석해 변동성을 표준화하고 측정 정확도·재현성을 확보한 안정화·품질관리 경험 확인.',
               '화공·고분자·신소재 전공 지식':'폴리이미드 분자 구조 설계 등 석사 과정의 고분자·화공 전공 지식을 공정에 적용함.'},
},
2: {
 'headline': '문제의 원인을 분석하는 태도는 강점이나 조직 역량 서술이 전무합니다',
 'pac': ['결과보다 과정·근본 원인을 분석하는 태도', '인턴십 품질 이슈 대응으로 현장 흐름 이해', '현장 제약 속 현실적 최선안 모색 능력', '외부 조건의 복합 영향 분석·대응 제안'],
 'eval': {
   '직무경험':'인턴십 품질 이슈 대응·PET병 검사기 오검출 개선 등 생산 현장 경험을 보유함.',
   '직무지식':'SPC를 활용한 공정 변동·이상 패턴 분석 등 품질관리 지식을 일부 보유함.',
   '직무동기jma':'현장 문제 해결 경험에서 직무 관심이 드러나나 직무 이해의 심화는 보통.',
   '전략적사고':'현실적 제약 속에서 적용 가능한 대안으로 접근을 전환한 사고가 확인됨.',
   '실행력':'편광필터 적용 아이디어를 제한적으로 적용해 오검출을 줄인 실행 경험 확인.',
   '문제해결력':'오검출 원인을 복합적으로 분석하고 개선안을 도출한 문제 해결 경험 확인.',
   '발전가능성':'SPC 지식과 소재 이해를 결합해 공정 변동을 보겠다는 발전 의지 확인.',
   '주도성':'현장 진행 방식과 달리 결과 이전 조건을 먼저 정리하려는 주도성 일부 확인.',
   '성실성':'결과를 그대로 넘기지 않고 한 번 더 상황을 살피는 성실한 태도가 확인됨.',
   '책임감':'품질 이슈 대응에서 원인 구조까지 이해하려는 책임감이 확인됨.',
   '직무동기mot':'제약 속 현실적 최적안을 찾는 엔지니어상을 직무 동기로 제시함.',
   '회사동기':'폐플라스틱 순환자원 대체 등 산업 흐름과 전공을 연결했으나 회사 동기는 포괄적.'},
 'verify': {'strengths':[('직무경험','상위 41%','인턴십 품질 대응·검사기 오검출 개선 등 생산 현장 문제 해결 경험을 보유함.','검사기 오검출 개선 과제에서 본인이 직접 주도한 부분과 한계를 질문해보세요.'),
                         ('문제해결력','상위 38%','오검출 원인을 설비·환경 복합 요인으로 분석하고 개선안을 도출한 경험이 확인됨.','이론적 최적안이 적용 어려웠을 때 대안을 찾은 과정을 질문해보세요.')],
            'reviews':[('리더십역량','하위 5%','해당 역량을 확인할 수 없음','팀이나 과제를 주도적으로 이끈 경험이 있는지 질문해보세요.'),
                       ('갈등관리역량','하위 6%','해당 역량을 확인할 수 없음','이해관계가 다른 동료와 의견 차이를 조율한 경험을 질문해보세요.')]},
 'completeness': {'답변적합도':'문항 의도를 대체로 반영하여 답변함','구체성':'경험 서술에 일부 추상적 표현 혼재','본인소개':'본인 중심 서술이 대체로 유지됨'},
 'hard': {'공정 안정화·품질관리':[3,7,8,10],'화공·고분자·신소재 전공 지식':[12],'생산·제조 실무 경험':[6,7,9]},
 'hard_summ': {'공정 안정화·품질관리':'SPC로 공정 변동·이상 패턴을 분석하고 검사기 오검출 빈도를 줄인 품질 개선 경험 확인.',
               '화공·고분자·신소재 전공 지식':'고분자공학 전공으로 습득한 플라스틱 소재 이해를 공정에 연결함.',
               '생산·제조 실무 경험':'PET병 생산 공정 인턴십에서 품질 이슈 대응·검사 개선을 수행한 현장 경험 확인.'},
},
3: {
 'headline': '조직·협업 역량은 우수하나 구체적 직무 성과 서술이 부족합니다',
 'pac': ['의견 조율·소통으로 협력·운영 경험 보유', '객관적 기록 활용해 팀 운영 방식 개선', '후배·운영진에게 조언하는 선임 역할 수행', '실험 데이터로 변수·공정 조건 관계 분석', '원인을 먼저 파악해 개선 방향 모색'],
 'eval': {
   '직무경험':'종합 설계 박막 분석 프로젝트와 배관 제작 공장 검사 근무 등 현장 경험을 보유함.',
   '직무지식':'공정 조건과 데이터의 관계를 해석하는 분석적 접근과 품질 검사 지식을 갖춤.',
   '직무동기jma':'원인 파악·개선 지향 태도에서 직무 관심이 드러나나 직무 이해 깊이는 보통.',
   '전략적사고':'변수 변화에 따른 패턴을 비교하며 원인을 단계적으로 좁혀간 사고가 확인됨.',
   '실행력':'배관 도면 대조 검사 등 맡은 작업을 정확히 수행한 실행 경험 확인.',
   '문제해결력':'분석 스펙트럼 차이의 원인을 데이터 반복 비교로 규명한 문제 해결 경험 확인.',
   '발전가능성':'결과를 원인까지 파고들어 개선 방향을 찾으려는 발전 지향 태도 확인.',
   '주도성':'문제의 원인을 먼저 파악하려 나서는 주도적 태도가 확인됨.',
   '성실성':'배관 제작 현장에서 작은 차이도 품질에 영향을 준다는 점을 체득한 성실성 확인.',
   '리더십역량':'동아리 총무·감독을 맡아 운영진과 함께 팀 운영을 이끈 경험이 확인됨.',
   '갈등관리역량':'선수 선발·연습 방식 갈등을 객관적 기록 기반 평가 기준 도입으로 조정한 경험 확인.',
   '팀워크역량':'팀원들과 함께 공정 조건이 결과에 미치는 영향을 확인해 나간 협업 경험 확인.',
   '의사소통역량':'구성원의 이야기를 먼저 듣고 방향을 맞추는 소통 태도가 운영 경험에서 드러남.',
   '대인관계역량':'후배·운영진에게 조언과 의견을 전하는 선임 역할 경험이 확인됨.',
   '직무동기mot':'공정 안정화·품질 향상에 기여하려는 직무 관심은 뚜렷하나 입사 후 계획은 보통.',
   '회사동기':'더 큰 현장에 도전하려는 동기는 있으나 한일시멘트 고유 강점 언급이 부족함.'},
 'verify': {'strengths':[('리더십역량','상위 22%','동아리 총무·감독으로 운영진과 함께 팀을 이끌고 운영 방식을 개선한 경험 보유.','기록 기반 평가 기준을 도입한 과정과 구성원 설득 방법을 질문해보세요.'),
                         ('갈등관리역량','상위 27%','선수 선발·연습 방식 갈등을 객관적 기록 기반 기준으로 조정한 경험이 확인됨.','혼자 판단의 한계를 느낀 뒤 합의를 끌어낸 구체적 사례를 질문해보세요.')],
            'reviews':[('회사동기','하위 32%','더 큰 현장 도전 의지는 있으나 한일시멘트를 선택한 구체적 이유 서술이 부족함.','여러 생산 기업 중 한일시멘트에 지원한 구체적 이유를 질문해보세요.'),
                       ('협상력','하위 9%','해당 역량을 확인할 수 없음','이해관계가 다른 상대와 조건을 협의해 합의한 경험을 질문해보세요.')]},
 'completeness': {'답변적합도':'문항 의도를 대체로 반영하여 답변함','구체성':'서술이 다소 일반적이고 수치 근거가 부족','본인소개':'본인 경험 중심으로 서술됨'},
 'hard': {'공정 안정화·품질관리':[7,8,17,18],'화공·고분자·신소재 전공 지식':[10,11],'생산·제조 실무 경험':[15,16]},
 'hard_summ': {'공정 안정화·품질관리':'공정 조건이 결과에 미치는 영향을 살피고 품질 기준의 중요성을 체득한 경험 확인.',
               '화공·고분자·신소재 전공 지식':'종합 설계에서 새 방식 박막의 특성을 분석한 신소재 관련 경험 확인.',
               '생산·제조 실무 경험':'수처리 배관 제작 공장에서 검사·도면 대조 등 현장 실무를 수행한 경험 확인.'},
},
4: {
 'headline': '정량적 직무 역량은 매우 우수하나 본인 중심 서술이 부족합니다',
 'pac': ['협력 요청·경제성 평가 등 프로젝트 경험', '인턴십서 산업 기술·경쟁력 분석 습관 형성', '병목 발견·타 부서 소통으로 문제 해결', '탄산칼슘 연구·BET 분석 등 화공 전공', '열분해 공정 설계로 수소·생산비 절감 달성'],
 'eval': {
   '직무경험':'학부연구생·생산기술연구원 인턴, 열분해 공정 설계 등 공학 직무 경험이 풍부함.',
   '직무지식':'경제성 평가·BET 분석·PSA 수소 재사용 등 공정·분석 지식을 폭넓게 보유함.',
   '직무동기jma':'공정에 투입되어 안정화에 기여하려는 직무 관심이 드러나나 표현은 다소 거침.',
   '전략적사고':'열분해 공정의 경제성과 수소 재사용까지 고려한 전략적 설계가 확인됨.',
   '실행력':'BET 분석으로 흡착 효율을 정량화하고 공정도를 작성해 끝까지 구현함.',
   '문제해결력':'로터리킬른 문제·수소 비용 구조를 PSA 공정으로 개선한 문제 해결 경험 확인.',
   '발전가능성':'특허·학회로 산업 기술을 탐색하며 경쟁력을 분석하는 학습 습관 확인.',
   '주도성':'특허를 참고해 단양공장 시멘트를 미리 학습하는 등 주도적 준비 확인.',
   '성실성':'분쇄·활성화·소성을 직접 거치며 재현성·신뢰도를 확보한 성실성 확인.',
   '책임감':'경진대회에서 협력을 요청하고 프로젝트를 끝까지 수행한 책임감 확인.',
   '갈등관리역량':'카메라 검수 공정의 병목을 타 부서와 소통해 해결한 경험 1건 확인.',
   '팀워크역량':'경진대회에서 학부연구생들에게 협력을 요청해 함께 프로젝트를 수행한 경험 확인.',
   '의사소통역량':'병목 해결을 위해 타 부서와 소통한 사례에서 의사소통 경험이 확인됨.',
   '대인관계역량':'동료의 일까지 살피는 사람을 에이스로 보는 인식은 있으나 본인 사례는 제한적.',
   '직무동기mot':'공정 안정화 기여 의지는 뚜렷하나 입사 후 계획의 구체성은 보통.',
   '회사동기':'단양공장 시멘트를 특허로 학습한 노력은 있으나 회사 선택 이유 서술은 부족함.'},
 'verify': {'strengths':[('직무경험','상위 9%','열분해 공정 설계·경제성 평가 등 정량 성과를 갖춘 공학 직무 경험이 풍부함.','열분해 공정 설계의 경제성·수소 절감 계산의 가정과 검증 방법을 질문해보세요.'),
                         ('직무지식','상위 11%','BET 분석·PSA 공정·경제성 평가 등 공정 설계 전반의 지식을 폭넓게 보유함.','BET 흡착 효율 정량화 경험을 시멘트 품질 분석에 어떻게 적용할지 질문해보세요.')],
            'reviews':[('회사동기','하위 28%','단양공장 학습 노력은 있으나 한일시멘트를 선택한 구체적 이유 서술이 부족함.','여러 화학·소재 기업 중 한일시멘트 생산직에 지원한 이유를 질문해보세요.'),
                       ('리더십역량','하위 10%','해당 역량을 확인할 수 없음','팀이나 과제를 앞장서 이끈 경험이 있는지 질문해보세요.')]},
 'completeness': {'답변적합도':'문항 의도에 부합하게 답변함','구체성':'수치·계산 근거가 풍부해 밀도 높음','본인소개':'외부 상황 서술이 일부 혼재함'},
 'hard': {'공정 설계·개선':[9,10,11,12,13],'화공·고분자·신소재 전공 지식':[7,8],'공정 안정화·품질관리':[6,8],'생산·제조 실무 경험':[2,4]},
 'hard_summ': {'공정 설계·개선':'열분해 공정을 설계하고 PSA 공정으로 수소 사용량을 30% 수준으로 절감한 설계·개선 경험 확인.',
               '화공·고분자·신소재 전공 지식':'탄산칼슘 수화반응 연구와 BET 분석 등 화공·소재 전공 지식을 적용함.',
               '공정 안정화·품질관리':'분쇄·활성화·소성 과정에서 재현성·신뢰도를 확보한 공정 안정화 경험 확인.',
               '생산·제조 실무 경험':'생산기술연구원 인턴·카메라 품질 검수 공정 근무 등 생산 현장 실무 경험 확인.'},
},
5: {
 'headline': '직무 역량과 자기 서술이 모두 우수하나 조직 역량은 부분적입니다',
 'pac': ['12년 개근 등 근면성과 책임감 보유', '두려움 극복하고 먼저 행동하는 주도성', '지시 전에 도울 일을 먼저 찾아 수행', '현장 데이터로 문제를 파악·해결하는 능력', '공정 메커니즘 이해 기반 데이터 해석 역량'],
 'eval': {
   '직무경험':'주조 인턴에서 전기전도도 측정·편석 분석·밀링 최적화 등 직무 직결 경험이 풍부함.',
   '직무지식':'공정 메커니즘 이해 기반의 데이터 해석과 LOT 비교 분석 등 분석 지식을 보유함.',
   '직무동기jma':'현장 데이터로 이상 신호를 조기 차단하려는 직무 관심이 명확함.',
   '전략적사고':'LOT·설비별 데이터를 비교해 편차 패턴을 도출한 분석적 사고가 확인됨.',
   '실행력':'샘플 두께 우선 측정 방식으로 전환해 측정 리드타임을 30% 단축한 실행력 확인.',
   '문제해결력':'전기전도도 미달 원인을 공정 변수·편석 분포로 규명한 문제 해결 경험 확인.',
   '발전가능성':'밀링 기록의 의미를 사수에게 확인해 공정 분석으로 이해한 학습 태도 확인.',
   '주도성':'지시를 기다리지 않고 도울 일을 먼저 찾아 나선 주도성이 일관되게 확인됨.',
   '성실성':'12년 개근 등 환경을 탓하지 않고 먼저 행동하는 성실성이 확인됨.',
   '책임감':'미달 LOT를 신속히 보고해 공정 리스크를 조기에 차단한 책임감이 확인됨.',
   '팀워크역량':'임직원·협력사 담당자의 협조를 이끌어 성과를 낸 협업 경험이 확인됨.',
   '의사소통역량':'사수에게 작업 의미를 확인하고 관계자와 긴밀히 소통한 경험이 확인됨.',
   '직무동기mot':'이상 신호 조기 차단·관계자 조율이라는 직무 본질을 명확히 인식함.',
   '회사동기':'납기·품질을 함께 지키려는 동기는 있으나 회사 고유 강점 언급은 보통.'},
 'verify': {'strengths':[('직무경험','상위 8%','주조 인턴에서 전기전도도 측정·편석 분석·밀링 최적화 등 직무 직결 경험이 풍부함.','밀링 방식 전환으로 리드타임을 30% 단축한 과정과 데이터 근거를 질문해보세요.'),
                         ('직무지식','상위 13%','공정 메커니즘 이해를 바탕으로 LOT별 데이터를 비교해 편차 패턴을 도출하는 지식을 갖춤.','편석 분포와 전도도 편차의 관계를 시멘트 품질 변동 분석에 어떻게 적용할지 질문해보세요.')],
            'reviews':[('리더십역량','하위 8%','해당 역량을 확인할 수 없음','팀이나 과제를 앞장서 이끈 경험이 있는지 질문해보세요.'),
                       ('협상력','하위 10%','해당 역량을 확인할 수 없음','협력사·타 부서와 이해관계가 다른 사안을 협의해 합의한 경험을 질문해보세요.')]},
 'completeness': {'답변적합도':'문항 의도에 부합하게 답변함','구체성':'수치·공정 맥락 중심의 구체적 서술','본인소개':'본인 주어 중심의 명확한 서술'},
 'hard': {'공정 안정화·품질관리':[4,7,11,12,14],'공정 설계·개선':[13,14],'생산·제조 실무 경험':[6,7,8]},
 'hard_summ': {'공정 안정화·품질관리':'전기전도도 미달 원인을 공정 변수로 규명하고 미달 LOT를 조기 차단한 안정화·품질관리 경험 확인.',
               '공정 설계·개선':'샘플 두께 우선 선별 방식으로 측정 공정을 전환해 리드타임을 30% 단축한 개선 경험 확인.',
               '생산·제조 실무 경험':'주조 인턴 현장실습에서 설비별 샘플 측정·기록 등 생산 실무를 수행한 경험 확인.'},
},
}

GMAP = {'상': '상', '중': '중', '하': '하', '없음': '없음'}


def full_sentences(parsed):
    """근거 마스터(절단 가능)를 자소서 본문에서 풀 문장으로 복원 + 문항(q1/q2) 귀속 판정."""
    q1, q2 = parsed['essay']['q1'], parsed['essay']['q2']
    full = {}; qof = {}
    for k, partial in parsed['master'].items():
        pref = partial[:18]
        for qi, body in [(1, q1), (2, q2)]:
            idx = body.find(pref)
            if idx < 0:
                continue
            m = re.search(r'.*?[.?!](?=\s|$)', body[idx:])
            full[k] = (m.group(0) if m else partial).strip()
            qof[k] = qi
            break
        else:
            full[k] = partial; qof[k] = 1
    return full, qof


def segment(body, ev_in_q):
    """본문을 [연결/근거(hl)] 세그먼트로 분할. ev_in_q: [(id, fulltext)] 위치순."""
    spans = []
    for eid, et in ev_in_q:
        idx = body.find(et[:18])
        if idx >= 0:
            end = idx + len(et)
            spans.append((idx, end, eid, body[idx:end]))
    spans.sort()
    segs = []; pos = 0
    for s, e, eid, txt in spans:
        if s > pos:
            t = body[pos:s].strip()
            if t:
                segs.append({'text': t, 'hl': False, 'gpk': False})
        segs.append({'id': eid, 'text': txt, 'hl': True, 'gpk': False})
        pos = max(pos, e)
    if pos < len(body):
        t = body[pos:].strip()
        if t:
            segs.append({'text': t, 'hl': False, 'gpk': False})
    return segs


def cohort():
    keys = ['직무적합도', '조직적합도', '지원동기', '답변적합도', '구체성', '본인소개']
    tot = [BP_OVERRIDE.get(n, P[str(n)]['bp']) for n in range(1, 6)]
    avg = {'total': round(sum(tot) / 5, 2)}
    for k in keys:
        avg[k] = round(sum(P[str(n)]['scores'][k] for n in range(1, 6)) / 5, 2)
    radar = [avg[k] for k in keys]
    cut = sorted(tot, reverse=True)[2]   # 3배수=3위 총점
    return avg, radar, cut


def main():
    avg, radar, cut = cohort()
    totals = {n: BP_OVERRIDE.get(n, P[str(n)]['bp']) for n in range(1, 6)}
    rank = {n: sorted(totals, key=lambda x: -totals[x]).index(n) + 1 for n in range(1, 6)}
    pct = {n: int((rank[n] - 0.5) / 5 * 100) for n in range(1, 6)}  # 상위% 근사

    for n in range(1, 6):
        pr = P[str(n)]; a = AUTH[n]
        old = json.load(open(os.path.join(BASE, f'dataset-응시자{n}.json'), encoding='utf-8'))
        full, qof = full_sentences(pr)

        # evaluation
        def itm(name, level, grade, evi, summ):
            return {'name': name, 'level': level, 'grade': grade,
                    'summary': summ if grade != '없음' and evi else '', 'evidence_ids': evi if grade != '없음' else []}
        jf = pr['jma']['factors']; parent = pr['jma']['parent']
        jma = [itm('직무경험', 'factor', jf['직무경험'][0], jf['직무경험'][1], a['eval'].get('직무경험', '')),
               itm('직무지식', 'factor', jf['직무지식'][0], jf['직무지식'][1], a['eval'].get('직무지식', '')),
               itm('직무동기', 'factor', jf['직무동기'][0], jf['직무동기'][1], a['eval'].get('직무동기jma', '')),
               {'name': '직무역량', 'level': 'subcat-header', 'grade': parent}]
        for s in SUBS:
            evi = pr['jma']['subs'][s]
            g = parent if evi else '없음'
            jma.append(itm(s, 'sub', g, evi, a['eval'].get(s, '')))
        org = []
        for nm in ORG:
            g, evi = pr['org'][nm]
            org.append(itm(nm, 'sub', g, evi, a['eval'].get(nm, '')))
        mot = []
        for nm, key in [('직무동기', '직무동기mot'), ('회사동기', '회사동기')]:
            g, evi = pr['mot'][nm]
            mot.append(itm(nm, 'factor', g, evi, a['eval'].get(key, '')))
        evaluation = {'직무적합도': {'항목': jma}, '조직적합도': {'항목': org}, '지원동기': {'항목': mot}}

        # evidence_sentences (풀 문장)
        ev_sent = {k: full[k] for k in sorted(full, key=int)}

        # essay sentences (문항별 hl)
        questions = []
        for qi, body, oldq in [(1, pr['essay']['q1'], old['essay']['questions'][0]),
                               (2, pr['essay']['q2'], old['essay']['questions'][1])]:
            ev_in_q = [(int(k), full[k]) for k in full if qof[k] == qi]
            segs = segment(body, ev_in_q)
            # detected: 이 문항 근거를 가진 주요 factor(등급) + 하위요인(태그)
            qids = set(int(k) for k in full if qof[k] == qi)
            mains = []
            for area in evaluation.values():
                for it in area['항목']:
                    if it.get('level') in ('factor', 'sub') and it['grade'] != '없음' and set(it.get('evidence_ids', [])) & qids:
                        mains.append((len(set(it['evidence_ids']) & qids), it['name'], it['grade'], it['level']))
            mains.sort(key=lambda x: -x[0])
            seen = set(); metrics = []
            for _, nm, g, lv in mains:
                if lv == 'factor' and nm not in seen:
                    metrics.append({'name': nm, 'grade': g}); seen.add(nm)
                if len(metrics) >= 3:
                    break
            tags = [nm for _, nm, g, lv in mains if lv == 'sub'][:4]
            questions.append({'no': qi, 'title': oldq['title'], 'answer_fit': oldq['answer_fit'],
                              'ai_rate': oldq['ai_rate'], 'gpk': pr['gpk'][qi - 1], 'sentences': segs,
                              'detected': {'metrics': metrics, 'factors': tags}})

        # hard_skills (JD 7종, 검출/미검출)
        hs = []
        for name in JD_HARD:
            if name in a['hard']:
                hs.append({'name': name, 'status': '검출', 'summary': a['hard_summ'][name], 'evidence_ids': a['hard'][name]})
            else:
                hs.append({'name': name, 'status': '미검출', 'summary': '', 'evidence_ids': []})

        # benchmarks (4.1 5명 재계산)
        bm = dict(old['benchmarks'])
        bm['avg'] = avg; bm['radar_avg'] = radar
        bm['cut'] = {'score': cut, 'label': '3배수 컷'}
        bm['percentile'] = pct[n]
        # pass badge label (총점 vs 컷)
        old['meta']['pass_badge'] = {'mode': 'multiple', 'n': 3, 'label': '3배수 이내' if BP_OVERRIDE.get(n, pr['bp']) >= cut else '3배수 초과'}

        # verification 조립
        def vp(t):
            return {'factor': t[0], 'grade': next((it['grade'] for ar in evaluation.values() for it in ar['항목'] if it['name'] == t[0]), '없음'),
                    'pct': t[1], 'comment': t[2], 'interview_question': t[3]}
        verification = {'strengths': [vp(t) for t in a['verify']['strengths']], 'reviews': [vp(t) for t in a['verify']['reviews']]}

        d = {
            '_comment': f"한일시멘트 BP 4.1 정본 — 응시자{n} (2026-06-16). 점수·등급(직무역량 8분자)·근거·자소서는 BP 4.1 PDF 실측. "
                        f"benchmarks.avg/radar_avg/cut/percentile는 5명 4.1 재계산. summary 불릿=PAC(자소서 요약, 그대로). "
                        f"hard_skills=JD 추출 7종 응시자별 검출(근거=자소서 문장). evaluation.summary·verification·completeness·headline은 4.1 근거 기반 생성 코멘트.",
            '_dummy_fields': [
                'benchmarks.top10 (기존값 유지 — 5명 소표본)',
                'summary.headline (생성 코멘트 — PAC는 불릿만 제공)',
                'evaluation.항목[].summary·verification·completeness (생성 코멘트)',
                '직무역량 하위 등급 (모분류 상속/없음 파생), essay.detected (근거-문항 매핑 파생)',
                'essay.questions[].answer_fit·ai_rate (GPK 정합 샘플)',
                'hard_skills 검출판단 (JD 추출 + 자소서 매핑 — 본 세션 LLM 판단)',
            ],
            'meta': old['meta'], 'scores': {'total': BP_OVERRIDE.get(n, pr['bp']), **pr['scores']},
            'benchmarks': bm, 'summary': {'headline': a['headline'], 'bullets': a['pac']},
            'evaluation': evaluation, 'completeness': {k: {'short_text': v} for k, v in a['completeness'].items()},
            'verification': verification, 'essay': {'questions': questions}, 'hard_skills': {'항목': hs},
            'evidence_sentences': ev_sent,
        }
        # 무결성
        ids = set(int(k) for k in ev_sent); ref = set()
        for ar in evaluation.values():
            for it in ar['항목']:
                ref |= set(it.get('evidence_ids', []))
        for h in hs:
            ref |= set(h['evidence_ids'])
        miss = ref - ids
        assert not miss, f"app{n} evidence 누락 {miss}"
        assert len(a['headline']) <= 54, f"app{n} headline {len(a['headline'])}"

        json.dump(d, open(os.path.join(BASE, f'dataset-응시자{n}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        hy = sum(1 for h in hs if h['status'] == '검출')
        print(f"app{n}: BP {BP_OVERRIDE.get(n, pr['bp'])} 컷{cut} {'이내' if pr['bp']>=cut else '미달'} 상위{pct[n]}% | 근거 {len(ev_sent)} | 하드 검출{hy}/{len(hs)} | PAC {len(a['pac'])} | detected {[len(q['detected']['metrics']) for q in questions]}")
    print(f"[5명 4.1 평균] {avg}")


if __name__ == '__main__':
    main()
