import os
import secrets


if os.path.exists('secrets.sh'):
    raise FileExistsError('secrets.sh already exists')
else:
    with open('secrets.sh', 'w') as f:
        f.write(f"export SECRET_KEY={secrets.token_hex(16)}\n")