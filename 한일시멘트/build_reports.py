# -*- coding: utf-8 -*-
"""
한일시멘트 BP 4.2 결과지 빌드 스크립트
  data/dataset-응시자N.json × template-bp42.html → prism-한일시멘트-응시자N-[날짜].html
근거: 작업계획서 §9(데이터 슬롯 맵)·§9-5(파생 규칙)·§9-10(사용 가이드)
사용: python3 build_reports.py
"""
import json, glob, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(BASE, 'template-bp42.html')
OUT_DATE = '20260613'

# ── §9-5-⑦ 룰 베이스 텍스트 (참고-SDS-매트릭별근거내용.md) ──
RULE_TEXTS = {
    '답변적합도': [
        (80, '문항에서 요구하는 의도를 정확히 파악하고, 이에 부합하는 내용으로 답변을 구성함'),
        (60, '문항 의도를 대체로 반영하고 있으며, 일부 항목에서 답변 방향이 소폭 벗어남'),
        (40, '문항 의도와 부분적으로 연관된 내용이 포함되어 있으나, 전반적으로 초점이 불명확함'),
        (20, '문항 의도와 다른 내용 중심으로 서술되어 있어 연관성이 낮음'),
        (0,  '문항과 실질적인 연관성이 확인되지 않으며, 답변이 질문 범위를 크게 벗어남')],
    '구체성': [
        (80, '구체적인 경험, 수치, 키워드가 풍부하게 포함되어 있으며 서술의 밀도가 높음'),
        (60, '구체적 서술이 전반적으로 포함되어 있으며, 일부 표현에서 추상적 요소가 혼재함'),
        (40, '구체적 서술과 추상적 표현이 고르게 섞여 있어 전달력이 다소 부족함'),
        (20, '추상적이거나 일반적인 표현 위주로 서술되어 있으며, 구체적 근거 제시가 적음'),
        (0,  '구체적 경험·수치·키워드가 거의 확인되지 않으며, 서술이 전반적으로 막연함')],
    '본인소개': [
        (80, '대부분의 문장이 본인 주어로 서술되어 있으며, 자신의 경험과 역할이 명확하게 드러남'),
        (60, '본인 중심의 서술 비율이 높으며, 일부 문장에서 외부 상황 서술이 포함됨'),
        (40, '본인 서술과 일반 서술이 혼재하여 지원자 고유의 관점이 명확하지 않음'),
        (20, '일반적 상황이나 외부 요인 중심의 서술이 많아 본인 역할이 잘 드러나지 않음'),
        (0,  '본인 주어 문장이 거의 없으며, 서술의 주체가 불분명함')],
}
def rule_text(metric, score):
    for lo, txt in RULE_TEXTS[metric]:
        if score >= lo: return txt
    return RULE_TEXTS[metric][-1][1]

# ── 등급 → 칩 클래스 매핑 (§9-5-③) ──
GRADE_P1   = {'상': ('g-high', '상'), '중': ('g-mid', '중'), '하': ('g-low', '하'), '없음': ('g-none', '-')}
GRADE_VP   = {'상': ('high', '상'), '중': ('mid', '중'), '하': ('low', '하'), '없음': ('none', '-')}
GRADE_DT   = {'상': ('high', '상'), '중': ('mid', '중'), '하': ('low', '하'), '없음': ('none', '-')}
# factor → 대분류 (P2 vp-cat 표기)
FACTOR_AREA = {
    '직무경험': '직무적합도', '직무지식': '직무적합도',
    '주도성': '직무역량', '성취지향': '직무역량', '전략적사고': '직무역량', '실행력': '직무역량', '메타인지역량': '직무역량',
    '리더십역량': '조직적합도', '협상력': '조직적합도', '갈등관리역량': '조직적합도',
    '팀워크역량': '조직적합도', '의사소통역량': '조직적합도', '대인관계역량': '조직적합도',
    '회사동기': '지원동기', '직무동기': '지원동기',
}

f2 = lambda v: f'{v:.2f}'

def cmp_html(group, score, avg):
    d = score - avg
    cls, sign = ('up', '+') if d >= 0 else ('down', '−')
    return f'{group} 평균 대비 <span class="{cls} num">{sign}{abs(d):.2f}p</span>'

