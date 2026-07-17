#!/usr/bin/env python3
"""Черновая классификация азулежу по стилю/веку/мотиву + data.js + attributions.csv."""
import json, csv, re, sys, html

meta_path, out_dir = sys.argv[1], sys.argv[2]
records = json.load(open(meta_path, encoding='utf-8'))

def year_to_cent(y):
    if y < 1600: return '15-16'
    if y < 1700: return '17'
    if y < 1800: return '18'
    if y < 1900: return '19'
    return '20-21'

def century_of(r):
    seeds = ' | '.join(r.get('seeds', []))
    if '15th-century' in seeds or '16th-century' in seeds: return '15-16'
    if '17th-century' in seeds: return '17'
    if '18th-century' in seeds: return '18'
    if '19th-century' in seeds: return '19'
    if any(s in seeds for s in ('20th-century','21st-century','Lisbon Metro')): return '20-21'
    # 'século XVII' и т.п. — в названии работы или файла
    m = re.search(r's[eé]culo\s+(XVIII|XVII|XXI|XIX|XVI|XX|XV)\b',
                  r.get('objname','') + ' ' + r['title'], re.I)
    if m:
        v = m.group(1).upper()
        return {'XV':'15-16','XVI':'15-16','XVII':'17','XVIII':'18','XIX':'19','XX':'20-21','XXI':'20-21'}[v]
    # год в названии РАБОТЫ (objname) — доверяем любому
    m = re.search(r'\b(1[5-9]\d\d|20[0-2]\d)\b', r.get('objname',''))
    if m: return year_to_cent(int(m.group(1)))
    # год в имени файла: 19xx/20xx почти всегда дата фото — берём только 1500–1899
    m = re.search(r'\b(1[5-8]\d\d)\b', r['title'])
    if m: return year_to_cent(int(m.group(1)))
    if 'Mudéjar' in seeds: return '15-16'
    return 'unknown'

def style_of(r, cent):
    seeds = ' | '.join(r.get('seeds', []))
    t = (r['title'] + ' ' + r.get('objname','')).lower()
    if 'Mudéjar' in seeds or 'hispano' in t or 'mud' in t and 'jar' in t: return 'hispano-moorish'
    if 'arte nova' in t or 'art nouveau' in t: return 'art-nouveau'
    if 'Lisbon Metro' in seeds or '21st-century' in seeds or 'metro' in t: return 'modernist'
    if '20th-century' in seeds: return 'modernist'
    if 'Blue and white' in seeds or 'azul e branco' in t: return 'blue-white'
    if 'Azulejo patterns' in seeds or 'padr' in t and ('padrão' in t or 'padrao' in t or 'pattern' in t):
        return 'pombaline' if cent in ('18','19','unknown') else 'pombaline'
    if cent == '15-16': return 'hispano-moorish' if 'geometr' in t else 'majolica'
    if cent == '17':
        return 'majolica' if any(k in t for k in ('figur','santo','senhora','retabulo','retábulo')) else 'blue-white'
    if cent == '18': return 'blue-white'
    if cent == '19': return 'art-nouveau' if 'fachada' in t or 'facade' in t else 'pombaline'
    if cent == '20-21': return 'modernist'
    return 'other'

def motif_of(r):
    seeds = ' | '.join(r.get('seeds', []))
    t = (r['title'] + ' ' + r.get('objname','')).lower()
    if 'Figuras de convite' in seeds or 'figura de convite' in t: return 'figura-de-convite'
    if 'High-relief' in seeds or 'relevo' in t: return 'relief'
    if 'Albarradas' in seeds or 'albarrada' in t: return 'floral'
    if 'Azulejo patterns' in seeds or 'padrão' in t or 'padrao' in t or 'pattern' in t or 'geometr' in t: return 'geometric'
    if 'Mudéjar' in seeds: return 'geometric'
    if any(k in t for k in ('painel','panel','retábulo','retabulo','panorama','batalha','vida de',
                            'nossa senhora','santo','são ','sao ','saint','miracle','historia','história','lenda')):
        return 'narrative-panels'
    if any(k in t for k in ('flor','floral','albarrada','vaso')): return 'floral'
    if any(k in t for k in ('figura','portrait','retrato','fernando pessoa','goethe')): return 'figurative'
    if 'train stations' in seeds or any(k in t for k in ('estação','estacao','station','igreja','church',
                                                          'palácio','palacio','fountain','chafariz','convento','mosteiro')):
        return 'narrative-panels'
    return 'other'

def nice_name(title):
    n = re.sub(r'^File:', '', title)
    n = re.sub(r'\.(jpe?g|png)$', '', n, flags=re.I)
    return n.replace('_', ' ')

tiles = []
for r in records:
    if not r.get('jname'): continue
    cent = century_of(r)
    tiles.append({
        'file': r['jname'], 'name': nice_name(r['title']),
        'artist': r.get('artist',''), 'license': r.get('license',''),
        'licurl': r.get('licurl',''), 'page': r.get('page',''),
        'date': r.get('date','')[:60],
        'style': style_of(r, cent), 'century': cent, 'motif': motif_of(r),
        'w': r['w'], 'h': r['h'],
    })

with open(f'{out_dir}/data.js', 'w', encoding='utf-8') as f:
    f.write('const TILES = ' + json.dumps(tiles, ensure_ascii=False, indent=1) + ';\n')

with open(f'{out_dir}/attributions.csv', 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w
    w.writerow(['source','page_url','author','license','license_url','filename','original_title','date'])
    for r in records:
        if not r.get('jname'): continue
        w.writerow(['Wikimedia Commons', r.get('page',''), r.get('artist',''),
                    r.get('license',''), r.get('licurl',''), r['jname'], r['title'], r.get('date','')])

from collections import Counter
print('tiles:', len(tiles))
for dim in ('style','century','motif'):
    print(dim, dict(Counter(t[dim] for t in tiles)))
