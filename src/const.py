
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
        12: {'last_exp': 15150},
        13: {'last_exp': 19168},
        14: {'last_exp': 22793},
        15: {'last_exp': 26465},
        16: {'last_exp': 30278},
        17: {'last_exp': 33777},
        18: {'last_exp': 37172},
        19: {'last_exp': 40118},
        20: {'last_exp': 43267},
        21: {'last_exp': 45898},
        22: {'last_exp': 48795},
        23: {'last_exp': 51922},
        24: {'last_exp': 55530},
        25: {'last_exp': 61170},
        26: {'last_exp': 70189},
        27: {'last_exp': 76189},
        28: {'last_exp': 82228},
        29: {'last_exp': 88304},
        30: {'last_exp': 94420},
        31: {'last_exp': 100573},
        32: {'last_exp': 106766},
        33: {'last_exp': 116525},
        34: {'last_exp': 126345},
        35: {'last_exp': 136228},
        36: {'last_exp': 153132},
        37: {'last_exp': 163614},
        38: {'last_exp': 174161},
        39: {'last_exp': 184773},
        40: {'last_exp': 195448},
    }


class CoreConst:

    allowed_loger_levels: set = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'TRACE'}


class PresenceConst:

    allowed_timer_mode: set = {'general', 'divided'}

    in_raid: dict = {'ru': 'В рейде', 'en': 'In raid'}
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
