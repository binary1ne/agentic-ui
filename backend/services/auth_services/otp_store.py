import time
from typing import Dict, Any, Optional

class OTPStore:
    """
    Singleton in-memory store for OTPs.
    Stores OTPs with an expiration time.
    """
    _instance = None
    _store: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OTPStore, cls).__new__(cls)
            cls._store = {}
        return cls._instance

    def store_otp(self, key: str, otp: str, ttl_seconds: int = 600):
        """
        Store an OTP for a given key (e.g., email or user_id).
        :param key: The identifier for the user/request.
        :param otp: The OTP string.
        :param ttl_seconds: Time to live in seconds (default 10 minutes).
        """
        expires_at = time.time() + ttl_seconds
        self._store[key] = {
            'otp': otp,
            'expires_at': expires_at
        }
        self.cleanup() # Opportunistic cleanup

    def verify_otp(self, key: str, otp: str) -> bool:
        """
        Verify if the provided OTP matches the stored one and is not expired.
        :param key: The identifier.
        :param otp: The OTP to verify.
        :return: True if valid, False otherwise.
        """
        record = self._store.get(key)
        if not record:
            return False

        if time.time() > record['expires_at']:
            del self._store[key]
            return False

        if record['otp'] == otp:
            del self._store[key] # Consume OTP
            return True
        
        return False

    def cleanup(self):
        """Remove expired OTPs."""
        now = time.time()
        keys_to_remove = [k for k, v in self._store.items() if now > v['expires_at']]
        for k in keys_to_remove:
            del self._store[k]
