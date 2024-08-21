from schemas.entity_sample.schema_example import User


def user_fixture(**kwargs):
    base_args = dict(
        username='user',
        email='email@mail.com',
        full_name='user name',
        disabled=False
    )

    # update fixture with kwargs
    base_args.update(kwargs)

    # validates schema
    return User(**base_args)
