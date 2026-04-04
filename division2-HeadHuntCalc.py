import math
from itertools import product
from collections import Counter

# =========================================================
# 【0】基礎配裝區 (包含武器 + 特化職業選擇，以及篩選及排序條件)
# =========================================================

agent_config = {
    "agent_watch": 1000,       # 手錶等級(預設武器傷害及爆頭傷害全滿)
    "agent_class": "精準射手",  # 精準射手提供爆頭傷害、爆破專家提供掩體外傷害，其他特化職業不影響堅定獵頭傷害計算
    "weapon": "1886",          # 目前可選用 1886, SR-1, 白色死神, 戰術.308
    "weapon_grade": 15,        # 武器專精等級
    "equip_core": 6,           # 裝備詞條當中 "武器傷害"(預設滿數值) 的數量
    "equip_sub": 6,            # 裝備詞條當中 "爆頭傷害"(預設滿數值) 的數量、"昏頭脹腦" 也計入此項
    "mods": [10, 10, 10]       # 裝備模組，可填寫 "爆頭傷害 10 %" 或是數字
}

Forcing_Chest_ChainKiller = False # 是否強制綁定連環殺手

Activate_Sesonal_Modifier = False # 是否啟用賽季修改器

query_config = {
    "filter": {
        "first_hit": {
            "enabled": False,  # 依據第一擊傷害作為篩選門檻
            "min": 6_360_822   # 單人 + 英雄難度，一般老練敵人(紫怪)
        },
        "second_hit": {
            "enabled": False,  # 依據第二擊傷害作為篩選門檻
            "min": 14_752_327  # 單人 + 傳奇難度，一般菁英敵人(金怪)
        },
        "upper_limit": {
            "enabled": False,  # 依據傷害上限作為篩選門檻
            "min": 25_172_179  # 四人 + 傳奇難度，一般菁英敵人(金怪)
        }
    },
    "sort": {
        "key": "first_hit",    # 可依據 first_hit / second_hit / upper_limit 進行排序
        "descending": True     # 由高到低進行排序
    },
    "top_n": 10                # 列出的配裝數量
}


# =========================================================
# 【1】裝備資料區（👉未來若有新裝備/武器，在這裡改）
# 裝備格式：(裝備名稱, 品牌, {額外詞條(可選)})
# 武器格式："名稱": "種類"
# =========================================================

mask     = [("昏頭脹腦","道格",{"HSD":10}), ("臨界","臨界"), ("茲維","茲維"), ("天命","天命"), ("哈布斯","哈布斯"), ("頂專","頂專"), ("阿爾拉蒂","阿爾拉蒂")]
backpack = [("禮物","天命",{"TWD":25}), ("茲維(警戒)","茲維",{"TWD":25}), ("哈布斯(警戒)","哈布斯",{"TWD":25}), ("阿爾拉蒂(警戒)","阿爾拉蒂",{"TWD":25})]
chest    = [("連環殺手","沃克"), ("茲維(獵頭)","茲維"), ("天命(獵頭)","天命"), ("哈布斯(獵頭)","哈布斯"), ("阿爾拉蒂(獵頭)","阿爾拉蒂")]
glove    = [("雄鷹爪擊","茲維"), ("臨界","臨界"), ("天命","天命"), ("哈布斯","哈布斯"), ("頂專","頂專"), ("阿爾拉蒂","阿爾拉蒂")]
holster  = [("臨界","臨界"), ("茲維","茲維"), ("天命","天命"), ("哈布斯","哈布斯"), ("頂專","頂專"), ("阿爾拉蒂","阿爾拉蒂")]
knee     = [("散兵坑禱詞","霸主",{"DTTOOC":8}), ("臨界","臨界"), ("茲維","茲維"), ("天命","天命"), ("哈布斯","哈布斯"), ("頂專","頂專"), ("阿爾拉蒂","阿爾拉蒂")]

all_parts = [mask, backpack, chest, glove, holster, knee]

WEAPON_TYPE_MAP = {
    "1886": "rifle",
    "SR-1": "marksman",
    "白色死神": "marksman",
    "戰術.308": "marksman",
}


