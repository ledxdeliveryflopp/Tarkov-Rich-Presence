
class CoreConst:

    allowed_loger_levels: set = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'TRACE'}


class PresenceConst:

    allowed_timer_mode: set = {'general', 'divided'}

    in_raid: dict = {'ru': 'В рейде', 'en': 'In raid'}
    location: dict = {'ru': 'Локация: ', 'en': 'Location: '}

    in_lobby: dict = {'ru': 'В схроне', 'en': 'In lobby'}
    in_lobby_state: dict = {'ru': 'Пока что хз', 'en': 'IDK'}


class LangConst:

    allowed_langs: set = {'ru', 'en'}


class Const:

    application: CoreConst = CoreConst()
    presence: PresenceConst = PresenceConst()
    lang: LangConst = LangConst()


const = Const()
