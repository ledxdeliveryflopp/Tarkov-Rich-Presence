
class LevelsConst:

    range: dict = {
        1: {'last_exp': 0, 'full_exp': 0},
        2: {'last_exp': 1000},
        3: {'last_exp': 3017},
        4: {'last_exp': 4415},
        5: {'last_exp': 5824},
        6: {'last_exp': 7221},
        7: {'last_exp': 8546},
        8: {'last_exp': 9913},
        9: {'last_exp': 11268},
        10: {'last_exp': 12519},
        11: {'last_exp': 13840},
        12: {'last_exp': 15716},
        13: {'last_exp': 22023},
        14: {'last_exp': 27951},
        15: {'last_exp': 34084},
        16: {'last_exp': 40548},
        17: {'last_exp': 46547},
        18: {'last_exp': 52419},
        19: {'last_exp': 57549},
        20: {'last_exp': 63065},
        21: {'last_exp': 67696},
        22: {'last_exp': 72817},
        23: {'last_exp': 78369},
        24: {'last_exp': 84803},
        25: {'last_exp': 94916},
        26: {'last_exp': 108067},
        27: {'last_exp': 122126},
        28: {'last_exp': 133164},
        29: {'last_exp': 144320},
        30: {'last_exp': 155595},
        31: {'last_exp': 166982},
        32: {'last_exp': 180344},
        33: {'last_exp': 196685},
        34: {'last_exp': 215087},
        35: {'last_exp': 233690},
        36: {'last_exp': 258091},
        37: {'last_exp': 281805},
        38: {'last_exp': 305744},
        39: {'last_exp': 326065},
        40: {'last_exp': 346570},
        41: {'last_exp': 367261},
        42: {'last_exp': 388137},
        43: {'last_exp': 416600},
        44: {'last_exp': 445333},
        45: {'last_exp': 474331},
        46: {'last_exp': 528224},
        47: {'last_exp': 559155},
        48: {'last_exp': 590350},
        49: {'last_exp': 621815},
        50: {'last_exp': 653537},
    }


class CoreConst:

    allowed_loger_levels: set = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'TRACE'}


class PresenceConst:

    allowed_timer_mode: set = {'general', 'divided'}

    level_details: dict = {'ru': 'Уровень', 'en': 'Level'}
    prestige_details: dict = {'ru': 'Престиж', 'en': 'Prestige'}
    in_raid_state: dict = {'ru': 'В рейде: ', 'en': 'In raid: '}
    location: dict = {'ru': 'Локация: ', 'en': 'Location: '}

    in_lobby: dict = {'ru': 'В схроне', 'en': 'In lobby'}
    in_lobby_state: dict = {'ru': 'Игроков в отряде: ', 'en': 'Players in lobby: '}


class LangConst:

    allowed_langs: set = {'ru', 'en'}


class Const:

    application: CoreConst = CoreConst()
    presence: PresenceConst = PresenceConst()
    lang: LangConst = LangConst()
    levels: LevelsConst = LevelsConst()


const = Const()