# =========================================================
# 【2】品牌限制條件（僅列出合理配裝）
# =========================================================
def is_valid_build(combo, Forcing_Chest_ChainKiller):
    brands = [item[1] for item in combo]
    count = Counter(brands)

    # ---- 臨界：2~3 或 0 ----
    if not (count["臨界"] == 0 or 2 <= count["臨界"] <= 3):
        return False

    # ---- 茲維：最多2 ----
    if count["茲維"] > 2:
        return False

    # ---- 天命：最多1 ----
    if count["天命"] > 1:
        return False

    # ---- 哈布斯：最多2 ----
    if count["哈布斯"] > 2:
        return False
    
    # ---- 頂專：2~3 或 0 ----
    if not (count["頂專"] == 0 or 2 <= count["頂專"] <= 3):
        return False

    # ---- 阿爾拉蒂：最多2 ----
    if count["阿爾拉蒂"] > 2:
        return False
    
    # ---- 沃克：是否綁定連環殺手 ----
    if Forcing_Chest_ChainKiller == True and count["沃克"] < 1:
        return False

    return True


# =========================================================
# 【3】「基礎數值來源」
# =========================================================

def init_stats():
    return {
        "BASE": 0,       # 基礎傷害
        "AWD": 0,        # 武器傷害
        "WD_rifle":0,    # 步槍傷害
        "WD_marksman":0, # 射手步槍傷害
        "TWD": 0,        # 總武器傷害
        "HSD": 0,        # 爆頭傷害
        "DTTOOC": 0,     # 對掩體外目標傷害
        "OTHER": 0
    }

# ✔ 手錶等級
def watch_max_level(stats, agent_watch):
    if agent_watch >= 1000:
        stats["AWD"] += 10
        stats["HSD"] += 20
    else:
        stats["AWD"] += 0
        stats["HSD"] += 0
    return stats

# ✔ 特化職業
def specialization(stats, agent_class):
    stats["WD_rifle"] += 15    # 共通加成
    stats["WD_marksman"] += 15 # 共通加成
    if agent_class == "精準射手":
        stats["HSD"] += 15
    elif agent_class == "爆破專家":
        stats["DTTOOC"] += 5
    return stats

# ✔ 武器數值
def weapon_stats(stats, weapon):
    stats["DTTOOC"] += 10          # 隨機詞條統一掩體外傷害
    if weapon == "1886":
        stats["BASE"] = 386892
        stats["WD_rifle"] += 15    # 核心屬性 (預設滿數值)
        stats["HSD"] += 60         # 槍種基礎數值
    elif weapon == "SR-1":
        stats["BASE"] = 409255
        stats["WD_marksman"] += 15 # 核心屬性 (預設滿數值)
        stats["HSD"] += 0          # 槍種基礎數值
        stats["HSD"] += 111        # 核心屬性 (預設滿數值)
        stats["HSD"] += 10         # 武器模組 (預設不開鏡)
    elif weapon == "白色死神":
        stats["BASE"] = 433563
        stats["WD_marksman"] += 15 # 核心屬性 (預設滿數值)
        stats["HSD"] += 0          # 槍種基礎數值
        stats["HSD"] += 137        # 核心屬性
        stats["HSD"] += 10         # 武器模組 (預設不開鏡)
    elif weapon == "戰術.308":
        stats["BASE"] = 403709
        stats["WD_marksman"] += 15 # 核心屬性 (預設滿數值)
        stats["HSD"] += 0          # 槍種基礎數值
        stats["HSD"] += 111        # 核心屬性 (預設滿數值)
        stats["HSD"] += 10         # 武器模組 (預設不開鏡)
    return stats

# ✔ 武器數值 (判斷適用 WD 種類)
def finalize_stats(stats, config):
    """
    ⭐ 將所有分散數值整理成最終 stats
    這裡會寫回 stats["WD_effective"]
    """

    weapon = config["weapon"]
    weapon_type = WEAPON_TYPE_MAP.get(weapon)

    if weapon_type is None:
        raise ValueError(f"未支援的武器: {weapon}")

    # 取得對應 WD
    weapon_key = f"WD_{weapon_type}"

    # ⭐ 合成 WD_effective（寫回 stats）
    stats["WD_effective"] = stats["AWD"] + stats.get(weapon_key, 0)

    return stats

# ✔ 武器專精
def weapon_expertise(stats, weapon_grade):
    stats["AWD"] += weapon_grade
    return stats

# ✔ 裝備核心屬性 (預設 6 紅 + 滿數值)
def equip_main(stats, equip_core):
    stats["AWD"] += 15 * 6
    return stats

# ✔ 裝備隨機詞條 (預設 6 爆頭傷害 10 %)
def equip_minor(stats, equip_sub):
    stats["HSD"] += 10 * 6
    return stats

