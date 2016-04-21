from nexpose.types import Element


class WeirdXmlAnswerError(Exception):
    pass


class StillElementInAttribError(WeirdXmlAnswerError):
    def __init__(self, element: Element) -> None:
        super().__init__(element, element.attrib, element.text)


class StillSubElementError(WeirdXmlAnswerError):
    def __init__(self, element: Element) -> None:
        super().__init__(element, list(element))
