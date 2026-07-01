import bcrypt
from logging import getLogger

logger = getLogger(__name__)

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

if __name__ == "__main__":
    password = "my_secure_password"
    hashed = get_password_hash(password)
    logger.info(f"Hashed password: {hashed}")
    logger.info(f"Password verification: {verify_password(password, hashed)}")
    logger.info(f"Password verification with wrong password: {verify_password('wrong_password', hashed)}")
    is_valid = verify_password(password, hashed)
    logger.info(f"Is the password valid? {is_valid}")