# ✔ 裝備模組 (預設 3 個)
def equip_mods(stats, mods):
    for mod in mods:
        if mod == "爆頭傷害 10 %":
            stats["HSD"] += 10
        elif isinstance(mod, (int, float)):
            stats["HSD"] += mod
        elif mod == "其他":
            stats["HSD"] += 0
    return stats

# ✔ 賽季修改器 (預設關閉)
def get_season_bonus():
    """
    從終端讀取賽季加成，回傳 dict
    """
    bonus = {}

    print("格式: 屬性 數值 (例如: HSD 15)")
    print("輸入 done 結束\n")

    while True:
        user_input = input("請輸入: ").strip()

        if user_input.lower() == "done":
            break

        if not user_input:
            continue

        parts = user_input.split()

        if len(parts) != 2:
            print("❌ 格式錯誤")
            continue

        key, value = parts

        try:
            value = float(value)
        except ValueError:
            print("❌ 數值錯誤")
            continue

        # 累加（允許同一屬性輸入多次）
        bonus[key] = bonus.get(key, 0) + value

        print(f"✅ 已加入: {key} +{value}")

    print("=== 賽季修改器輸入完成 ===\n")

    return bonus

def apply_season_bonus(stats, bonus):
    for k, v in bonus.items():
        if k in stats:
            stats[k] += v
        else:
            print(f"⚠️ 忽略未知屬性: {k}")
    return stats

if Activate_Sesonal_Modifier == True:
    print("\n=== 賽季修改器啟用中 ===")
    season_bonus = get_season_bonus()

# 整合所有「基礎數值來源」 (👉 上述的數值來源都在這裡集中處理)
def build_base_stats(config):

    stats = init_stats()

    stats = watch_max_level(stats, config["agent_watch"])
    stats = specialization(stats, config["agent_class"])
    stats = weapon_stats(stats, config["weapon"])
    stats = weapon_expertise(stats, config["weapon_grade"])
    stats = equip_main(stats, config["equip_core"])
    stats = equip_minor(stats, config["equip_sub"])
    stats = equip_mods(stats, config["mods"])

    return stats


# =========================================================
# 【4】品牌效果
# =========================================================
def apply_brand_effects(brand_count, stats):

    # ---- 臨界 ----
    c = brand_count["臨界"]
    if c >= 2:
        stats["WD_rifle"] += 25
        stats["WD_marksman"] += 25
    if c >= 3:
        stats["HSD"] += 30

    # ---- 茲維 ----
    c = brand_count["茲維"]
    if c >= 2:
        stats["WD_rifle"] += 20

    # ---- 天命 ----
    c = brand_count["天命"]
    if c >= 1:
        stats["HSD"] += 13

    # ---- 哈布斯 ----
    c = brand_count["哈布斯"]
    if c >= 1:
        stats["HSD"] += 13
    if c >= 2:
        stats["WD_marksman"] += 20

    # ---- 頂專 ----
    c = brand_count["頂專"]
    if c >= 2:
        stats["WD_marksman"] += 30
    if c >= 3:
        stats["HSD"] += 30

    # ---- 阿爾拉蒂 ----
    c = brand_count["阿爾拉蒂"]
    if c >= 1:
        stats["WD_marksman"] += 10
    if c >= 2:
        stats["HSD"] += 13

    # ---- 其他品牌 ----
    c = brand_count["沃克"]
    if c >= 1:
        stats["AWD"] += 5
    
    c = brand_count["霸主"]
    if c >= 1:
        stats["WD_rifle"] += 10

    return stats


# =========================================================
# 【5】單件裝備詞條
# =========================================================
def apply_item_stats(combo, stats):
    for item in combo:
        if len(item) >= 3:
            extra = item[2]
            for k, v in extra.items():
                stats[k] += v
    return stats


# =========================================================
# 【6】獵頭者傷害模型
# =========================================================

def get_chest_multiplier(combo):
    """
    根據裝備判斷倍率
    """

    chest_item = combo[2][0]   # 第 3 個是 chest

    if chest_item == "連環殺手":
        return 1.5
    else:
        return 1.25

