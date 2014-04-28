from passlib.context import CryptContext


pwd_context = CryptContext()

USERS = {
    1: 'admin',
    2: 'bob',
    3: 'billy'
}
GROUPS = {
    1: ['g:su', 'u:1'],
    2: ['g:supervisors', 'u:2'],
    3: ['g:reporters', 'u:3']
}


def group_finder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])
    else:
        return None