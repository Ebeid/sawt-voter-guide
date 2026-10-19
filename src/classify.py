"""Tag each contest with ballot-order rank, district family and jurisdiction."""
import re

# ---- ballot-order categories (lower = earlier on the ballot) ----
CAT = {
    'fed_sen': 10, 'fed_house': 11,
    'exec': 20, 'court_high': 38, 'boe_state': 36,
    'leg_sen': 30, 'leg_house': 31,
    'court_app': 41, 'court_local': 45, 'exec_np': 46,
    'co_exec': 50, 'co_board': 51, 'co_row': 52, 'co_school': 53,
    'city': 60, 'school': 70, 'college': 71, 'special': 75,
    'm_state': 90, 'm_county': 91, 'm_city': 92, 'm_school': 93,
}
GROUP = {
    'fed_sen': 'fed', 'fed_house': 'fed', 'exec': 'state', 'court_high': 'state', 'boe_state': 'state',
    'leg_sen': 'leg', 'leg_house': 'leg', 'court_app': 'jud', 'court_local': 'jud', 'exec_np': 'state',
    'co_exec': 'county', 'co_board': 'county', 'co_row': 'county', 'co_school': 'school',
    'city': 'city', 'school': 'school', 'college': 'school', 'special': 'special',
    'm_state': 'meas', 'm_county': 'meas', 'm_city': 'meas', 'm_school': 'meas',
}
EXEC_ORDER = {
    '_': ['Governor', 'Lieutenant Governor', 'Secretary of State', 'Attorney General', 'Comptroller',
          'State Controller', 'Treasurer', 'State Auditor', 'Auditor', 'Insurance Commissioner',
          'Commissioner of Agriculture', 'Railroad Commissioner', 'Public Service Commission',
          'Board of Equalization', 'State Superintendent'],
    'CA': ['Governor', 'Lieutenant Governor', 'Secretary of State', 'State Controller', 'Treasurer',
           'Attorney General', 'Insurance Commissioner', 'Board of Equalization'],
    'OH': ['Governor', 'Attorney General', 'Auditor', 'Secretary of State', 'Treasurer'],
    'TX': ['Governor', 'Lieutenant Governor', 'Attorney General', 'Comptroller',
           'Commissioner of Agriculture', 'Railroad Commissioner'],
}
STATEWIDE_FIRST = {'CA', 'MI', 'OH'}  # these ballots open with Governor, then federal

LEG_FAMS = ('State Senate', 'State House', 'State Assembly', 'House of Delegates')
DIST_RE = re.compile(r'^(.*?),\s*((?:Trustee Area|Supervisorial District|District|Ward|Area|Zone|Division|Precinct|LD)\b.*)$')

# ---- city -> counties ----
CITY_COUNTY = {
    'CA': {
        'Anaheim': ['Orange'], 'Antioch': ['Contra Costa'], 'Bakersfield': ['Kern'], 'Banning': ['Riverside'],
        'Berkeley': ['Alameda'], 'Burbank': ['Los Angeles'], 'Citrus Heights': ['Sacramento'],
        'Concord': ['Contra Costa'], 'Costa Mesa': ['Orange'], 'Cudahy': ['Los Angeles'],
        'Daly City': ['San Mateo'], 'Dublin': ['Alameda'], 'East Palo Alto': ['San Mateo'],
        'El Cajon': ['San Diego'], 'Elk Grove': ['Sacramento'], 'Folsom': ['Sacramento'],
        'Foster City': ['San Mateo'], 'Fremont': ['Alameda'], 'Fresno': ['Fresno'], 'Fullerton': ['Orange'],
        'Gilroy': ['Santa Clara'], 'Hayward': ['Alameda'], 'Irvine': ['Orange'], 'Los Angeles': ['Los Angeles'],
        'Milpitas': ['Santa Clara'], 'Morgan Hill': ['Santa Clara'], 'Mountain View': ['Santa Clara'],
        'Newark': ['Alameda'], 'Oakland': ['Alameda'], 'Pacifica': ['San Mateo'], 'Pleasanton': ['Alameda'],
        'Redwood City': ['San Mateo'], 'Richmond': ['Contra Costa'], 'Riverside': ['Riverside'],
        'San Bernardino': ['San Bernardino'], 'San Diego': ['San Diego'], 'San Jose': ['Santa Clara'],
        'San Ramon': ['Contra Costa'], 'Santa Ana': ['Orange'], 'Santa Clara': ['Santa Clara'],
        'Santa Cruz': ['Santa Cruz'], 'Stanton': ['Orange'], 'Tracy': ['San Joaquin'],
        'Union City': ['Alameda'], 'Victorville': ['San Bernardino'], 'Vista': ['San Diego'],
        'Walnut Creek': ['Contra Costa'], 'West Hollywood': ['Los Angeles'],
    },
    'TX': {'Austin': ['Travis', 'Williamson', 'Hays']},
    'MI': {'Ann Arbor': ['Washtenaw'], 'Dearborn Heights': ['Wayne']},
    'NC': {'Raleigh': ['Wake', 'Durham']},
    'NJ': {'Piscataway': ['Middlesex']},
    'RI': {'Providence': ['Providence']},
    'VA': {'Roanoke': ['@Roanoke city']},
}

