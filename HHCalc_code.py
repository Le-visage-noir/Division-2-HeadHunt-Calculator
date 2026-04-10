import string

BASE62 = string.digits + string.ascii_letters

def base62_encode_str(s: str) -> str:
    data = s.encode("utf-8")

    num = int.from_bytes(data, "big")

    if num == 0:
        return BASE62[0]

    result = ""
    while num > 0:
        num, rem = divmod(num, 62)
        result = BASE62[rem] + result

    return result

def base62_decode_str(s: str) -> str:
    num = 0
    for c in s:
        num = num * 62 + BASE62.index(c)

    length = (num.bit_length() + 7) // 8
    data = num.to_bytes(length, "big")

    return data.decode("utf-8")

def encode_base62(agent_config, query_config, fck, season_on, sb):
    raw = encode_build_v2(agent_config, query_config, fck, season_on, sb)
    return base62_encode_str(raw)

def decode_build(code):
    try:
        raw = base62_decode_str(code)
    except:
        raise ValueError("無效分享碼")

    if raw.startswith("v2|"):
        return decode_build_v2(raw)
    elif raw.startswith("v1|"):
        return ValueError("未知版本")
    else:
        raise ValueError("未知版本")

def encode_build_v2(agent_config, query_config, fck, season_on, sb):

    parts = []

    parts.append(f"a:{agent_config['agent_watch']}")
    parts.append(f"c:{['精準射手','爆破專家','其他'].index(agent_config['agent_class'])}")
    parts.append(f"w:{['1886','SR-1','白色死神','戰術.308'].index(agent_config['weapon'])}")
    parts.append(f"g:{agent_config['weapon_grade']}")
    parts.append(f"ec:{agent_config['equip_core']}")
    parts.append(f"es:{agent_config['equip_sub']}")

    parts.append(f"m:{','.join(map(str, agent_config['mods']))}")

    parts.append(f"fh:{int(query_config['filter']['first_hit']['enabled'])},{query_config['filter']['first_hit']['min']//100000}")
    parts.append(f"sh:{int(query_config['filter']['second_hit']['enabled'])},{query_config['filter']['second_hit']['min']//100000}")
    parts.append(f"ul:{int(query_config['filter']['upper_limit']['enabled'])},{query_config['filter']['upper_limit']['min']//100000}")

    parts.append(f"sk:{['first_hit','second_hit','upper_limit'].index(query_config['sort']['key'])}")
    parts.append(f"d:{int(query_config['sort']['descending'])}")
    parts.append(f"n:{query_config['top_n']}")

    parts.append(f"fck:{int(fck)}")
    parts.append(f"so:{int(season_on)}")

    parts.append(f"sb:{sb.get('HSD',0)},{sb.get('AWD',0)},{sb.get('TWD',0)}")
    

    return "v2|" + ";".join(parts)

def decode_build_v2(code):

    version, body = code.split("|", 1)

    data = {}

    for part in body.split(";"):
        k, v = part.split(":", 1)
        data[k] = v

    # ===== 解析 =====
    agent_config = {
        "agent_watch": int(data.get("a", 1000)),
        "agent_class": ["精準射手","爆破專家","其他"][int(data.get("c", 0))],
        "weapon": ["1886","SR-1","白色死神","戰術.308"][int(data.get("w", 0))],
        "weapon_grade": int(data.get("g", 0)),
        "equip_core": int(data.get("ec", 6)),
        "equip_sub": int(data.get("es", 6)),
        "mods": list(map(int, data.get("m","10,10,10").split(",")))
    }

    query_config = {
        "filter": {
            "first_hit": {
                "enabled": bool(int(data.get("fh","0,0").split(",")[0])),
                "min": int(data.get("fh","0,0").split(",")[1]) * 100000
            },
            "second_hit": {
                "enabled": bool(int(data.get("sh","0,0").split(",")[0])),
                "min": int(data.get("sh","0,0").split(",")[1]) * 100000
            },
            "upper_limit": {
                "enabled": bool(int(data.get("ul","0,0").split(",")[0])),
                "min": int(data.get("ul","0,0").split(",")[1]) * 100000
            }
        },
        "sort": {
            "key": ["first_hit","second_hit","upper_limit"][int(data.get("sk",0))],
            "descending": bool(int(data.get("d",1)))
        },
        "top_n": int(data.get("n",10))
    }

    fck = bool(int(data.get("fck",0)))
    season_on = bool(int(data.get("so",0)))

    sb_vals = list(map(int, data.get("sb","0,0,0").split(",")))
    season_bonus = {"HSD": sb_vals[0], "AWD": sb_vals[1], "TWD": sb_vals[2]}

    return agent_config, query_config, fck, season_on, season_bonus