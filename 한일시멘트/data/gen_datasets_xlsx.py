# -*- coding: utf-8 -*-
"""한일시멘트 BP — 최종 엑셀(BP데이터_..._7a73f657_직무역량총계등급 추가.xlsx)로 5명 데이터셋 최신화 (2026-06-17)
  실측(엑셀): 총점·6메트릭·문항별 답변적합도 / 역량별 등급(8분자 개별 + 직무역량 집계)·평가요약(explain) / 근거문장(문항·offset) / 자소서 전문
  보존(엑셀 미포함): PAC 불릿·헤드라인·하드스킬(JD)·면접질문·상위/하위% pct·GPK·completeness·meta
  상대평가: 평균·radar_avg·컷=5명 집계 / 상위10%=90백분위 / 상위%=총점순위
  BP 총점 = ⌊Σ(metric×weight)⌋ 산식 재계산 (엑셀 시트1 총점은 app1에서 시스템 산출오류 65.55 → 산식 68.07, CH-029)
  사용: python3 data/gen_datasets_xlsx.py && python3 build_reports.py
"""
import openpyxl, json, os, re, math

BASE = os.path.dirname(os.path.abspath(__file__))
XL = os.path.join(BASE, '..', 'BP데이터_한일시멘트_7a73f657_직무역량총계등급 추가.xlsx')
wb = openpyxl.load_workbook(XL, data_only=True)

WEIGHT = {'직무적합도': 0.25, '조직적합도': 0.20, '지원동기': 0.20, '답변적합도': 0.10, '구체성': 0.20, '본인소개': 0.05}

GMAP = {'high': '상', 'mid': '중', 'low': '하', 'none': '없음'}
JOB_FACTOR = {'workExperience': '직무경험', 'jobKnowledge': '직무지식', 'jobMotivation': '직무동기'}
SUB_ORDER = ['strategicThinking', 'abilityToExecute', 'problemSolving', 'potentialForGrowth',
             'personalInitiative', 'compliance', 'diligence', 'responsibility']
SUB_KO = {'strategicThinking': '전략적사고', 'abilityToExecute': '실행력', 'problemSolving': '문제해결력',
          'potentialForGrowth': '발전가능성', 'personalInitiative': '주도성', 'compliance': '원칙준수',
          'diligence': '성실성', 'responsibility': '책임감'}
ORG_ORDER = ['leadership', 'negotiation', 'conflictManagement', 'teamwork', 'communication', 'socialSkills']
ORG_KO = {'leadership': '리더십역량', 'negotiation': '협상력', 'conflictManagement': '갈등관리역량',
          'teamwork': '팀워크역량', 'communication': '의사소통역량', 'socialSkills': '대인관계역량'}
# 역량명(한글, 공백 제거) → 역량키 (시트3은 역량키가 없어 이름으로 매칭)
NAME2KEY = {'직무경험': 'workExperience', '직무지식': 'jobKnowledge', '직무동기': 'jobMotivation',
            '전략적사고': 'strategicThinking', '실행력': 'abilityToExecute', '문제해결력': 'problemSolving',
            '발전가능성': 'potentialForGrowth', '주도성': 'personalInitiative', '원칙준수': 'compliance',
            '성실성': 'diligence', '책임감': 'responsibility', '리더십역량': 'leadership', '협상력': 'negotiation',
            '갈등관리역량': 'conflictManagement', '팀워크역량': 'teamwork', '의사소통역량': 'communication',
            '대인관계역량': 'socialSkills', '회사동기': 'companyMotivation'}


def norm(s):
    return str(s).replace(' ', '').strip()


def clean(s):
    return re.sub(r'\s+', ' ', str(s).replace('□', '℃').replace('\xa0', ' ')).strip() if s is not None else ''


def rows(sheet):
    return list(wb[sheet].iter_rows(values_only=True))


# ── 시트1: 점수 ── (col15='직무역량(집계)등급' 실측 추가, 2026-06-17)
S1 = {}
for r in rows('1.요약(지원자별)')[1:]:
    aid = str(r[2])
    q1af, q2af = round(r[11] / 100, 2), round(r[12] / 100, 2)
    m = {'직무적합도': round(r[8] / 100, 2), '조직적합도': round(r[9] / 100, 2), '지원동기': round(r[10] / 100, 2),
         '답변적합도': round((r[11] + r[12]) / 2 / 100, 2), '구체성': round(r[13] / 100, 2), '본인소개': round(r[14] / 100, 2)}
    # BP 총점 = ⌊Σ(metric×weight)⌋ — 엑셀 r[7]은 app1에서 시스템 산출오류(65.55) → 산식 재계산(68.07, CH-029)
    total = math.floor(sum(m[k] * WEIGHT[k] for k in WEIGHT) * 100) / 100
    agg = str(r[15]).strip() if r[15] else '하'
    S1[aid] = {'total': total, **m, 'af': (q1af, q2af), 'agg_grade': '없음' if agg == '해당없음' else agg}

