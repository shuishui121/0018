"""种子数据：剧种、传承人、剧团、学艺经历、获奖、音视频、剧目"""
from datetime import date
from sqlalchemy.orm import Session
from pypinyin import lazy_pinyin, Style

from . import models
from .security import hash_password
from .config import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD


def name_pinyin_initial(name: str) -> str:
    """计算姓名拼音首字母（大写）"""
    if not name:
        return ""
    pys = lazy_pinyin(name, style=Style.FIRST_LETTER)
    if not pys:
        return ""
    return pys[0][0].upper() if pys[0] else ""


def name_pinyin(name: str) -> str:
    return "".join(lazy_pinyin(name))


GENRE_DATA = [
    {
        "name": "京剧",
        "pinyin": "jingju",
        "history": "京剧形成于清代乾隆年间，由徽班进京后融合汉调、昆曲、秦腔等多种戏曲声腔发展而成，被誉为'国粹'，迄今已有两百余年历史。",
        "art_features": "以唱、念、做、打为核心表演手段，角色分生、旦、净、末、丑五大行当；脸谱、水袖、翎子等程式化表演极具特色；唱腔以西皮、二黄为主，伴奏以京胡、月琴、三弦为核心。",
        "classic_plays": "《四郎探母》《贵妃醉酒》《霸王别姬》《空城计》《玉堂春》《龙凤呈祥》",
        "main_schools": "梅派（梅兰芳）、程派（程砚秋）、尚派（尚小云）、荀派（荀慧生）、马派（马连良）、谭派、余派、杨派、奚派、裘派等",
        "distribution_areas": "以北京为中心，辐射天津、上海以及全国主要城市；港澳台地区及海外华人社区亦有广泛传播。",
    },
    {
        "name": "越剧",
        "pinyin": "yueju",
        "history": "发源于浙江嵊县（今嵊州），清末由'落地唱书'演变而成，20 世纪 20 年代进入上海后逐渐兴盛，成为全国第二大剧种。",
        "art_features": "以抒情细腻、唱腔柔美见长，音乐以尺调腔与弦下腔为主；多以才子佳人为题材；表演以女子越剧为特色，生旦净丑均由女演员扮演。",
        "classic_plays": "《梁山伯与祝英台》《红楼梦》《西厢记》《祥林嫂》《碧玉簪》《五女拜寿》",
        "main_schools": "袁派（袁雪芬）、尹派（尹桂芳）、范派（范瑞娟）、傅派（傅全香）、徐派（徐玉兰）、戚派（戚雅仙）、毕派、陆派等",
        "distribution_areas": "主要流行于浙江、上海、江苏、福建等长江以南地区，在港澳台和海外华人中亦具影响力。",
    },
    {
        "name": "黄梅戏",
        "pinyin": "huangmeixi",
        "history": "起源于湖北黄梅县采茶调，清乾隆年间传入安徽安庆一带，与当地民间歌舞、青阳腔融合，形成具有浓郁地方特色的剧种。",
        "art_features": "唱腔质朴清新、朗朗上口，以平词、花腔为两大声腔体系；表演自然生活化，乡土气息浓厚；伴奏以高胡、笛子、扬琴为主。",
        "classic_plays": "《天仙配》《女驸马》《牛郎织女》《打猪草》《夫妻观灯》",
        "main_schools": "严派（严凤英）、王派（王少舫）、马派（马兰）、韩派（韩再芬）等",
        "distribution_areas": "安徽安庆为核心，湖北、江西、江苏等长江中下游省份广泛流行。",
    },
    {
        "name": "豫剧",
        "pinyin": "yuju",
        "history": "旧称河南梆子，发源于明末清初的河南开封一带，由秦腔与蒲州梆子传入河南后与当地民歌小调结合而成。",
        "art_features": "唱腔高亢激昂、大气磅礴，以祥符调、豫东调、豫西调、沙河调为四大流派；板式丰富，擅演袍带戏与现代戏；伴奏以板胡、二胡、琵琶为主。",
        "classic_plays": "《穆桂英挂帅》《花木兰》《红娘》《白蛇传》《朝阳沟》",
        "main_schools": "陈派（陈素真）、常派（常香玉）、崔派（崔兰田）、马派（马金凤）、阎派（阎立品）、桑派等",
        "distribution_areas": "以河南为中心，辐射陕西、山西、河北、山东、湖北、安徽、新疆等十余省区。",
    },
    {
        "name": "昆曲",
        "pinyin": "kunqu",
        "history": "原名'昆山腔'，元末明初形成于江苏昆山一带，经魏良辅改革后风靡明清两朝，被誉为'百戏之祖'，2001 年入选联合国人类非物质文化遗产代表作名录。",
        "art_features": "文词典雅、格律严谨，唱腔婉转清丽，以'婉丽妩媚、一唱三叹'著称；表演精致规范，水袖、扇子、巾生等程式高度成熟；南北曲牌体音乐。",
        "classic_plays": "《牡丹亭》《长生殿》《桃花扇》《西厢记》《浣纱记》《玉簪记》",
        "main_schools": "南昆（苏州派）、北昆（高阳派）、湘昆、永嘉昆等",
        "distribution_areas": "江苏苏州、南京，上海，北京，浙江杭州、永嘉，湖南郴州等地保留专业院团。",
    },
    {
        "name": "秦腔",
        "pinyin": "qinqiang",
        "history": "起源于西周，成形于秦代，盛行于汉唐，是梆子腔的鼻祖，对晋剧、豫剧、河北梆子等剧种均产生深远影响。",
        "art_features": "唱腔慷慨激昂、粗犷豪放，以欢音、苦音为两大腔系；板式众多，角色行当齐全；伴奏以板胡为主奏乐器，配锣鼓铙钹气势雄浑。",
        "classic_plays": "《三滴血》《火焰驹》《周仁回府》《铡美案》《游龟山》",
        "main_schools": "东路秦腔（同州梆子）、西路秦腔（西府秦腔）、南路秦腔（汉调恍恍）、北路秦腔（阿宫腔）",
        "distribution_areas": "以陕西关中为核心，流行于甘肃、宁夏、青海、新疆、山西西部等地。",
    },
]


