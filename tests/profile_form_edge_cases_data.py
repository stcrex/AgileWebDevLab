"""Auto-generated edge-case rows for profile_preferences validation (do not hand-tune IDs)."""

PROFILE_FORM_EDGE_CASES = [
    # CASE-000: nominal save path
    ('ok-0',{'full_name': 'Valid User 0','uwa_id': '00100000','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-001: missing full name
    ('bad-name-1',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-002: bad UWA short digits
    ('bad-uwa-2',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-003: overlong program
    ('bad-prog-3',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-004: overlong skills
    ('bad-skills-4',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-005: nominal save path
    ('ok-5',{'full_name': 'Valid User 5','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-006: missing full name
    ('bad-name-6',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-007: bad UWA short digits
    ('bad-uwa-7',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-008: overlong program
    ('bad-prog-8',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-009: overlong skills
    ('bad-skills-9',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-010: nominal save path
    ('ok-10',{'full_name': 'Valid User 10','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-011: missing full name
    ('bad-name-11',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-012: bad UWA short digits
    ('bad-uwa-12',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-013: overlong program
    ('bad-prog-13',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-014: overlong skills
    ('bad-skills-14',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-015: nominal save path
    ('ok-15',{'full_name': 'Valid User 15','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-016: missing full name
    ('bad-name-16',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-017: bad UWA short digits
    ('bad-uwa-17',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-018: overlong program
    ('bad-prog-18',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-019: overlong skills
    ('bad-skills-19',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-020: nominal save path
    ('ok-20',{'full_name': 'Valid User 20','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-021: missing full name
    ('bad-name-21',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-022: bad UWA short digits
    ('bad-uwa-22',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-023: overlong program
    ('bad-prog-23',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-024: overlong skills
    ('bad-skills-24',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-025: nominal save path
    ('ok-25',{'full_name': 'Valid User 25','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-026: missing full name
    ('bad-name-26',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-027: bad UWA short digits
    ('bad-uwa-27',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-028: overlong program
    ('bad-prog-28',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-029: overlong skills
    ('bad-skills-29',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-030: nominal save path
    ('ok-30',{'full_name': 'Valid User 30','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-031: missing full name
    ('bad-name-31',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-032: bad UWA short digits
    ('bad-uwa-32',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-033: overlong program
    ('bad-prog-33',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-034: overlong skills
    ('bad-skills-34',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-035: nominal save path
    ('ok-35',{'full_name': 'Valid User 35','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-036: missing full name
    ('bad-name-36',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-037: bad UWA short digits
    ('bad-uwa-37',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-038: overlong program
    ('bad-prog-38',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-039: overlong skills
    ('bad-skills-39',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-040: nominal save path
    ('ok-40',{'full_name': 'Valid User 40','uwa_id': '00100040','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-041: missing full name
    ('bad-name-41',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-042: bad UWA short digits
    ('bad-uwa-42',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-043: overlong program
    ('bad-prog-43',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-044: overlong skills
    ('bad-skills-44',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-045: nominal save path
    ('ok-45',{'full_name': 'Valid User 45','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-046: missing full name
    ('bad-name-46',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-047: bad UWA short digits
    ('bad-uwa-47',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-048: overlong program
    ('bad-prog-48',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-049: overlong skills
    ('bad-skills-49',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-050: nominal save path
    ('ok-50',{'full_name': 'Valid User 50','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-051: missing full name
    ('bad-name-51',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-052: bad UWA short digits
    ('bad-uwa-52',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-053: overlong program
    ('bad-prog-53',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-054: overlong skills
    ('bad-skills-54',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-055: nominal save path
    ('ok-55',{'full_name': 'Valid User 55','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-056: missing full name
    ('bad-name-56',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-057: bad UWA short digits
    ('bad-uwa-57',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-058: overlong program
    ('bad-prog-58',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-059: overlong skills
    ('bad-skills-59',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-060: nominal save path
    ('ok-60',{'full_name': 'Valid User 60','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-061: missing full name
    ('bad-name-61',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-062: bad UWA short digits
    ('bad-uwa-62',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-063: overlong program
    ('bad-prog-63',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-064: overlong skills
    ('bad-skills-64',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-065: nominal save path
    ('ok-65',{'full_name': 'Valid User 65','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-066: missing full name
    ('bad-name-66',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-067: bad UWA short digits
    ('bad-uwa-67',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-068: overlong program
    ('bad-prog-68',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-069: overlong skills
    ('bad-skills-69',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-070: nominal save path
    ('ok-70',{'full_name': 'Valid User 70','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-071: missing full name
    ('bad-name-71',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-072: bad UWA short digits
    ('bad-uwa-72',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-073: overlong program
    ('bad-prog-73',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-074: overlong skills
    ('bad-skills-74',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
    # CASE-075: nominal save path
    ('ok-75',{'full_name': 'Valid User 75','uwa_id': '','program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'purple',},(),),
    # CASE-076: missing full name
    ('bad-name-76',{'full_name': '', 'uwa_id': '', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'blue'},('full_name',),),
    # CASE-077: bad UWA short digits
    ('bad-uwa-77',{'full_name': 'X', 'uwa_id': '12', 'program': '', 'bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'green'},('uwa_id',),),
    # CASE-078: overlong program
    ('bad-prog-78',{'full_name': 'Y', 'uwa_id': '','program': 'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP','bio': '', 'skills': '', 'availability': '', 'avatar_colour': 'teal'},('program',),),
    # CASE-079: overlong skills
    ('bad-skills-79',{'full_name': 'Z', 'uwa_id': '', 'program': '', 'bio': '','skills': 'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS','availability': '', 'avatar_colour': 'orange'},('skills',),),
]

