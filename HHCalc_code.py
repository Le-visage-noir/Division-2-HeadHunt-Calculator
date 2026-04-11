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

def decode_build_redirect(code):
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

def encode_build_v2(agent_config, query_config, forcing_ck, season_on, season_bonus):

    parts = []

    # ===== agent =====
    parts.append(f"a:{agent_config['agent_watch']}")
    parts.append(f"c:{['精準射手 (爆頭傷害 15 %)','爆破專家 (對掩體外傷害 5 %)','其他'].index(agent_config['agent_class'])}")
    parts.append(f"w:{['1886','SR-1','白色死神','戰術.308'].index(agent_config['weapon'])}")
    parts.append(f"g:{agent_config['weapon_grade']}")
    parts.append(f"ec:{agent_config['equip_core']}")
    parts.append(f"es:{agent_config['equip_sub']}")

    parts.append(f"m:{','.join(map(str, agent_config['mods']))}")
    
    weapon_mod = agent_config.get("weapon_mod")
    if weapon_mod:
        wm_str = ",".join(f"{k}:{v}" for k, v in weapon_mod.items())
        parts.append(f"wm:{wm_str}")

    proto = agent_config["weapon_prototype"]
    parts.append(f"po:{int(proto['enabled'])}")

    if proto["stats"]:
        proto_str = ",".join(f"{k}:{v}" for k, v in proto["stats"].items())
        parts.append(f"ps:{proto_str}")

    # ===== filter =====
    f = query_config["filter"]

    parts.append(f"fh:{int(f['first_hit']['enabled'])},{f['first_hit']['min']}")
    parts.append(f"sh:{int(f['second_hit']['enabled'])},{f['second_hit']['min']}")
    parts.append(f"ul:{int(f['upper_limit']['enabled'])},{f['upper_limit']['min']}")

    # ===== sort =====
    parts.append(f"sk:{['first_hit','second_hit','upper_limit'].index(query_config['sort']['key'])}")
    parts.append(f"d:{int(query_config['sort']['descending'])}")
    parts.append(f"n:{query_config['top_n']}")

    # ===== flags =====
    parts.append(f"fck:{int(forcing_ck)}")
    parts.append(f"so:{int(season_on)}")

    # ===== season =====
    parts.append(f"sb:{season_bonus.get('HSD',0)},{season_bonus.get('AWD',0)},{season_bonus.get('TWD',0)}")

    raw = "v2|" + ";".join(parts)

    return base62_encode_str(raw)

def decode_build_v2(code):

    version, body = code.split("|", 1)

    data = {}

    for part in body.split(";"):
        k, v = part.split(":", 1)
        data[k] = v

    # ===== agent =====
    agent_config = {
        "agent_watch": int(data.get("a", 1000)),
        "agent_class": ['精準射手 (爆頭傷害 15 %)','爆破專家 (對掩體外傷害 5 %)','其他'][int(data.get("c", 0))],
        "weapon": ["1886","SR-1","白色死神","戰術.308"][int(data.get("w", 0))],
        "weapon_grade": int(data.get("g", 0)),
        "equip_core": int(data.get("ec", 6)),
        "equip_sub": int(data.get("es", 6)),
        "mods": list(map(float, data.get("m","10,10,10").split(",")))
    }
    
    # ===== weapon mod =====
    weapon_mod = {}
    
    if "wm" in data:
        for item in data["wm"].split(","):
            k, v = item.split(":")
            weapon_mod[k] = float(v)
            
    agent_config["weapon_mod"] = weapon_mod

    # ===== prototype =====
    proto_enabled = bool(int(data.get("po", 0)))

    proto_stats = {}
    if "ps" in data:
        for item in data["ps"].split(","):
            k, v = item.split(":")
            proto_stats[k] = float(v)

    agent_config["weapon_prototype"] = {
        "enabled": proto_enabled,
        "stats": proto_stats
    }

    # ===== filter =====
    def parse_filter(x):
        en, val = x.split(",")
        return {"enabled": bool(int(en)), "min": int(val)}
    
    query_config = {
        "filter": {
            "first_hit": parse_filter(data.get("fh","0,0")),
            "second_hit": parse_filter(data.get("sh","0,0")),
            "upper_limit": parse_filter(data.get("ul","0,0"))
        },
        "sort": {
            "key": ["first_hit","second_hit","upper_limit"][int(data.get("sk",0))],
            "descending": bool(int(data.get("d",1)))
        },
        "top_n": int(data.get("n",10))
    }

    forcing_ck = bool(int(data.get("fck",0)))
    season_on = bool(int(data.get("so",0)))

    sb = list(map(float, data.get("sb","0,0,0").split(",")))
    season_bonus = {"HSD": sb[0], "AWD": sb[1], "TWD": sb[2]}

    return agent_config, query_config, forcing_ck, season_on, season_bonus