INHERITOR_DATA = [
    # 京剧
    {"name": "梅葆玖", "gender": "男", "birth": "1934-03-29", "age_group": "70+", "genre": "京剧", "role": "旦角", "region": "北京", "master": None, "bio": "梅兰芳先生第九子，梅派艺术嫡系传人，国家一级演员。"},
    {"name": "李世济", "gender": "女", "birth": "1933-05-01", "age_group": "70+", "genre": "京剧", "role": "旦角", "region": "北京", "master": None, "bio": "程派艺术重要传承人，著名京剧表演艺术家。"},
    {"name": "谭元寿", "gender": "男", "birth": "1929-01-27", "age_group": "70+", "genre": "京剧", "role": "老生", "region": "北京", "master": None, "bio": "谭门第五代嫡传，谭派老生代表人物。"},
    {"name": "张建国", "gender": "男", "birth": "1958-06-01", "age_group": "60-69", "genre": "京剧", "role": "老生", "region": "北京", "master": "谭元寿", "bio": "奚派老生传承人，国家一级演员，中国京剧艺术基金会理事。"},
    {"name": "迟小秋", "gender": "女", "birth": "1965-10-15", "age_group": "50-59", "genre": "京剧", "role": "旦角", "region": "北京", "master": "李世济", "bio": "程派青衣代表人物，北京京剧院领衔主演。"},
    {"name": "杜镇杰", "gender": "男", "birth": "1961-02-28", "age_group": "60-69", "genre": "京剧", "role": "老生", "region": "北京", "master": None, "bio": "余杨派老生传承人，北京京剧院国家一级演员。"},
    {"name": "王珮瑜", "gender": "女", "birth": "1978-03-04", "age_group": "40-49", "genre": "京剧", "role": "老生", "region": "上海", "master": None, "bio": "余派坤生代表，上海京剧院国家一级演员，致力于京剧传播。"},

    # 越剧
    {"name": "袁雪芬", "gender": "女", "birth": "1922-03-26", "age_group": "70+", "genre": "越剧", "role": "旦角", "region": "上海", "master": None, "bio": "越剧袁派创始人，越剧改革先驱，国家级非物质文化遗产传承人。"},
    {"name": "王文娟", "gender": "女", "birth": "1926-12-19", "age_group": "70+", "genre": "越剧", "role": "旦角", "region": "上海", "master": None, "bio": "越剧王派创始人，以《红楼梦》林黛玉一角闻名。"},
    {"name": "徐玉兰", "gender": "女", "birth": "1921-12-27", "age_group": "70+", "genre": "越剧", "role": "小生", "region": "上海", "master": None, "bio": "越剧徐派小生创始人，代表角色《红楼梦》贾宝玉。"},
    {"name": "单仰萍", "gender": "女", "birth": "1962-06-29", "age_group": "60-69", "genre": "越剧", "role": "旦角", "region": "上海", "master": "王文娟", "bio": "王派传人，上海越剧院国家一级演员。"},
    {"name": "钱惠丽", "gender": "女", "birth": "1963-04-01", "age_group": "60-69", "genre": "越剧", "role": "小生", "region": "上海", "master": "徐玉兰", "bio": "徐派小生传承人，上海越剧院副院长。"},
    {"name": "茅威涛", "gender": "女", "birth": "1962-08-08", "age_group": "60-69", "genre": "越剧", "role": "小生", "region": "浙江杭州", "master": None, "bio": "尹派代表人物，浙江小百花越剧院院长，中国戏剧家协会副主席。"},
    {"name": "陈飞", "gender": "女", "birth": "1969-07-15", "age_group": "50-59", "genre": "越剧", "role": "旦角", "region": "浙江绍兴", "master": None, "bio": "傅派传人，绍兴小百花越剧团国家一级演员。"},

    # 黄梅戏
    {"name": "严凤英", "gender": "女", "birth": "1930-04-13", "age_group": "70+", "genre": "黄梅戏", "role": "旦角", "region": "安徽安庆", "master": None, "bio": "黄梅戏一代宗师，严派创始人，代表作品《天仙配》《女驸马》。"},
    {"name": "马兰", "gender": "女", "birth": "1962-04-23", "age_group": "60-69", "genre": "黄梅戏", "role": "旦角", "region": "安徽合肥", "master": None, "bio": "黄梅戏五朵金花之一，中国戏剧梅花奖得主。"},
    {"name": "韩再芬", "gender": "女", "birth": "1968-03-20", "age_group": "50-59", "genre": "黄梅戏", "role": "旦角", "region": "安徽安庆", "master": None, "bio": "韩派创始人，安庆再芬黄梅艺术剧院院长，国家一级演员。"},
    {"name": "吴琼", "gender": "女", "birth": "1962-03-24", "age_group": "60-69", "genre": "黄梅戏", "role": "旦角", "region": "安徽合肥", "master": None, "bio": "黄梅戏五朵金花之一，以演唱严派名段著称。"},
    {"name": "黄新德", "gender": "男", "birth": "1947-08-01", "age_group": "70+", "genre": "黄梅戏", "role": "小生", "region": "安徽合肥", "master": None, "bio": "黄梅戏生角代表人物，国家一级演员。"},

    # 豫剧
    {"name": "常香玉", "gender": "女", "birth": "1923-09-15", "age_group": "70+", "genre": "豫剧", "role": "旦角", "region": "河南郑州", "master": None, "bio": "豫剧常派创始人，人民艺术家，以《花木兰》闻名全国。"},
    {"name": "马金凤", "gender": "女", "birth": "1922-11-01", "age_group": "70+", "genre": "豫剧", "role": "旦角", "region": "河南洛阳", "master": None, "bio": "豫剧马派创始人，代表剧目《穆桂英挂帅》。"},
    {"name": "陈素真", "gender": "女", "birth": "1918-04-01", "age_group": "70+", "genre": "豫剧", "role": "旦角", "region": "河南开封", "master": None, "bio": "豫剧陈派创始人，豫剧皇后。"},
    {"name": "李树建", "gender": "男", "birth": "1962-04-15", "age_group": "60-69", "genre": "豫剧", "role": "老生", "region": "河南郑州", "master": None, "bio": "豫剧李派老生创始人，河南豫剧院院长，中国戏剧家协会副主席。"},
    {"name": "虎美玲", "gender": "女", "birth": "1946-06-01", "age_group": "70+", "genre": "豫剧", "role": "旦角", "region": "河南郑州", "master": "常香玉", "bio": "常派传人，国家一级演员。"},
    {"name": "汪荃珍", "gender": "女", "birth": "1963-02-20", "age_group": "60-69", "genre": "豫剧", "role": "旦角", "region": "河南郑州", "master": None, "bio": "河南豫剧院三团团长，中国戏剧梅花奖得主。"},

    # 昆曲
    {"name": "俞振飞", "gender": "男", "birth": "1902-07-15", "age_group": "70+", "genre": "昆曲", "role": "小生", "region": "上海", "master": None, "bio": "昆曲俞派小生创始人，江南曲圣俞粟庐之子。"},
    {"name": "蔡正仁", "gender": "男", "birth": "1941-07-02", "age_group": "70+", "genre": "昆曲", "role": "小生", "region": "上海", "master": "俞振飞", "bio": "俞派传人，上海昆剧团国家一级演员，国家级非遗传承人。"},
    {"name": "张继青", "gender": "女", "birth": "1939-01-03", "age_group": "70+", "genre": "昆曲", "role": "旦角", "region": "江苏南京", "master": None, "bio": "昆曲'张三梦'（《惊梦》《寻梦》《痴梦》）代表人物，梅花大奖得主。"},
    {"name": "王芳", "gender": "女", "birth": "1963-05-01", "age_group": "60-69", "genre": "昆曲", "role": "旦角", "region": "江苏苏州", "master": None, "bio": "苏州昆剧院领衔主演，中国戏剧梅花奖二度梅得主。"},
    {"name": "魏春荣", "gender": "女", "birth": "1969-01-01", "age_group": "50-59", "genre": "昆曲", "role": "旦角", "region": "北京", "master": None, "bio": "北方昆曲剧院国家一级演员，梅花奖得主。"},

    # 秦腔
    {"name": "马友仙", "gender": "女", "birth": "1944-04-15", "age_group": "70+", "genre": "秦腔", "role": "旦角", "region": "陕西西安", "master": None, "bio": "秦腔马派创始人，国家级非物质文化遗产传承人。"},
    {"name": "贠宗翰", "gender": "男", "birth": "1940-01-01", "age_group": "70+", "genre": "秦腔", "role": "老生", "region": "陕西西安", "master": None, "bio": "秦腔表演艺术家，以《三滴血》《赵氏孤儿》闻名。"},
    {"name": "李梅", "gender": "女", "birth": "1969-06-16", "age_group": "50-59", "genre": "秦腔", "role": "旦角", "region": "陕西西安", "master": "马友仙", "bio": "陕西省戏曲研究院院长，中国戏剧梅花奖二度梅得主。"},
    {"name": "李东桥", "gender": "男", "birth": "1961-02-20", "age_group": "60-69", "genre": "秦腔", "role": "小生", "region": "陕西西安", "master": None, "bio": "秦腔小生代表人物，梅花奖得主。"},
    {"name": "齐爱云", "gender": "女", "birth": "1968-02-01", "age_group": "50-59", "genre": "秦腔", "role": "旦角", "region": "陕西西安", "master": None, "bio": "西安秦腔剧院国家一级演员，梅花奖得主。"},
]