# ── 시트2: 역량별 등급·평가요약 ──  S2[aid][(평가영역, 역량키)] = (grade_ko, explain)
S2 = {}
for r in rows('2.역량평가(factor별)')[1:]:
    aid = str(r[0]); area = r[3]; key = r[5]; grade = GMAP.get(r[7], r[6]); explain = clean(r[10])
    S2.setdefault(aid, {})[(area, key)] = (grade, explain)

# ── 시트3: 근거문장 (문항·offset) ──  S3[aid] = [(area, key, 문항, value, begin, end)]
S3 = {}
for r in rows('3.근거문장(reason)')[1:]:
    aid = str(r[0]); area = r[2]; key = NAME2KEY.get(norm(r[3]), norm(r[3])); 문항 = int(r[6])
    S3.setdefault(aid, []).append((area, key, 문항, r[7], r[12], r[13]))

# ── 시트6: 자소서 (raw, □→℃만 — offset 보존) ──
S4 = {}
for r in rows('6.자소서(문항별답변)')[1:]:
    S4[str(r[0])] = (str(r[3]).replace('□', '℃'), str(r[4]).replace('□', '℃'))

QTITLE = {}
for r in rows('0.검사방정보'):
    if r[0] == '문항1': QTITLE[1] = clean(r[1])
    if r[0] == '문항2': QTITLE[2] = clean(r[1])


def pctl(vals, p):
    s = sorted(vals); n = len(s); idx = p * (n - 1); lo = int(idx); frac = idx - lo
    return s[lo] if lo + 1 >= n else s[lo] + frac * (s[lo + 1] - s[lo])


def build_evidence(aid):
    """근거문장 → 글로벌 id(문항·begin 순) + factor별 id + 문항별 hl 세그먼트."""
    ev = S3.get(aid, [])
    uniq = {}  # (문항, begin) -> (end, text)
    for area, key, 문항, val, b, e in ev:
        uniq.setdefault((문항, b), (e, clean(val)))
    order = sorted(uniq.keys())  # (문항, begin)
    id_of = {k: i + 1 for i, k in enumerate(order)}
    evidence_sentences = {str(id_of[k]): uniq[k][1] for k in order}
    # factor(area,key) -> evidence_ids
    fac_ids = {}
    for area, key, 문항, val, b, e in ev:
        fac_ids.setdefault((area, key), set()).add(id_of[(문항, b)])
    fac_ids = {k: sorted(v) for k, v in fac_ids.items()}
    # 문항별 hl 세그먼트 (raw offset 기반)
    seg_by_q = {}
    for 문항 in (1, 2):
        body = S4[aid][문항 - 1]
        spans = sorted([(b, uniq[(문항, b)][0], id_of[(문항, b)]) for (mq, b) in uniq if mq == 문항])
        segs = []; pos = 0
        for b, e, sid in spans:
            if b > pos:
                t = clean(body[pos:b])
                if t: segs.append({'text': t, 'hl': False, 'gpk': False})
            segs.append({'id': sid, 'text': clean(body[b:e]), 'hl': True, 'gpk': False})
            pos = max(pos, e)
        tail = clean(body[pos:])
        if tail: segs.append({'text': tail, 'hl': False, 'gpk': False})
        seg_by_q[문항] = segs
    # 문항별 id 집합 (detected용)
    qids = {1: set(), 2: set()}
    for (mq, b), sid in id_of.items():
        qids[mq].add(sid)
    return evidence_sentences, fac_ids, seg_by_q, qids


