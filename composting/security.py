from sqlalchemy.orm.exc import NoResultFound
from passlib.context import CryptContext


pwd_context = CryptContext()


GROUPS = {
    1: ['g:su', 'u:1'],
    2: ['g:supervisors', 'u:2'],
    3: ['g:reporters', 'u:3']
}


def group_finder(user_id, request):
    from composting.models.user import User
    try:
        user = User.get(User.id == user_id)
    except NoResultFound:
        return None
    else:
        return ['u:{}'.format(user.id)]