TROUPE_DATA = [
    {"name": "国家京剧院", "genre": "京剧", "region": "北京", "description": "国家级京剧专业院团，承担京剧艺术传承创新重任。"},
    {"name": "北京京剧院", "genre": "京剧", "region": "北京", "description": "梅、尚、程、荀、马、谭、张、裘诸派荟萃的一流院团。"},
    {"name": "上海京剧院", "genre": "京剧", "region": "上海", "description": "南方京剧重镇，创作演出多部优秀新编历史剧。"},
    {"name": "上海越剧院", "genre": "越剧", "region": "上海", "description": "越剧艺术最高殿堂之一，袁、尹、范、傅、徐、王等流派传承基地。"},
    {"name": "浙江小百花越剧院", "genre": "越剧", "region": "浙江杭州", "description": "以'小百花'品牌享誉海内外，越剧创新的重要力量。"},
    {"name": "安庆再芬黄梅艺术剧院", "genre": "黄梅戏", "region": "安徽安庆", "description": "以韩再芬命名的黄梅戏专业院团，致力于黄梅戏传承创新。"},
    {"name": "安徽省黄梅戏剧院", "genre": "黄梅戏", "region": "安徽合肥", "description": "黄梅戏代表性院团，创作演出多部经典现代戏。"},
    {"name": "河南豫剧院", "genre": "豫剧", "region": "河南郑州", "description": "豫剧最高艺术机构，下辖三个演出团，流派纷呈。"},
    {"name": "洛阳豫剧院", "genre": "豫剧", "region": "河南洛阳", "description": "马派艺术传承基地，《穆桂英挂帅》为其代表剧目。"},
    {"name": "上海昆剧团", "genre": "昆曲", "region": "上海", "description": "南昆传承重镇，俞振飞等大师亲传弟子集中地。"},
    {"name": "江苏省苏州昆剧院", "genre": "昆曲", "region": "江苏苏州", "description": "昆曲发源地核心院团，'传'字辈传承有序。"},
    {"name": "北方昆曲剧院", "genre": "昆曲", "region": "北京", "description": "北昆代表院团，保留高阳派艺术特色。"},
    {"name": "陕西省戏曲研究院", "genre": "秦腔", "region": "陕西西安", "description": "西北地区最大戏曲院团，秦腔传承创新核心力量。"},
    {"name": "西安秦腔剧院", "genre": "秦腔", "region": "陕西西安", "description": "西安本土秦腔院团，易俗社与三意社百年老店合体。"},
]