def metric_bar(score, avg, top10):
    return f'''<div class="cbar mini">
            <div class="cbar-track"></div>
            <div class="cbar-fill" style="width:{f2(score)}%;background:rgba(0,117,255,0.3);height:14px;"></div>
            <div class="cbar-dot dot-avg" style="left:{f2(avg)}%;width:10px;height:10px;"></div>
            <div class="cbar-dot dot-top" style="left:{f2(top10)}%;width:10px;height:10px;"></div>
          </div>
          <div class="cbar-legend">
            <span class="lg"><span class="sw" style="background:#7C52F1;width:10px;height:10px;"></span><span><b>평균 점수</b> <span class="num">{f2(avg)}</span></span></span>
            <span class="lg"><span class="sw" style="background:#041D30;width:10px;height:10px;"></span><span><b>상위 10% 점수</b> <span class="num">{f2(top10)}</span></span></span>
          </div>'''

def validate_lengths(d):
    """§9-8 길이 제약 — 위반 시 P1 고정 영역(서머리 294px)이 넘쳐 하부가 잘리므로 빌드 실패 처리."""
    errs = []
    if len(d['summary']['headline']) > 54:
        errs.append(f"headline {len(d['summary']['headline'])}자 > 54 (헤드라인 폭 460px에서 2줄 초과, CH-017)")
    for i, b in enumerate(d['summary']['bullets']):
        if len(b) > 29:
            errs.append(f"불릿{i+1} {len(b)}자 > 29 (1줄 초과): {b}")
    if len(d['summary']['bullets']) > 4:
        errs.append(f"불릿 {len(d['summary']['bullets'])}개 > 4")
    if errs:
        raise RuntimeError(f"{d['meta']['candidate']} §9-8 길이 제약 위반:\n  " + "\n  ".join(errs))