HOU = ['Austin', 'Brazoria', 'Chambers', 'Colorado', 'Fort Bend', 'Galveston', 'Grimes', 'Harris', 'Waller', 'Washington']
AUS = ['Bastrop', 'Bell', 'Blanco', 'Burnet', 'Caldwell', 'Coke', 'Comal', 'Concho', 'Fayette', 'Hays', 'Irion',
       'Lampasas', 'Lee', 'Llano', 'McCulloch', 'Milam', 'Mills', 'Runnels', 'San Saba', 'Schleicher', 'Sterling',
       'Tom Green', 'Travis', 'Williamson']
DAL = ['Collin', 'Dallas', 'Grayson', 'Hunt', 'Kaufman', 'Rockwall']

# (substring in office/locality, display name, counties, jurisdiction type, category or None)
BODY = {
    'CA': [
        ('Fremont Union High School District', 'Fremont Union High School District', ['Santa Clara'], 'sc', 'school'),
        ('West Valley-Mission Community College', 'West Valley-Mission Community College District', ['Santa Clara'], 'sc', 'college'),
        ('Gavilan College', 'Gavilan Joint Community College District', ['Santa Clara', 'San Benito'], 'sc', 'college'),
        ('Los Angeles Community College District', 'Los Angeles Community College District', ['Los Angeles'], 'sc', 'college'),
        ('Los Rios Community College', 'Los Rios Community College District', ['Sacramento', 'El Dorado', 'Placer', 'Yolo'], 'sc', 'college'),
        ('Contra Costa Community College', 'Contra Costa Community College District', ['Contra Costa'], 'co', 'college'),
        ('Ohlone Community College', 'Ohlone Community College District', ['Alameda'], 'sc', 'college'),
        ('City College of San Francisco', 'City College of San Francisco', ['San Francisco'], 'co', 'college'),
        ('North Orange County Community College', 'North Orange County Community College District', ['Orange'], 'sc', 'college'),
        ('State Center Community College', 'State Center Community College District', ['Fresno', 'Madera', 'Kings', 'Tulare'], 'sc', 'college'),
        ('Anaheim Elementary', 'Anaheim Elementary School District', ['Orange'], 'sc', 'school'),
        ('Antioch Unified', 'Antioch Unified School District', ['Contra Costa'], 'sc', 'school'),
        ('Berryessa Union', 'Berryessa Union School District', ['Santa Clara'], 'sc', 'school'),
        ('Central Unified', 'Central Unified School District', ['Fresno'], 'sc', 'school'),
        ('Dublin Unified', 'Dublin Unified School District', ['Alameda'], 'sc', 'school'),
        ('East Side Union', 'East Side Union High School District', ['Santa Clara'], 'sc', 'school'),
        ('Evergreen Elementary', 'Evergreen Elementary School District', ['Santa Clara'], 'sc', 'school'),
        ('Franklin-McKinley', 'Franklin-McKinley School District', ['Santa Clara'], 'sc', 'school'),
        ('Gilroy Unified', 'Gilroy Unified School District', ['Santa Clara'], 'sc', 'school'),
        ('Morgan Hill Unified', 'Morgan Hill Unified School District', ['Santa Clara'], 'sc', 'school'),
        ('Natomas Unified', 'Natomas Unified School District', ['Sacramento'], 'sc', 'school'),
        ('New Haven Unified', 'New Haven Unified School District', ['Alameda'], 'sc', 'school'),
        ('Oakland Unified', 'Oakland Unified School District', ['Alameda'], 'sc', 'school'),
        ('Sacramento City Unified', 'Sacramento City Unified School District', ['Sacramento'], 'sc', 'school'),
        ('San Francisco Unified', 'San Francisco Unified School District', ['San Francisco'], 'co', 'school'),
        ('San Jose Unified', 'San Jose Unified School District', ['Santa Clara'], 'sc', 'school'),
        ('San Juan Unified', 'San Juan Unified School District', ['Sacramento'], 'sc', 'school'),
        ('Santa Ana Unified', 'Santa Ana Unified School District', ['Orange'], 'sc', 'school'),
        ('Santa Clara Unified', 'Santa Clara Unified School District', ['Santa Clara'], 'sc', 'school'),
        ('Torrance Unified', 'Torrance Unified School District', ['Los Angeles'], 'sc', 'school'),
        ('Vista Unified', 'Vista Unified School District', ['San Diego'], 'sc', 'school'),
        ('Los Angeles Unified', 'Los Angeles Unified School District', ['Los Angeles'], 'sc', 'school'),
        ('East Bay Regional Park', 'East Bay Regional Park District', ['Alameda', 'Contra Costa'], 'co', 'special'),
        ('AC Transit', 'AC Transit', ['Alameda', 'Contra Costa'], 'sp', 'special'),
        ('Alameda County Water District', 'Alameda County Water District', ['Alameda'], 'sp', 'special'),
        ('Ramona Municipal Water', 'Ramona Municipal Water District', ['San Diego'], 'sp', 'special'),
        ('Rincon Del Diablo', 'Rincon Del Diablo Municipal Water District', ['San Diego'], 'sp', 'special'),
        ('Deer Springs Fire', 'Deer Springs Fire Protection District', ['San Diego'], 'sp', 'special'),
        ('North County Fire', 'North County Fire Protection District', ['San Diego'], 'sp', 'special'),
        ('Tri-City Healthcare', 'Tri-City Healthcare District', ['San Diego'], 'sp', 'special'),
        ('Ramona Community Planning', 'Ramona Community Planning Group', ['San Diego'], 'sp', 'special'),
        ('Sweetwater Community Planning', 'Sweetwater Community Planning Group', ['San Diego'], 'sp', 'special'),
        ('San Francisco Supervisor', None, ['San Francisco'], 'co', 'co_board'),
    ],
    'TX': [
        ('Austin ISD', 'Austin ISD', ['Travis'], 'sc', 'school'),
        ('Del Valle ISD', 'Del Valle ISD', ['Travis'], 'sc', 'school'),
        ('Fort Bend ISD', 'Fort Bend ISD', ['Fort Bend'], 'sc', 'school'),
        ('Keller ISD', 'Keller ISD', ['Tarrant'], 'sc', 'school'),
        ('Leander ISD', 'Leander ISD', ['Williamson', 'Travis'], 'sc', 'school'),
        ('Pflugerville ISD', 'Pflugerville ISD', ['Travis', 'Williamson'], 'sc', 'school'),
        ('Princeton ISD', 'Princeton ISD', ['Collin'], 'sc', 'school'),
        ('Round Rock ISD', 'Round Rock ISD', ['Williamson', 'Travis'], 'sc', 'school'),
        ('Tomball ISD', 'Tomball ISD', ['Harris', 'Montgomery'], 'sc', 'school'),
        ('Wylie ISD', 'Wylie ISD', ['Collin', 'Dallas'], 'sc', 'school'),
        ('Fort Bend Central Appraisal', None, ['Fort Bend'], 'co', 'special'),
        ('263rd Criminal District Court', None, ['Harris'], 'co', 'court_local'),
        ('328th District Court', None, ['Fort Bend'], 'co', 'court_local'),
        ('15th Court of Appeals', None, None, 'st', 'court_app'),
        ('14th Court of Appeals', None, HOU, 'rg', 'court_app'),
        ('1st Court of Appeals', None, HOU, 'rg', 'court_app'),
        ('3rd Court of Appeals', None, AUS, 'rg', 'court_app'),
        ('5th Court of Appeals', None, DAL, 'rg', 'court_app'),
    ],
    'MI': [
        ('Oakland Community College', 'Oakland Community College', ['Oakland'], 'sc', 'college'),
        ('Ann Arbor Public Schools', 'Ann Arbor Public Schools', ['Washtenaw'], 'sc', 'school'),
        ('Crestwood School Board', 'Crestwood School District', ['Wayne'], 'sc', 'school'),
        ('Dearborn Board of Education', 'Dearborn Public Schools', ['Wayne'], 'sc', 'school'),
        ('Plymouth-Canton', 'Plymouth-Canton Community Schools', ['Wayne'], 'sc', 'school'),
    ],
    'MN': [('Minneapolis Board of Education', 'Minneapolis Public Schools', ['Hennepin'], 'sc', 'school')],
    'NC': [
        ('Alamance-Burlington', 'Alamance-Burlington Schools', ['Alamance'], 'sc', 'school'),
        ('District Court Judge, District 10', None, ['Wake'], 'co', 'court_local'),
    ],
    'MO': [('Associate Circuit Judge, Circuit 21', None, ['St. Louis'], 'co', 'court_local')],
}