def main():
    # 상대평가 집계
    keys = ['직무적합도', '조직적합도', '지원동기', '답변적합도', '구체성', '본인소개']
    aids = list(S1.keys())
    avg = {'total': round(sum(S1[a]['total'] for a in aids) / 5, 2)}
    top10 = {'total': round(pctl([S1[a]['total'] for a in aids], 0.9), 2)}
    for k in keys:
        avg[k] = round(sum(S1[a][k] for a in aids) / 5, 2)
        top10[k] = round(pctl([S1[a][k] for a in aids], 0.9), 2)
    radar = [avg[k] for k in keys]
    cut = sorted((S1[a]['total'] for a in aids), reverse=True)[2]
    rank = {a: sorted(aids, key=lambda x: -S1[x]['total']).index(a) + 1 for a in aids}
    pct = {a: int((rank[a] - 0.5) / 5 * 100) for a in aids}

    for n in range(1, 6):
        aid = str(n)
        cur = json.load(open(os.path.join(BASE, f'dataset-응시자{n}.json'), encoding='utf-8'))
        # 표시명·번호 (사용자 지시 2026-06-17): '응시자N'→'지원자N'(엑셀 지원자명 일치), 응시번호 '000N'→'N'(한자리)
        cur['meta']['candidate'] = f'지원자{n}'
        cur['meta']['candidate_number'] = str(n)
        evs, fac_ids, seg_by_q, qids = build_evidence(aid)

        def factor_item(area, key, level, name_ko):
            grade, explain = S2[aid].get((area, key), ('없음', ''))
            ids = fac_ids.get((area, key), [])
            return {'name': name_ko, 'level': level, 'grade': grade,
                    'summary': explain, 'evidence_ids': ids}

        # 직무적합도: 3 factor + 직무역량 subcat(집계등급 엑셀 실측) + 8 sub
        jma = [factor_item('직무적합도', 'workExperience', 'factor', '직무경험'),
               factor_item('직무적합도', 'jobKnowledge', 'factor', '직무지식'),
               factor_item('직무적합도', 'jobMotivation', 'factor', '직무동기')]
        # 직무역량 중분류(집계) 등급: 시트1 '직무역량(집계)등급' 실측 (2026-06-17 추가, PDF추정값 대체)
        jma.append({'name': '직무역량', 'level': 'subcat-header', 'grade': S1[aid]['agg_grade']})
        for key in SUB_ORDER:
            jma.append(factor_item('직무적합도', key, 'sub', SUB_KO[key]))
        org = [factor_item('조직적합도', key, 'sub', ORG_KO[key]) for key in ORG_ORDER]
        mot = [factor_item('지원동기', 'jobMotivation', 'factor', '직무동기'),
               factor_item('지원동기', 'companyMotivation', 'factor', '회사동기')]
        evaluation = {'직무적합도': {'항목': jma}, '조직적합도': {'항목': org}, '지원동기': {'항목': mot}}

        # explain by factor name (검증포인트 코멘트용) — 직무동기는 직무적합도 기준
        explain_by_name = {}
        for (area, key), (g, ex) in S2[aid].items():
            nm = JOB_FACTOR.get(key) or SUB_KO.get(key) or ORG_KO.get(key) or ('회사동기' if key == 'companyMotivation' else None)
            if nm and (nm not in explain_by_name or area == '직무적합도'):
                explain_by_name[nm] = (g, ex)

        # P3 노출 규칙(CH-034): 상단=6개 메트릭+점수(해당 문항에 factor 근거가 닿은 메트릭만, 고정 순서),
        #   하단=검출된 factor 전부(cap 없음). 메트릭은 점수만 있고 등급 없음 → 등급칩 대신 '점수' 표기
        #   (사용자 확정: 원본에 없는 등급 임의부여 금지). 직무역량(집계)은 컨테이너라 하단 factor 목록에서 제외.
        #   rollup: 메트릭 영역(직무적합도/조직적합도/지원동기) 내 어떤 factor라도 검출되면 그 메트릭+점수 표시.
        METRIC_ORDER = ['직무적합도', '조직적합도', '지원동기', '답변적합도', '구체성', '본인소개']
        metric_fac_ids = {'직무적합도': set(), '조직적합도': set(), '지원동기': set()}
        for it in jma:  # 직무적합도 (직무경험·지식·동기 + 8분자)
            if it['level'] in ('factor', 'sub'):
                metric_fac_ids['직무적합도'] |= set(it['evidence_ids'])
        for it in org:  # 조직적합도 (리더십·팀워크 등)
            if it['level'] in ('factor', 'sub'):
                metric_fac_ids['조직적합도'] |= set(it['evidence_ids'])
        for it in mot:  # 지원동기 (직무동기·회사동기)
            if it['level'] in ('factor', 'sub'):
                metric_fac_ids['지원동기'] |= set(it['evidence_ids'])

        # essay
        questions = []
        for q in (1, 2):
            af = S1[aid]['af'][q - 1]
            gpk = cur['essay']['questions'][q - 1].get('gpk', '탐지')
            qid = qids[q]
            # 상단: factor 근거가 닿은 메트릭만 + 점수 (답변적합도·구체성·본인소개는 factor 없어 미출현)
            metrics = [{'name': m, 'score': S1[aid][m]} for m in METRIC_ORDER
                       if metric_fac_ids.get(m, set()) & qid]
            # 하단: 검출된 factor 전부 (직무역량 집계=컨테이너 제외, 중복 제거, 근거수 정렬, cap 없음)
            fachits = {}
            for it in jma + org + mot:
                if it['level'] in ('factor', 'sub') and it['grade'] != '없음':
                    c = len(set(it['evidence_ids']) & qid)
                    if c:
                        fachits[it['name']] = max(fachits.get(it['name'], 0), c)
            tags = [nm for nm, _ in sorted(fachits.items(), key=lambda x: -x[1])]
            questions.append({'no': q, 'title': QTITLE[q], 'answer_fit': af, 'ai_rate': cur['essay']['questions'][q - 1].get('ai_rate', 0),
                              'gpk': gpk, 'sentences': seg_by_q[q], 'detected': {'metrics': metrics, 'factors': tags}})

        # verification: 선별·pct·면접질문 보존, 등급·코멘트(explain)는 갱신
        def vp_update(v):
            g, ex = explain_by_name.get(v['factor'], (v['grade'], v['comment']))
            return {'factor': v['factor'], 'grade': g, 'pct': v['pct'],
                    'comment': ex or v['comment'], 'interview_question': v['interview_question']}
        verification = {'strengths': [vp_update(v) for v in cur['verification']['strengths']],
                        'reviews': [vp_update(v) for v in cur['verification']['reviews']]}

        # hard_skills: 근거 id를 옛(PDF) → 새(엑셀) id로 텍스트 prefix 매칭 재매핑
        cur_evs = cur.get('evidence_sentences', {})
        def remap(old_ids):
            out = []
            for oid in old_ids:
                ot = cur_evs.get(str(oid), '')
                if not ot:
                    continue
                for nid, nt in evs.items():
                    if nt[:14] == ot[:14]:
                        out.append(int(nid)); break
            return sorted(set(out))
        hard = {'항목': []}
        for h in cur['hard_skills']['항목']:
            nids = remap(h['evidence_ids']) if h['status'] == '검출' else []
            hard['항목'].append({'name': h['name'], 'status': h['status'], 'summary': h['summary'], 'evidence_ids': nids})

        # benchmarks
        bm = dict(cur['benchmarks']); bm['avg'] = avg; bm['radar_avg'] = radar; bm['top10'] = top10
        bm['cut'] = {'score': cut, 'label': '3배수 컷'}; bm['percentile'] = pct[aid]
        cur['meta']['pass_badge'] = {'mode': 'multiple', 'n': 3, 'label': '3배수 이내' if S1[aid]['total'] >= cut else '3배수 초과'}

        d = {
            '_comment': f"한일시멘트 BP — 응시자{n} (최종 엑셀 7a73f657_직무역량총계등급 기준 최신화, 2026-06-17). "
                        f"점수·문항별 답변적합도·역량별 등급(8분자 개별 + 직무역량 집계)·평가요약(explain)·근거문장(문항·offset)·자소서는 엑셀 실측. "
                        f"BP 총점=⌊Σ(metric×weight)⌋ 산식 재계산(app1 엑셀 65.55는 시스템오류 → 68.07, CH-029). "
                        f"benchmarks 평균·radar·컷=5명 집계, 상위10%=90백분위, 상위%=총점순위. "
                        f"PAC·헤드라인·하드스킬(JD)·면접질문·상위/하위%·GPK·completeness는 기존 보존.",
            '_dummy_fields': [
                'summary.headline (생성)', 'summary.bullets (PAC 별도제공)',
                'hard_skills.항목 (JD 추출+자소서 검출 — 엑셀 외)',
                'verification.pct·interview_question (생성/순위) — comment·grade는 엑셀 실측',
                'essay.gpk (PDF 실측 탐지/미탐지 — 엑셀 외)·ai_rate (미사용)',
                'completeness.*.short_text (생성)',
                'benchmarks.top10 (5명 90백분위)·cut·percentile (5명 집계)',
                'essay.detected (근거-문항 매핑 파생)',
            ],
            'meta': cur['meta'], 'scores': {'total': S1[aid]['total'], **{k: S1[aid][k] for k in keys}},
            'benchmarks': bm, 'summary': cur['summary'], 'evaluation': evaluation,
            'completeness': cur['completeness'], 'verification': verification,
            'essay': {'questions': questions}, 'hard_skills': hard, 'evidence_sentences': evs,
        }
        # 무결성: evidence_ids ⊆ evidence_sentences
        ids = set(int(k) for k in evs); ref = set()
        for ar in evaluation.values():
            for it in ar['항목']: ref |= set(it.get('evidence_ids', []))
        for h in d['hard_skills']['항목']: ref |= set(h['evidence_ids'])
        miss = ref - ids
        assert not miss, f"app{n} evidence 누락 {miss} (하드스킬은 PDF 근거번호라 엑셀 id와 다를 수 있음)"

        json.dump(d, open(os.path.join(BASE, f'dataset-응시자{n}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f"app{n}: BP {S1[aid]['total']} 답변({S1[aid]['af']}) 근거 {len(evs)} | 합불 {cur['meta']['pass_badge']['label']} 상위{pct[aid]}%")
    print(f"[집계] 평균 {avg['total']} 컷 {cut} 상위10%(total) {top10['total']}")


if __name__ == '__main__':
    main()
