import httpx
from loguru import logger

from src.const import const
from src.github.schemas import ReleaseSchemas


class GitHubApi:

    def __init__(self):
        super().__init__()
        self.latest_release = f'{const.git.GITHUB_API}{const.git.GITHUB_OWNER}/{const.git.GITHUB_REPO}/releases/latest'
        self.token = 'Bearer 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'

    @logger.catch
    def get_latest_release_version(self) -> str:
        logger.info('Getting latest release')
        headers = {'Authorization': self.token}
        response = httpx.get(
            url=self.latest_release, headers=headers,
        )
        validated = ReleaseSchemas(**response.json())
        logger.debug(f'Latest release version: {validated.tag_name}')
        return validated.tag_name