MEASURE_LOC = {
    'CA': {
        'Berkeley': ('ci', 'Berkeley'), 'Irvine': ('ci', 'Irvine'), 'Los Angeles': ('ci', 'Los Angeles'),
        'Oakland': ('ci', 'Oakland'), 'Walnut Creek': ('ci', 'Walnut Creek'),
        'Los Angeles County': ('co', ['Los Angeles']), 'San Francisco': ('co', ['San Francisco']),
        'San Mateo County': ('co', ['San Mateo']),
        'Los Angeles Unified School District': ('sc', 'Los Angeles Unified'),
    }
}

LOCAL_CATS = [
    ('co_row', ['Clerk of Superior Court', 'District Attorney', 'County Attorney', 'County Clerk', 'District Clerk',
                'Sheriff', 'County Treasurer', 'Assessor', 'Tax Assessor']),
    ('court_local', ['Superior Court', 'District Court', 'Court at Law', 'Criminal Court', 'Probate Court',
                     'Justice of the Peace', 'Associate Circuit Judge']),
    ('co_exec', ['County Judge', 'County Executive', 'Commission Chair']),
    ('co_board', ['Board of Supervisors', 'County Supervisor', 'County Commissioner', 'County Council',
                  'County Legislature', 'Board of Commissioners']),
    ('co_school', ['County Board of Education', 'Dept. of Education Trustee']),
    ('city', ['Mayor', 'City Attorney', 'City Council', 'Township Council', 'Charter Commission', 'Rent Stabilization']),
    ('college', ['College']),
    ('school', ['School', 'ISD', 'Unified', 'Board of Education', 'Public Schools']),
    ('special', ['Park District', 'Transit', 'Water District', 'Fire Protection', 'Healthcare District',
                 'Planning Group', 'Appraisal District']),
]