def seed(db: Session) -> None:
    """填充种子数据（幂等）"""
    # 创建默认管理员
    if not db.query(models.User).filter(models.User.username == DEFAULT_ADMIN_USERNAME).first():
        db.add(models.User(
            username=DEFAULT_ADMIN_USERNAME,
            password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            role="admin",
        ))
        db.commit()

    # 创建剧种
    genre_map: dict[str, models.Genre] = {}
    for g in GENRE_DATA:
        genre = db.query(models.Genre).filter(models.Genre.name == g["name"]).first()
        if not genre:
            genre = models.Genre(**g)
            db.add(genre)
            db.flush()
        genre_map[genre.name] = genre

    db.commit()

    # 第一遍：先创建所有传承人（不处理师承）
    inheritor_map: dict[str, models.Inheritor] = {}
    for ih in INHERITOR_DATA:
        existing = db.query(models.Inheritor).filter(models.Inheritor.name == ih["name"], models.Inheritor.genre_id == genre_map[ih["genre"]].id).first()
        if existing:
            inheritor_map[existing.name] = existing
            continue
        genre = genre_map[ih["genre"]]
        obj = models.Inheritor(
            name=ih["name"],
            pinyin_initial=name_pinyin_initial(ih["name"]),
            gender=ih["gender"],
            birth_date=date.fromisoformat(ih["birth"]),
            age_group=ih["age_group"],
            genre_id=genre.id,
            role_type=ih["role"],
            region=ih["region"],
            master_id=None,
            bio=ih["bio"],
        )
        db.add(obj)
        inheritor_map[ih["name"]] = obj

    db.flush()

    # 第二遍：补师承
    for ih in INHERITOR_DATA:
        if ih["master"] and ih["master"] in inheritor_map:
            inheritor_map[ih["name"]].master_id = inheritor_map[ih["master"]].id

    db.commit()

    # 剧团
    for t in TROUPE_DATA:
        genre = genre_map.get(t["genre"])
        existing = db.query(models.Troupe).filter(models.Troupe.name == t["name"]).first()
        if existing:
            continue
        db.add(models.Troupe(
            name=t["name"],
            genre_id=genre.id if genre else None,
            region=t["region"],
            description=t["description"],
        ))

    # 代表剧目
    classic_plays_map: dict[tuple[str, str], models.Play] = {}
    for ih in INHERITOR_DATA:
        name = ih["name"]
        genre = genre_map[ih["genre"]]
        # 为每位传承人随机分配 2-3 个代表剧目（按剧种）
        role = ih["role"]
        # 根据剧种直接从经典剧目描述中取几个
        samples = []
        if ih["genre"] == "京剧":
            samples = [("四郎探母", "杨四郎"), ("贵妃醉酒", "杨贵妃"), ("空城计", "诸葛亮"), ("霸王别姬", "虞姬")]
        elif ih["genre"] == "越剧":
            samples = [("红楼梦", role in ("旦角",) and "林黛玉" or "贾宝玉"), ("梁山伯与祝英台", role in ("旦角",) and "祝英台" or "梁山伯"), ("西厢记", "崔莺莺")]
        elif ih["genre"] == "黄梅戏":
            samples = [("天仙配", "七仙女"), ("女驸马", "冯素珍"), ("牛郎织女", "织女")]
        elif ih["genre"] == "豫剧":
            samples = [("花木兰", "花木兰"), ("穆桂英挂帅", "穆桂英"), ("三哭殿", "银屏公主")]
        elif ih["genre"] == "昆曲":
            samples = [("牡丹亭", "杜丽娘"), ("长生殿", "杨贵妃"), ("西厢记", "张生")]
        else:
            samples = [("三滴血", "周天佑"), ("火焰驹", "李彦荣"), ("周仁回府", "周仁")]
        for i, (play_name, role_name) in enumerate(samples[:3]):
            key = (ih["genre"], play_name)
            if key not in classic_plays_map:
                play = db.query(models.Play).filter(models.Play.name == play_name, models.Play.genre_id == genre.id).first()
                if not play:
                    play = models.Play(name=play_name, genre_id=genre.id, description=f"{genre.name}经典剧目《{play_name}》")
                    db.add(play)
                    db.flush()
                classic_plays_map[key] = play
            play = classic_plays_map[key]
            ih_obj = inheritor_map[name]
            # 检查是否已关联
            exists = db.query(models.InheritorPlay).filter(models.InheritorPlay.inheritor_id == ih_obj.id, models.InheritorPlay.play_id == play.id).first()
            if not exists:
                db.add(models.InheritorPlay(inheritor_id=ih_obj.id, play_id=play.id, role_name=role_name))

    # 学艺经历（每位传承人 2-4 条）
    for ih in INHERITOR_DATA:
        ih_obj = inheritor_map[ih["name"]]
        existing_learn = db.query(models.Learning).filter(models.Learning.inheritor_id == ih_obj.id).first()
        if existing_learn:
            continue
        birth_year = int(ih["birth"][:4])
        learnings = [
            {"year": birth_year + 10, "title": f"入{ih['genre']}科班学艺", "description": f"在{ih['region']}当地戏校启蒙，师从前辈学习基本功。"},
            {"year": birth_year + 15, "title": "正式拜师学艺", "description": f"工{ih['role']}，系统学习唱念做打。"},
            {"year": birth_year + 25, "title": "加入专业剧团", "description": f"进入{ih['region']}专业院团，舞台实践逐渐成熟。"},
            {"year": birth_year + 35, "title": "艺术风格形成期", "description": f"在继承传统基础上形成个人表演特色。"},
        ]
        for l in learnings[:3]:
            db.add(models.Learning(inheritor_id=ih_obj.id, **l))

    # 获奖（每位传承人 1-3 条）
    for ih in INHERITOR_DATA:
        ih_obj = inheritor_map[ih["name"]]
        existing_award = db.query(models.Award).filter(models.Award.inheritor_id == ih_obj.id).first()
        if existing_award:
            continue
        birth_year = int(ih["birth"][:4])
        awards = [
            {"name": "中国戏剧梅花奖", "year": birth_year + 40, "level": "国家级"},
            {"name": "文华表演奖", "year": birth_year + 45, "level": "国家级"},
            {"name": f"{ih['genre']}表演艺术终身成就奖", "year": birth_year + 55, "level": "省级"},
        ]
        for a in awards[:2 if ih["age_group"] in ("40-49", "50-59") else 3]:
            if a["year"] <= 2026:
                db.add(models.Award(inheritor_id=ih_obj.id, **a))

    # 音视频资料（每位传承人 1-3 条）
    for ih in INHERITOR_DATA:
        ih_obj = inheritor_map[ih["name"]]
        existing_media = db.query(models.Media).filter(models.Media.inheritor_id == ih_obj.id).first()
        if existing_media:
            continue
        media_list = [
            {"type": "audio", "title": f"{ih['name']}唱腔精选（一）", "file_path": None, "description": "经典剧目唱腔录音资料。"},
            {"type": "video", "title": f"{ih['name']}代表剧目演出录像", "file_path": None, "description": "舞台演出现场录像。"},
            {"type": "audio", "title": f"{ih['name']}谈艺录", "file_path": None, "description": "口述历史采访录音。"},
        ]
        for m in media_list[:2]:
            db.add(models.Media(inheritor_id=ih_obj.id, **m))

    db.commit()
