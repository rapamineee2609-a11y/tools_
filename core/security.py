import re
import hashlib
from typing import Dict, List

def check_password_strength(password: str) -> Dict:
    """Check password strength and return detailed report."""
    score = 0
    feedback = []
    
    # Length check
    if len(password) < 8:
        feedback.append("Too short (min 8 characters)")
    elif len(password) >= 12:
        score += 2
    else:
        score += 1
    
    # Complexity checks
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add lowercase letters")
    
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add uppercase letters")
    
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Add numbers")
    
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 2
    else:
        feedback.append("Add special characters")
    
    # Common password check
    common_passwords = ["password", "123456", "qwerty", "admin", "letmein", "welcome"]
    if password.lower() in common_passwords:
        score -= 3
        feedback.append("Very common password")
    
    # Strength rating
    if score <= 2:
        strength = "Weak 🔴"
    elif score <= 4:
        strength = "Moderate 🟡"
    elif score <= 6:
        strength = "Strong 🟢"
    else:
        strength = "Excellent 💪"
    
    return {
        "strength": strength,
        "score": score,
        "max_score": 8,
        "feedback": feedback if feedback else ["Good password!"],
        "length": len(password)
    }