def county_name(st, c):
    if c.startswith('@'):
        return c[1:]
    return c + ' County'


def city_of(office):
    for pat in [r'^(.*?) City Council', r'^(.*?) Mayor$', r'^(.*?) City Attorney', r'^(.*?) Rent Stabilization',
                r'^(.*?) Charter Commission', r'^(.*?) Township Council']:
        m = re.match(pat, office)
        if m:
            c = m.group(1)
            return {'Union': 'Union City', 'Redwood': 'Redwood City', 'Foster': 'Foster City'}.get(c, c)
    return None


def county_from_office(office):
    m = re.search(r'\(([^)]+?) County\)', office)
    if m:
        return m.group(1)
    m = re.match(r'^(.+?) County\b', office)
    if m:
        return m.group(1)
    return None


def split_district(sec, office):
    if sec == 'F' and office.startswith('U.S. House'):
        return 'U.S. House', office.split(', ', 1)[1]
    fam = office.split(',', 1)[0]
    if sec == 'S' and ',' in office and (fam in LEG_FAMS or fam in ('Board of Equalization', 'State Board of Education')):
        return fam, office.split(', ', 1)[1]
    m = DIST_RE.match(office)
    if m and sec != 'S' and not office.startswith('District Court Judge'):
        return m.group(1), m.group(2)
    return office, ''