def build(d):
    validate_lengths(d)
    m, sc, bm = d['meta'], d['scores'], d['benchmarks']
    group = bm['group']
    t = open(TEMPLATE, encoding='utf-8').read()
    T = {}

    # ── 공통 ──
    T['CHANNEL_TITLE'] = m['channel_title']
    T['NAME'] = m['candidate']
    T['NUM'] = str(m['candidate_number'])
    T['POSITION'] = m['position']
    T['EVAL_DATE'] = m['evaluation_date']
    T['TOTAL'] = f2(sc['total'])

    # ── P1 배지 (§9-5-①: mode null → 합불 배지·컷 점 미출력) ──
    badges = [f'          <div class="bp-badge">{group} 상위 {bm["percentile"]}%</div>']
    has_cut = m['pass_badge'].get('mode') is not None
    if has_cut:
        badges.append(f'          <div class="bp-badge fill">{m["pass_badge"]["label"]}</div>')
    T['BADGES_HTML'] = '\n'.join(badges)

    # ── 서머리 ──
    T['HEADLINE'] = d['summary']['headline']
    T['BULLETS_HTML'] = '\n' + '\n'.join(f'          <li>{b}</li>' for b in d['summary']['bullets']) + '\n        '
    cut_dot = f'\n              <div class="cbar-dot dot-cut" style="left:{f2(bm["cut"]["score"])}%;"></div>' if has_cut else ''
    cut_lg = f'\n              <span class="lg"><span class="sw" style="background:#fff;border:2px solid #ff006b;"></span><span><b>{bm["cut"]["label"]}</b> <span class="num">{f2(bm["cut"]["score"])}</span></span></span>' if has_cut else ''
    T['SUMMARY_BAR_HTML'] = f'''<div class="cbar">
              <div class="cbar-track"></div>
              <div class="cbar-fill" style="width:{f2(sc['total'])}%;background:rgba(0,117,255,0.45);"></div>
              <div class="cbar-dot dot-avg" style="left:{f2(bm['avg']['total'])}%;"></div>{cut_dot}
              <div class="cbar-dot dot-top" style="left:{f2(bm['top10']['total'])}%;"></div>
            </div>
            <div class="cbar-legend">{cut_lg}
              <span class="lg"><span class="sw" style="background:#7C52F1;"></span><span><b>평균</b> <span class="num">{f2(bm['avg']['total'])}</span></span></span>
              <span class="lg"><span class="sw" style="background:#041D30;"></span><span><b>상위 10%</b> <span class="num">{f2(bm['top10']['total'])}</span></span></span>
            </div>'''

    # ── P1 역량 3카드 ──
    items_jma = d['evaluation']['직무적합도']['항목']
    factors_jma = [i for i in items_jma if i['level'] == 'factor']
    subhead = next(i for i in items_jma if i['level'] == 'subcat-header')
    subs_jma = [i for i in items_jma if i['level'] == 'sub']
    T['JMA_SCORE'] = f2(sc['직무적합도'])
    T['JMA_CMP'] = cmp_html(group, sc['직무적합도'], bm['avg']['직무적합도'])
    T['JMA_BAR'] = metric_bar(sc['직무적합도'], bm['avg']['직무적합도'], bm['top10']['직무적합도'])
    def grow(it):
        cls, txt = GRADE_P1[it['grade']]
        return f'<div class="grow"><span class="lbl">{it["name"]}</span><span class="grade {cls}">{txt}</span></div>'
    T['JMA_LEFT_ROWS'] = '\n            ' + '\n            '.join(grow(i) for i in factors_jma) + '\n          '
    cls, txt = GRADE_P1[subhead['grade']]
    T['JMA_SUBHEAD'] = f'<span class="lbl">직무역량</span><span class="grade {cls}">{txt}</span>'
    srows = []
    for i in subs_jma:
        cls, txt = GRADE_P1[i['grade']]
        srows.append(f'<div class="srow"><span class="lbl">{i["name"]}</span><span class="grade {cls}">{txt}</span></div>')
    if len(srows) % 2 == 1:
        srows.append('<div class="srow" style="border-bottom:none;"><span class="lbl">&nbsp;</span></div>')
    T['JMA_SUB_ROWS'] = '\n              ' + '\n              '.join(srows) + '\n            '

    hs_yes = [h['name'] for h in d['hard_skills']['항목'] if h['status'] == '검출']
    hs_no = [h['name'] for h in d['hard_skills']['항목'] if h['status'] == '미검출']
    T['HS_YES_LIST'] = ', '.join(hs_yes) if hs_yes else '없음'
    T['HS_NO_LIST'] = ', '.join(hs_no) if hs_no else '없음'

    T['ORG_SCORE'] = f2(sc['조직적합도'])
    T['ORG_CMP'] = cmp_html(group, sc['조직적합도'], bm['avg']['조직적합도'])
    T['ORG_BAR'] = metric_bar(sc['조직적합도'], bm['avg']['조직적합도'], bm['top10']['조직적합도'])
    wrows = []
    for i in d['evaluation']['조직적합도']['항목']:
        cls, txt = GRADE_P1[i['grade']]
        wrows.append(f'<div class="wrow"><span class="lbl">{i["name"]}</span><span class="grade {cls}">{txt}</span></div>')
    T['ORG_ROWS'] = '\n            ' + '\n            '.join(wrows) + '\n          '

    T['MOT_SCORE'] = f2(sc['지원동기'])
    T['MOT_CMP'] = cmp_html(group, sc['지원동기'], bm['avg']['지원동기'])
    T['MOT_BAR'] = metric_bar(sc['지원동기'], bm['avg']['지원동기'], bm['top10']['지원동기'])
    mot_items = d['evaluation']['지원동기']['항목']
    mrows = []
    for n, i in enumerate(mot_items):
        cls, txt = GRADE_P1[i['grade']]
        bb = 'border-bottom:none;' if n == len(mot_items) - 1 else ''
        mrows.append(f'<div class="grow" style="width:100%;{bb}"><span class="lbl">{i["name"]}</span><span class="grade {cls}" style="font-size:14px;">{txt}</span></div>')
    T['MOT_ROWS'] = '\n            ' + '\n            '.join(mrows) + '\n          '

    # ── P1 응답완성도 3박스 (§9-5-④: <40 주의 배지) ──
    boxes = []
    for name in ['답변적합도', '구체성', '본인소개']:
        v = sc[name]
        short = d['completeness'][name]['short_text']
        if v < 40:
            score_html = f'<span class="frame"><span class="warn-badge">주의</span><span class="side-score num">{f2(v)}</span></span>'
        else:
            score_html = f'<span class="side-score num">{f2(v)}</span>'
        boxes.append(f'''        <div class="side-box first">
          <div class="side-head"><span class="side-name">{name}</span>{score_html}</div>
          <div class="side-cmt">{short}</div>
        </div>''')
    T['SIDE_BOXES'] = '\n' + '\n        <div class="side-divider"></div>\n'.join(boxes) + '\n      '

    # ── 레이더 (축 순서·명칭은 Figma 고정: 답변완성도/자기소개) ──
    axes = [('직무적합도', sc['직무적합도']), ('조직적합도', sc['조직적합도']), ('지원동기', sc['지원동기']),
            ('답변완성도', sc['답변적합도']), ('구체성', sc['구체성']), ('자기소개', sc['본인소개'])]
    T['RADAR_LABELS'] = '[' + ', '.join(f"['{n}','{f2(v)}']" for n, v in axes) + ']'
    T['RADAR_AVG'] = '[' + ','.join(str(v) for v in bm['radar_avg']) + ']'
    T['RADAR_USER'] = '[' + ','.join(f2(v) for n, v in axes) + ']'

    # ── P2 검증 포인트 ──
    def vp_item(v, up):
        cls, txt = GRADE_VP[v['grade']]
        area = FACTOR_AREA.get(v['factor'])
        cat = f'<span class="cat">{area}</span>' if area else ''
        badge_cls = 'up' if up else 'down'
        return f'''          <div class="vp-item">
            <div class="vp-item-top">
              <div class="vp-cat">{cat}<div class="vp-name-row"><span class="nm">{v['factor']}</span><span class="vp-grade {cls}">{txt}</span></div></div>
              <span class="vp-badge {badge_cls}">{v['pct']}</span>
            </div>
            <div class="vp-sum">{v['comment']}</div>
            <div class="vp-tip"><span class="tlbl">면접연계</span><span class="ttxt">{v['interview_question']}</span></div>
          </div>'''
    T['VP_STRENGTHS'] = '\n'.join(vp_item(v, True) for v in d['verification']['strengths']).lstrip()
    T['VP_REVIEWS'] = '\n'.join(vp_item(v, False) for v in d['verification']['reviews']).lstrip()

    qrows = []
    for q in d['essay']['questions']:
        qrows.append(f'''      <div class="qrow">
        <div class="qleft"><span class="qno">문항 {q['no']}</span><span class="qtext">{q['title']}</span></div>
        <div class="qright">
          <div class="qmetric"><span>답변적합도</span><span class="v num">{f2(q['answer_fit'])}</span></div>
          <div class="qmetric"><span>AI 작성률</span><span class="pct num">{q['ai_rate']}%</span></div>
        </div>
      </div>''')
    T['QROWS'] = '\n' + '\n'.join(qrows) + '\n    '

    # ── P3 자기소개서 분석 ──
    qcards = []
    for q in d['essay']['questions']:
        groups = ''.join(f'<div class="p3-metric-group"><span class="p3-metric-name">{mm["name"]}</span><span class="vp-grade {GRADE_VP[mm["grade"]][0]}">{GRADE_VP[mm["grade"]][1]}</span></div>'
                         for mm in q['detected']['metrics'])
        parts = []
        for s in q['sentences']:
            if s['hl']: parts.append(f'<span class="hl">{s["text"]}</span>')
            elif s['gpk']: parts.append(f'<span class="gpk">{s["text"]}</span>')
            else: parts.append(s['text'])
        body = ' '.join(parts)
        factors = q['detected']['factors']
        tags = ''.join(f'<span class="p3-skill-tag">{f}{"," if n < len(factors)-1 else ""}</span>\n            '
                       for n, f in enumerate(factors)).rstrip()
        qcards.append(f'''      <div class="p3-qcard">
        <div class="p3-qhead">
          <span>문항 {q['no']}</span>
          <span>{q['title']}</span>
        </div>
        <div class="p3-metric">
          {groups}
        </div>
        <div class="p3-body">
          <p>{body}</p>
        </div>
        <div class="p3-qfooter">
          <div class="p3-skills">
            <span class="p3-skills-label">자기소개서에서 확인한 지원자 역량:</span>
            {tags}
          </div>
          <div class="p3-ai-rate"><span class="p3-ai-lbl">AI 작성률</span><span class="p3-ai-val num">{q['ai_rate']}%</span></div>
        </div>
      </div>''')
    T['P3_QCARDS'] = '\n\n' + '\n\n'.join(qcards) + '\n\n    '

    # ── P4+ 상세 블록 ──
    ev = d['evidence_sentences']
    def dt_body(comment, ids):
        c = comment if comment else '해당 역량을 확인할 수 없음'
        if ids:
            lis = '\n        '.join(f'<li>{ev[str(i)]}</li>' for i in ids)
            lst = f'<ul class="dt-list">\n        {lis}\n      </ul>'
        else:
            lst = '<div class="dt-empty">확인된 자기소개서 근거 문장이 없습니다.</div>'
        return f'''    <div class="dt-row-body">
      <div class="dt-comment">{c}</div>
      <div class="dt-srclabel">자기소개서 내용</div>
      {lst}
    </div>'''
    blocks = []
    for area in ['직무적합도', '조직적합도', '지원동기']:
        blocks.append(f'  <div class="blk dt-cat"><span class="nm">{area}</span><span class="score num">{f2(sc[area])}점</span></div>')
        for it in d['evaluation'][area]['항목']:
            cls, txt = GRADE_DT[it['grade']]
            if it['level'] == 'subcat-header':
                blocks.append(f'  <div class="blk dt-subcat"><div class="dt-subcat-head"><span class="nm">{it["name"]}</span><span class="dt-badge {cls}">{txt}</span></div></div>')
                continue
            nm_cls = 'nm' if it['level'] == 'factor' else 'dt-tag'
            blocks.append(f'''  <div class="blk dt-row">
    <div class="dt-row-title"><span class="{nm_cls}">{it['name']}</span><span class="dt-badge {cls}">{txt}</span></div>
{dt_body(it.get('summary',''), it.get('evidence_ids',[]))}
  </div>''')
    for name in ['답변적합도', '구체성', '본인소개']:
        blocks.append(f'  <div class="blk dt-cat"><span class="nm">{name}</span><span class="score num">{f2(sc[name])}점</span></div>')
        blocks.append(f'  <div class="blk dt-commentrow">{rule_text(name, sc[name])}</div>')
    blocks.append('  <div class="blk dt-hardcat"><span class="nm">하드스킬</span></div>')
    for h in d['hard_skills']['항목']:
        skn_cls = 'skn num' if all(ord(ch) < 128 for ch in h['name']) else 'skn'
        if h['status'] == '검출':
            lis = '\n        '.join(f'<li>{ev[str(i)]}</li>' for i in h['evidence_ids'])
            body = f'''    <div class="dt-hardrow-body">
      <div class="dt-srclabel">자기소개서 내용</div>
      <ul class="dt-list">
        {lis}
      </ul>
    </div>'''
            pill = 'yes">검출'
        else:
            body = '    <div class="dt-hardrow-empty">관련 근거 문장 없음.</div>'
            pill = 'no">미검출'
        blocks.append(f'''  <div class="blk dt-hardrow">
    <div class="dt-hardrow-title"><span class="{skn_cls}">{h['name']}</span><span class="dt-detect {pill}</span></div>
{body}
  </div>''')
    T['DT_BLOCKS'] = '\n\n'.join(blocks)

    # ── 치환 + 검증 ──
    for k, v in T.items():
        t = t.replace('{{' + k + '}}', v)
    import re
    left = re.findall(r'\{\{[A-Z_]+\}\}', t)
    if left:
        raise RuntimeError(f'{m["candidate"]}: 미치환 토큰 {set(left)}')
    return t

def main():
    for path in sorted(glob.glob(os.path.join(BASE, 'data', 'dataset-*.json'))):
        d = json.load(open(path, encoding='utf-8'))
        out = os.path.join(BASE, f'prism-한일시멘트-{d["meta"]["candidate"]}-{OUT_DATE}.html')
        open(out, 'w', encoding='utf-8').write(build(d))
        print('생성:', os.path.basename(out))

if __name__ == '__main__':
    main()
