# -*- coding: utf-8 -*-
"""BP 4.1 PDF 파서 — 5개 PDF에서 점수·GPK·역량등급(8분자)·근거문장·자소서 추출 → /tmp/parsed41.json
   입력: /tmp/a4_0N.txt (pdftotext -layout -upw 0000 산출). 사용: python3 data/parse_pdf41.py"""
import re, json, os

GMAP = {'상': '상', '중': '중', '하': '하', '-': '없음'}
SUBS = ['전략적사고', '실행력', '문제해결력', '발전가능성', '주도성', '원칙준수', '성실성', '책임감']
SUBS_RE = {'전략적사고': r'전략적\s*사고', '실행력': '실행력', '문제해결력': '문제해결력',
           '발전가능성': '발전가능성', '주도성': '주도성', '원칙준수': '원칙준수', '성실성': '성실성', '책임감': '책임감'}
ORG = ['리더십역량', '협상력', '갈등관리역량', '팀워크역량', '의사소통역량', '대인관계역량']
ORG_RE = {'리더십역량': r'리더십\s*역량', '협상력': '협상력', '갈등관리역량': r'갈등관리\s*역량',
          '팀워크역량': r'팀워크\s*역량', '의사소통역량': r'의사소통\s*역량', '대인관계역량': r'대인관계\s*역량'}

def evids(s):
    return [int(x) for x in re.findall(r'\[(\d+)\]', s)]

def grade_evi(seg, name_re):
    """name_re 뒤의 (등급)(근거) 추출. 등급: 상/중/하/-."""
    m = re.search(name_re + r'\s+(상|중|하|-)\s+((?:\[\d+\]\s*)+|-)', seg)
    if not m:
        return None
    return GMAP[m.group(1)], evids(m.group(2))

def parse(n):
    t = open(f'/tmp/a4_0{n}.txt', encoding='utf-8').read().replace('□', '℃')
    d = {'n': n}

    # ── 점수 ──
    d['bp'] = float(re.search(r'(\d+\.\d+)\s*점', t).group(1))
    sc = {}
    for lb in ['직무적합도', '조직적합도', '지원동기', '답변적합도', '구체성', '본인소개']:
        sc[lb] = float(re.search(re.escape(lb) + r'\s*\n*\s*(\d+\.\d+)', t).group(1))
    d['scores'] = sc

    # ── GPK (문항별 탐지/미탐지) — '문항 1 … 문항 2' 한 줄, 다음 줄 '탐지 탐지' ──
    g = re.search(r'문항\s*1[^\n]*문항\s*2[^\n]*\n[^\n]*?(미탐지|탐지)[^\n]*?(미탐지|탐지)', t)
    d['gpk'] = [g.group(1), g.group(2)] if g else None

    # ── 역량 등급표 ── (요약표: 직무적합도/조직적합도/지원동기 ~ '근거 문장' 마스터 전까지)
    jma_seg = re.search(r'직무적합도\s*\n+\s*항목.*?(조직적합도\s*\n+\s*항목)', t, re.S)
    org_seg = re.search(r'조직적합도\s*\n+\s*항목.*?(지원동기\s*\n+\s*항목)', t, re.S)
    mot_seg = re.search(r'지원동기\s*\n+\s*항목(.*?)(직무적합도 근거|조직적합도 근거|\Z)', t, re.S)
    jma_t = jma_seg.group(0) if jma_seg else ''
    org_t = org_seg.group(0) if org_seg else ''
    mot_t = mot_seg.group(1) if mot_seg else ''

    ev = {}
    # 직무적합도 factors
    jma = {}
    for nm, rg in [('직무경험', '직무경험'), ('직무지식', '직무지식'), ('직무동기', '직무동기')]:
        jma[nm] = grade_evi(jma_t, rg)
    jr = re.search(r'직무\s*역량\s+(상|중|하|-)', jma_t)
    jma_parent = GMAP[jr.group(1)] if jr else None
    # 직무역량 하위 (역량 영역 = 직무역량 이후)
    sub_area = jma_t[jr.end():] if jr else ''
    subs = {}
    for s in SUBS:
        m = re.search(SUBS_RE[s] + r'\s+((?:\[\d+\]\s*)+|-)', sub_area)
        subs[s] = evids(m.group(1)) if m else []
    d['jma'] = {'factors': jma, 'parent': jma_parent, 'subs': subs}
    # 조직
    org = {}
    for nm in ORG:
        org[nm] = grade_evi(org_t, ORG_RE[nm])
    d['org'] = org
    # 지원동기
    mot = {}
    for nm, rg in [('직무동기', r'직무\s*동기'), ('회사동기', r'회사\s*동기')]:
        mot[nm] = grade_evi(mot_t, rg)
    d['mot'] = mot

    # ── 근거문장 마스터 (id → 원문) ──
    lines = t.split('\n')
    master = {}
    cur = None; buf = []
    def flush():
        nonlocal cur, buf
        if cur is not None:
            master[cur] = re.sub(r'\s+', ' ', ' '.join(buf)).strip()
        cur = None; buf = []
    for ln in lines:
        m = re.match(r'\s*\[(\d+)\]\s*(.*)', ln)
        if m:
            flush(); cur = int(m.group(1)); buf = [m.group(2)]
        elif cur is not None and ln.strip() and not re.search(r'\d/\d|Copyright|서류평가|근거 문장', ln) and (len(ln) - len(ln.lstrip())) >= 2:
            buf.append(ln.strip())
        else:
            flush()
    flush()
    d['master'] = {str(k): master[k] for k in sorted(master)}

    # ── 자소서 본문 (GPT Killer 상세) — 인덱스 기반 분리 + 페이지 보일러플레이트 제거 ──
    def clean_body(s):
        out = []
        for ln in s.split('\n'):
            l = ln.strip()
            if not l:
                continue
            if re.match(r'^\d+\s*/\s*\d+$', l):
                continue
            if 'Copyright' in l or '본 결과의 평가' in l or '무단 복제' in l:
                continue
            if l == '서류평가' or l.startswith('대졸 신입') or 'GPT Killer' in l:
                continue
            out.append(l)
        return re.sub(r'\s+', ' ', ' '.join(out)).strip()
    i_start = t.find('GPT Killer 상세')
    i_q1end = t.find('있을까요?', i_start)
    i_q2 = t.find('지원한 직무를 위해 필요한 역량', i_start)
    i_q2qend = t.find('주세요.', i_q2)
    i_bp = t.find('BP평가', i_q2qend if i_q2qend > 0 else i_start)
    q1 = clean_body(t[i_q1end + len('있을까요?'):i_q2]) if i_q1end > 0 and i_q2 > 0 else ''
    q2 = clean_body(t[i_q2qend + len('주세요.'):i_bp]) if i_q2qend > 0 and i_bp > 0 else ''
    q1 = re.sub(r'\s*\d+\.?\s*$', '', q1).strip()   # 문항2 번호('2.')가 q1 끝에 딸려오는 것 제거
    d['essay'] = {'q1': q1, 'q2': q2}
    return d


