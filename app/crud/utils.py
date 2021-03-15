from app.db.models import Atbds


def add_id_or_alias_filter(atbd_id: str, *queries):
    try:
        int(atbd_id)
        return [q.filter(Atbds.id == atbd_id) for q in queries]

    except ValueError:
        return [q.filter(Atbds.alias == atbd_id) for q in queries]

