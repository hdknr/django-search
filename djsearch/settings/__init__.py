from django.conf import settings as dj_settings
from .settings import Settings as BaseSettings


class Settings(BaseSettings):
    @property
    def ELASTICSEARCH(self):
        return dict(
            hosts=self.HOSTS,
            port=self.PORT,
            index=self.INDEX,
        )


PARAMS = (
    ("HOSTS", (False, ["localhost"])),
    ("PORT", (False, 9200)),
    ("INDEX", (False, "django")),
)


djsearch_settings = Settings(
    getattr(dj_settings, "DJSEARCH", None),
    dict((i[0], i[1][1]) for i in PARAMS),
    [i[0] for i in PARAMS if i[1][0]],
)
