from app.crud.base import CRUDBase
from app.db.models import Assets
from schemas.atbds import Lookup, Create, Update


class CRUDAssets(CRUDBase[Assets, Lookup, Create, Update]):
    pass


order_scenes = CRUDAssets(Assets)
