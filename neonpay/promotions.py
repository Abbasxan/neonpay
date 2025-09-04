"""
NEONPAY Promotions - Promo codes and discount system
Provides flexible discount management for payment stages
"""

import time
import secrets
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DiscountType(Enum):
    """Types of discounts available"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    

@dataclass
class PromoCode:
    """
    Promo code configuration with validation and security
    """
    code: str
    discount_type: DiscountType
    discount_value: Union[int, float]
    max_uses: Optional[int] = None
    expires_at: Optional[float] = None
    min_amount: Optional[int] = None
    max_discount: Optional[int] = None
    user_limit: int = 1
    active: bool = True
    description: str = ""
    created_at: float = field(default_factory=time.time)
    used_count: int = 0
    used_by: Dict[int, int] = field(default_factory=dict)  # user_id -> usage_count
    
    def __post_init__(self):
        """Validate promo code configuration"""
        # Validate code
        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("Promo code must be a non-empty string")
        
        if len(self.code) > 32:
            raise ValueError("Promo code must be 32 characters or less")
        
        # Validate discount type
        if not isinstance(self.discount_type, DiscountType):
            raise ValueError("Discount type must be a valid DiscountType")
        
        # Validate discount value
        if not isinstance(self.discount_value, (int, float)) or self.discount_value <= 0:
            raise ValueError("Discount value must be a positive number")
        
        if self.discount_type == DiscountType.PERCENTAGE:
            if self.discount_value > 100:
                raise ValueError("Percentage discount cannot exceed 100%")
        
        # Validate max_uses
        if self.max_uses is not None:
            if not isinstance(self.max_uses, int) or self.max_uses <= 0:
                raise ValueError("Max uses must be a positive integer")
        
        # Validate expires_at
        if self.expires_at is not None:
            if not isinstance(self.expires_at, (int, float)) or self.expires_at <= 0:
                raise ValueError("Expiration time must be a positive timestamp")
        
        # Validate min_amount
        if self.min_amount is not None:
            if not isinstance(self.min_amount, int) or self.min_amount <= 0:
                raise ValueError("Minimum amount must be a positive integer")
        
        # Validate max_discount
        if self.max_discount is not None:
            if not isinstance(self.max_discount, int) or self.max_discount <= 0:
                raise ValueError("Maximum discount must be a positive integer")
        
        # Validate user_limit
        if not isinstance(self.user_limit, int) or self.user_limit <= 0:
            raise ValueError("User limit must be a positive integer")
    
    def is_valid(self, user_id: int, amount: int) -> tuple[bool, str]:
        """
        Check if promo code is valid for user and amount
        
        Returns:
            (is_valid, error_message)
        """
        if not self.active:
            return False, "Promo code is inactive"
        
        # Check expiration
        if self.expires_at and time.time() > self.expires_at:
            return False, "Promo code has expired"
        
        # Check max uses
        if self.max_uses and self.used_count >= self.max_uses:
            return False, "Promo code usage limit reached"
        
        # Check user limit
        user_usage = self.used_by.get(user_id, 0)
        if user_usage >= self.user_limit:
            return False, "You have reached the usage limit for this promo code"
        
        # Check minimum amount
        if self.min_amount and amount < self.min_amount:
            return False, f"Minimum amount required: {self.min_amount} Stars"
        
        return True, ""
    
    def calculate_discount(self, amount: int) -> int:
        """Calculate discount amount for given price"""
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = int(amount * (self.discount_value / 100))
        else:
            discount = int(self.discount_value)
        
        # Apply maximum discount limit
        if self.max_discount:
            discount = min(discount, self.max_discount)
        
        # Ensure discount doesn't exceed amount
        discount = min(discount, amount - 1)  # Leave at least 1 Star
        
        return max(0, discount)
    
    def use(self, user_id: int) -> None:
        """Mark promo code as used by user"""
        self.used_count += 1
        self.used_by[user_id] = self.used_by.get(user_id, 0) + 1


class PromoSystem:
    """
    Promo code management system
    
    Handles creation, validation, and application of promotional codes
    """
    
    def __init__(self, max_codes: int = 1000):
        self._promo_codes: Dict[str, PromoCode] = {}
        self._max_codes = max_codes
        logger.info("PromoSystem initialized")
    
    def create_promo_code(
        self,
        code: str,
        discount_type: DiscountType,
        discount_value: Union[int, float],
        **kwargs
    ) -> PromoCode:
        """
        Create a new promo code
        
        Args:
            code: Promo code string
            discount_type: Type of discount
            discount_value: Discount value
            **kwargs: Additional promo code parameters
        """
        # Check maximum codes limit
        if len(self._promo_codes) >= self._max_codes:
            raise ValueError(f"Maximum number of promo codes ({self._max_codes}) reached")
        
        # Check if code already exists
        if code.upper() in self._promo_codes:
            raise ValueError(f"Promo code '{code}' already exists")
        
        promo_code = PromoCode(
            code=code.upper(),
            discount_type=discount_type,
            discount_value=discount_value,
            **kwargs
        )
        
        self._promo_codes[code.upper()] = promo_code
        logger.info(f"Created promo code: {code}")
        
        return promo_code
    
    def generate_random_code(
        self,
        discount_type: DiscountType,
        discount_value: Union[int, float],
        length: int = 8,
        **kwargs
    ) -> PromoCode:
        """Generate a random promo code"""
        if length < 4 or length > 32:
            raise ValueError("Code length must be between 4 and 32 characters")
        
        # Generate random code
        while True:
            code = secrets.token_urlsafe(length)[:length].upper()
            if code not in self._promo_codes:
                break
        
        return self.create_promo_code(code, discount_type, discount_value, **kwargs)
    
    def get_promo_code(self, code: str) -> Optional[PromoCode]:
        """Get promo code by code string"""
        return self._promo_codes.get(code.upper())
    
    def validate_promo_code(self, code: str, user_id: int, amount: int) -> tuple[bool, str, Optional[PromoCode]]:
        """
        Validate promo code for user and amount
        
        Returns:
            (is_valid, error_message, promo_code)
        """
        promo_code = self.get_promo_code(code)
        if not promo_code:
            return False, "Invalid promo code", None
        
        is_valid, error_message = promo_code.is_valid(user_id, amount)
        return is_valid, error_message, promo_code
    
    def apply_promo_code(self, code: str, user_id: int, amount: int) -> tuple[int, Optional[PromoCode]]:
        """
        Apply promo code and return discounted amount
        
        Returns:
            (discounted_amount, promo_code)
        """
        is_valid, error_message, promo_code = self.validate_promo_code(code, user_id, amount)
        
        if not is_valid or not promo_code:
            raise ValueError(error_message)
        
        discount = promo_code.calculate_discount(amount)
        discounted_amount = amount - discount
        
        # Mark as used
        promo_code.use(user_id)
        
        logger.info(f"Applied promo code {code}: {amount} -> {discounted_amount} Stars")
        
        return discounted_amount, promo_code
    
    def deactivate_promo_code(self, code: str) -> bool:
        """Deactivate a promo code"""
        promo_code = self.get_promo_code(code)
        if promo_code:
            promo_code.active = False
            logger.info(f"Deactivated promo code: {code}")
            return True
        return False
    
    def remove_promo_code(self, code: str) -> bool:
        """Remove a promo code completely"""
        code_upper = code.upper()
        if code_upper in self._promo_codes:
            del self._promo_codes[code_upper]
            logger.info(f"Removed promo code: {code}")
            return True
        return False
    
    def list_promo_codes(self, active_only: bool = False) -> Dict[str, PromoCode]:
        """Get all promo codes"""
        if active_only:
            return {k: v for k, v in self._promo_codes.items() if v.active}
        return self._promo_codes.copy()
    
    def cleanup_expired(self) -> int:
        """Remove expired promo codes and return count"""
        current_time = time.time()
        expired_codes = []
        
        for code, promo_code in self._promo_codes.items():
            if promo_code.expires_at and current_time > promo_code.expires_at:
                expired_codes.append(code)
        
        for code in expired_codes:
            del self._promo_codes[code]
        
        if expired_codes:
            logger.info(f"Cleaned up {len(expired_codes)} expired promo codes")
        
        return len(expired_codes)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get promo system statistics"""
        active_codes = sum(1 for code in self._promo_codes.values() if code.active)
        total_uses = sum(code.used_count for code in self._promo_codes.values())
        
        return {
            "total_codes": len(self._promo_codes),
            "active_codes": active_codes,
            "total_uses": total_uses,
            "max_codes": self._max_codes
          }
      