def exec_rank(st, office):
    order = EXEC_ORDER.get(st, EXEC_ORDER['_'])
    for i, name in enumerate(order):
        if office == name or office.startswith(name + ','):
            return i
    for i, name in enumerate(EXEC_ORDER['_']):
        if office == name or office.startswith(name):
            return 20 + i
    return None


def classify(st, it):
    """Return metadata dict for one item (candidate row or measure)."""
    sec = it[0]
    meta = {'b': '', 'y': '', 'c': [], 'j': 'st'}
    if sec == 'M':
        title, status, loc = it[1], it[2], it[3]
        meta.update(f=title, d='')
        if 'statewide' in loc:
            cat = 'm_state'
        else:
            kind, val = MEASURE_LOC[st][loc]
            if kind == 'ci':
                cat = 'm_city'; meta.update(j='ci', y=val, c=[county_name(st, x) for x in CITY_COUNTY[st][val]])
            elif kind == 'co':
                cat = 'm_county'; meta.update(j='co', c=[county_name(st, x) for x in val])
            else:
                cat = 'm_school'
                body = next(b for b in BODY[st] if b[0] == val)
                meta.update(j='sc', b=body[1], c=[county_name(st, x) for x in body[2]])
        meta.update(cat=cat)
        return finish(st, meta, it)

    office = it[2]
    fam, dist = split_district(sec, office)
    meta.update(f=fam, d=dist)
    cat = None
    # explicit body rules first
    for pat, disp, cos, jt, bcat in BODY.get(st, []):
        if pat in office:
            cat = bcat
            meta['j'] = jt
            if cos:
                meta['c'] = [county_name(st, x) for x in cos]
            if jt in ('sc', 'sp'):
                meta['b'] = disp
            break
    if sec == 'F':
        cat = 'fed_sen' if office.startswith('U.S. Senate') else 'fed_house'
    elif sec == 'S' and cat is None:
        if fam in ('State Senate',):
            cat = 'leg_sen'
        elif fam in LEG_FAMS:
            cat = 'leg_house'
        elif 'Court of Appeals' in office:
            cat = 'court_app'
        elif 'Supreme Court' in office or 'Court of Criminal Appeals' in office:
            cat = 'court_high'
        elif 'Board of Education' in office or 'Regents' in office or 'Board of Governors' in office:
            cat = 'boe_state'
        elif office == 'State Superintendent':
            cat = 'exec_np' if st == 'CA' else 'exec'
        elif exec_rank(st, office) is not None:
            cat = 'exec'
        else:
            raise ValueError(f'unclassified state office {st}: {office}')
    elif sec == 'L':
        if cat is None:
            for c, kws in LOCAL_CATS:
                if any(k in office for k in kws):
                    cat = c
                    break
        if cat is None:
            raise ValueError(f'unclassified local office {st}: {office}')
        if not meta['c']:
            city = city_of(office)
            if cat == 'city' and city:
                meta.update(j='ci', y=city, c=[county_name(st, x) for x in CITY_COUNTY[st][city]])
            else:
                co = county_from_office(office)
                if not co:
                    raise ValueError(f'no county for {st}: {office}')
                meta.update(j='co', c=[county_name(st, co)])
        if cat == 'city' and not meta['y']:
            city = city_of(office)
            meta.update(j='ci', y=city, c=[county_name(st, x) for x in CITY_COUNTY[st][city]])
    meta['cat'] = cat
    return finish(st, meta, it)


def finish(st, meta, it):
    cat = meta['cat']
    r = CAT[cat]
    if cat == 'exec':
        r += (exec_rank(st, it[2]) or 0) / 100
        if st in STATEWIDE_FIRST:
            r = 5 + (r - 20)
    if cat == 'boe_state' and st in STATEWIDE_FIRST:
        r = 32  # after the legislature on CA/MI/OH ballots
    if cat == 'city':
        o = it[2] if it[0] != 'M' else ''
        r += 0.0 if o.endswith('Mayor') else 0.01 if 'Attorney' in o else 0.02 if 'Council' in o else 0.03
    if st == 'TX' and cat == 'court_high':
        r = 22
    if st == 'TX' and cat == 'boe_state':
        r = 23
    meta['r'] = round(r, 2)
    meta['g'] = GROUP[cat]
    return meta