def main():
    out = {}
    for n in range(1, 6):
        out[n] = parse(n)
    json.dump(out, open('/tmp/parsed41.json', 'w'), ensure_ascii=False, indent=1)

    # ── 검증 출력 ──
    for n in range(1, 6):
        d = out[n]
        print('=' * 70)
        s = d['scores']
        print(f"■ 응시자0{n}  BP {d['bp']}  GPK {d['gpk']}")
        print(f"  점수: 직무 {s['직무적합도']} 조직 {s['조직적합도']} 지원 {s['지원동기']} 답변 {s['답변적합도']} 구체 {s['구체성']} 본인 {s['본인소개']}")
        jf = d['jma']['factors']
        print(f"  [직무적합도] " + ' / '.join(f"{k} {v[0] if v else '?'}{v[1] if v else ''}" for k, v in jf.items()))
        print(f"    직무역량({d['jma']['parent']}) subs: " + ' / '.join(f"{k}{d['jma']['subs'][k]}" for k in SUBS))
        print(f"  [조직] " + ' / '.join(f"{k} {v[0] if v else '?'}{v[1] if v else ''}" for k, v in d['org'].items()))
        print(f"  [지원동기] " + ' / '.join(f"{k} {v[0] if v else '?'}{v[1] if v else ''}" for k, v in d['mot'].items()))
        mk = d['master']
        ids = sorted(int(k) for k in mk)
        contig = ids == list(range(1, max(ids) + 1)) if ids else False
        print(f"  근거문장 마스터: {len(mk)}개, id 1~{max(ids) if ids else 0}, 연속={contig}")
        print(f"  자소서: 문항1 {len(d['essay']['q1'])}자, 문항2 {len(d['essay']['q2'])}자")


if __name__ == '__main__':
    main()
