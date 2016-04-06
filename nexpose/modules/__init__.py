import logging
from collections import defaultdict

import requests
from lxml import etree
from typing import Optional, Mapping, Tuple

from nexpose.models.failure import Failure
from nexpose.networkerror import NetworkError
from nexpose.types import Element


class ModuleBase:
    def __init__(self, host: str, port: int = 3780,
                 sessions_id: Optional[Mapping[Tuple[int, int], str]] = None) -> None:
        self.host = host
        self.port = port

        self.sessions_id = defaultdict(default_factory=lambda: None)
        if sessions_id is not None:
            self.sessions_id.update(sessions_id)

        logging.captureWarnings(True)

    def _post(self, xml: Element, api_version: Tuple[int, int] = (1, 1)) -> Element:
        url = 'https://{host}:{port}/api/{api_version}/xml'.format(
            host=self.host,
            port=self.port,
            api_version='.'.join([str(v) for v in api_version])
        )

        session_id = self.sessions_id[api_version]
        if session_id is not None:
            xml.attrib['session-id'] = session_id

        req_raw = etree.tostring(xml,
                                 xml_declaration=True,
                                 pretty_print=True,
                                 encoding='UTF-8')

        session = self.__get_session()

        ans = session.post(url=url, data=req_raw, verify=False)
        ans_xml = etree.fromstring(ans.content)

        self.__check_failure(xml=ans_xml, api_version=api_version)

        return ans_xml

    @staticmethod
    def __get_session():
        if '_{}__session'.format(ModuleBase.__name__) not in ModuleBase.__dict__:
            ModuleBase.__session = None

        if ModuleBase.__session is None:
            session = requests.Session()
            session.headers['Content-Type'] = 'text/xml'
            ModuleBase.__session = session
        else:
            ModuleBase.__session.cookies.clear()  # nexpose dislike having login cookies and login for other thing

        return ModuleBase.__session

    @staticmethod
    def __check_failure(xml: Element, api_version: Tuple[int, int]) -> None:
        if api_version == (1, 1):
            if xml.attrib.get('success', None) == '1':
                return
            xml = xml[0]

        if api_version == (1, 2) and xml.tag != 'Failure':
            return

        failure = Failure.from_xml(xml=xml)
        raise NetworkError(failure=failure)