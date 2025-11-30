
class CoreConst:

    allowed_loger_levels: set = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'TRACE'}


class PresenceConst:

    allowed_timer_mode: set = {'general', 'divided'}


class LangConst:

    allowed_langs: set = {'ru', 'en'}


class Const:

    application: CoreConst = CoreConst()
    presence: PresenceConst = PresenceConst()
    lang: LangConst = LangConst()


const = Const()