def calc_damage(stats, combo, max_hits=10):
    """
    chest_type:
        "連環殺手"  ---> 1.5
        others  ---> 1.25

    max_hits:
        模擬最多打幾下（避免無限疊）

    return_sequence:
        是否回傳每一擊傷害（分析用）
    """

    # =========================
    # 倍率設定
    # =========================
    r = get_chest_multiplier(combo)

    # =========================
    # 第一擊
    # =========================
    D1 = math.ceil(stats["BASE"] * (1 + stats["WD_effective"]/100))
    D1 = math.ceil(D1 * (1 + stats["TWD"]/100))
    D1 = math.ceil(D1 * (1 + stats["HSD"]/100))
    D1 = math.ceil(D1 * (1 + stats["DTTOOC"]/100))

    # =========================
    # 上限 (第一擊 + 武器傷害的 1250 %)
    # =========================
    DHH_upper_addition = math.ceil(stats["BASE"] * (1 + stats["WD_effective"]/100))
    DHH_upper_addition = math.ceil(DHH_upper_addition * (1 + stats["TWD"]/100))
    DHH_upper_addition = math.ceil(DHH_upper_addition * 12.5)
    DHH_upper_limit = D1 + DHH_upper_addition

    # =========================
    # 疊加傷害
    # =========================
    damages = [D1]

    for i in range(1, max_hits):
        next_dmg = D1 + math.ceil(r * damages[-1])

        if next_dmg > DHH_upper_limit:
            next_dmg = DHH_upper_limit

        damages.append(next_dmg)

        if next_dmg == DHH_upper_limit:
            break

    # 保證至少有三擊
    while len(damages) < 3:
        damages.append(DHH_upper_limit)

    return {
        "first_hit": D1,
        "first_3_hits": damages[:3],
        "upper_limit": DHH_upper_limit
    }


# =========================================================
# 【7】評估 Build（整合所有系統）
# =========================================================
def evaluate_build(combo, config):

    brands = [item[1] for item in combo]
    brand_count = Counter(brands)

    stats = build_base_stats(config)
    stats = apply_brand_effects(brand_count, stats)
    if Activate_Sesonal_Modifier == True:
        stats = apply_season_bonus(stats, season_bonus)
    stats = apply_item_stats(combo, stats)
    stats = finalize_stats(stats, config)

    dmg_info = calc_damage(stats, combo)

    return {
        "combo": [item[0] for item in combo],
        "stats": stats,
        "first_hit": dmg_info["first_hit"],
        "second_hit": dmg_info["first_3_hits"][1],
        "third_hit": dmg_info["first_3_hits"][2],
        "first_3_hits": dmg_info["first_3_hits"],
        "upper_limit": dmg_info["upper_limit"]
    }

# =========================================================
# 【8】主程式：產生所有合理組合 + 排序
# =========================================================
valid_builds = []

for combo in product(*all_parts):
    if is_valid_build(combo, Forcing_Chest_ChainKiller):
        valid_builds.append(combo)

print(f"合理組合數量: {len(valid_builds)}")

# 評估所有 build
results = [evaluate_build(c, agent_config) for c in valid_builds]

def apply_filters(results, query_config):

    filters = query_config["filter"]

    def check(r):

        # 第一擊
        if filters["first_hit"]["enabled"]:
            if r["first_hit"] < filters["first_hit"]["min"]:
                return False

        # 第二擊
        if filters["second_hit"]["enabled"]:
            if r["second_hit"] < filters["second_hit"]["min"]:
                return False

        # 上限
        if filters["upper_limit"]["enabled"]:
            if r["upper_limit"] < filters["upper_limit"]["min"]:
                return False

        return True

    return [r for r in results if check(r)]

def apply_sort(results, query_config):

    sort_key = query_config["sort"]["key"]
    descending = query_config["sort"]["descending"]

    return sorted(results, key=lambda x: x[sort_key], reverse=descending)

def run_query(results, query_config):

    # 篩選
    filtered = apply_filters(results, query_config)

    # 排序
    sorted_results = apply_sort(filtered, query_config)

    # 取前 N
    top_n = query_config["top_n"]

    return sorted_results[:top_n]

def format_stats(stats, ndigits=1):
    formatted = {}
    for k, v in stats.items():
        if isinstance(v, float):
            formatted[k] = round(v, ndigits)
        else:
            formatted[k] = v
    return formatted

print(f"符合條件組合數量: {len(apply_filters(results, query_config))}")

final_results = run_query(results, query_config)

for i, r in enumerate(final_results, 1):
    print(f"\n=== 第 {i} 名 ===")
    print("裝備:  ", r["combo"])
    print("前三擊:", r["first_3_hits"])
    print("上限:  ", r["upper_limit"])
    print("數值:  ", format_stats(r["stats"]))