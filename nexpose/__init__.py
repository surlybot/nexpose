from typing import Optional, Tuple, Mapping, no_type_check

from nexpose.session import Session
from nexpose.site import Site


class Nexpose:

    # mypy dislike kwargs
    @no_type_check
    def __init__(self, host: str, port: int = 3780,
                 sessions_id: Optional[Mapping[Tuple[int, int], str]] = None) -> None:
        kwargs = dict(host=host, port=port, sessions_id=sessions_id)

        self.session = Session(**kwargs)
        self.site = Site(**kwargs)
