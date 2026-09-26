import re
from typing import Dict, Any, List, Tuple, Optional

class InputValidator:
    """
    Strict validation service to prevent invalid, gibberish, or contradictory
    inputs from entering the structured PersonalWishesState.
    """

    PLACEHOLDER_WORDS = {
        "idk", "none", "nothing", "whatever", "n/a", "na", "no idea",
        "random", "test", "testing", "asdf", "foo", "bar", "unknown",
        "blank", "skip", "nope", "null", "nil", "qwerty", "xyz"
    }

    KEYBOARD_MASH_PATTERNS = [
        r"(?:asdf|qwerty|zxcv|poiuy|lkjhg|qazwsx|mnbvc|dfghj|wert)",
    ]

    @classmethod
    def is_gibberish(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects keyboard mash, random strings, repetitive characters,
        or strings lacking linguistic structure.
        """
        s = text.strip()
        if not s:
            return True, "Value cannot be empty"

        s_lower = s.lower()

        # 1. Exact match on known placeholder/refusal words
        if s_lower in cls.PLACEHOLDER_WORDS:
            return True, f"'{s}' is a placeholder or refusal, not a valid legal value"

        # 2. Check for repetitive characters (e.g. "aaaa", "zzzzz", ".....")
        # Distinguish between repetitive letters/symbols (3+) vs digits (5+ like 99999) to allow valid postal codes like 560001 or 1000
        if re.search(r"([a-zA-ZÀ-ÿ])\1{2,}", s_lower) or re.search(r"(\d)\1{4,}", s_lower) or re.search(r"([!?,;@#$%^&*])\1{2,}", s_lower):
            return True, "Contains repetitive characters characteristic of typing tests or mash"

        # 3. Check for keyboard walk patterns
        for pat in cls.KEYBOARD_MASH_PATTERNS:
            if re.search(pat, s_lower):
                return True, "Contains keyboard walk patterns (e.g. 'asdf', 'qwerty')"

        # 4. Check for pure punctuation / symbols
        if not re.search(r"[a-zA-Z0-9À-ÿ]", s):
            return True, "Contains only punctuation or special symbols"

        # 5. Check words for lack of vowels or extreme consonant clusters
        words = re.findall(r"[a-zA-ZÀ-ÿ]+", s)
        for w in words:
            w_lower = w.lower()
            # If word is 4+ characters, it should generally have at least one vowel
            if len(w_lower) >= 4 and not re.search(r"[aeiouyà-ÿ]", w_lower):
                return True, f"Word '{w}' contains no vowels and appears to be random keyboard mash"
            # Check for 5+ consecutive consonants
            if re.search(r"[bcdfghjklmnpqrstvwxz]{5,}", w_lower):
                return True, f"Word '{w}' has unnatural consonant clusters"

        return False, None

    @classmethod
    def validate_name(cls, name: str) -> Tuple[bool, Optional[str]]:
        """
        Validates that a string is a plausible human legal name.
        """
        if not isinstance(name, str):
            return False, "Name must be a text string"

        clean = name.strip()
        if len(clean) < 2:
            return False, "Name is too short (minimum 2 characters)"
        if len(clean) > 80:
            return False, "Name is too long (maximum 80 characters)"

        # Names cannot contain digits
        if re.search(r"\d", clean):
            return False, "Legal names cannot contain digits or numbers"

        # Check for disallowed special characters (only letters, spaces, hyphens, apostrophes, periods allowed)
        if re.search(r"[^A-Za-zÀ-ÿ\s\-\'\.]", clean):
            return False, "Name contains invalid special characters"

        # Check for gibberish
        gibberish, reason = cls.is_gibberish(clean)
        if gibberish:
            return False, f"Invalid name: {reason}"

        return True, None

    @classmethod
    def validate_address(cls, address: str) -> Tuple[bool, Optional[str]]:
        """
        Validates that a string is a plausible physical home address.
        """
        if not isinstance(address, str):
            return False, "Address must be a text string"

        clean = address.strip()
        if len(clean) < 5:
            return False, "Address is too short to be a valid residential address (minimum 5 characters)"
        if len(clean) > 250:
            return False, "Address is too long (maximum 250 characters)"

        # Pure numbers is not an address (needs street or city)
        if re.match(r"^\d+$", clean):
            return False, "Address cannot be only numbers; please include a street name or locality"

        # Must contain letters
        if not re.search(r"[A-Za-zÀ-ÿ]", clean):
            return False, "Address must contain letters identifying the street or city"

        # Check for gibberish
        gibberish, reason = cls.is_gibberish(clean)
        if gibberish:
            return False, f"Invalid address: {reason}"

        return True, None

    @classmethod
    def validate_relationship(cls, relationship: str) -> Tuple[bool, Optional[str]]:
        """
        Validates executor relationship.
        """
        if not isinstance(relationship, str):
            return False, "Relationship must be a text string"

        clean = relationship.strip()
        if len(clean) < 2 or len(clean) > 50:
            return False, "Relationship descriptor has invalid length"

        if re.search(r"\d", clean):
            return False, "Relationship cannot contain digits"

        gibberish, reason = cls.is_gibberish(clean)
        if gibberish:
            return False, f"Invalid relationship: {reason}"

        return True, None

    @classmethod
    def validate_proposed_updates(
        cls,
        updates: Dict[str, Any],
        user_message: str = ""
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Filters proposed updates, stripping any field that fails validation
        and returning a list of rejection reasons.
        """
        validated: Dict[str, Any] = {}
        rejections: List[str] = []

        if not isinstance(updates, dict):
            return {}, ["Proposed state updates must be a dictionary"]

        for field, value in updates.items():
            if value is None:
                continue

            if field == "full_name":
                valid, reason = cls.validate_name(str(value))
                if valid:
                    validated["full_name"] = str(value).strip()
                else:
                    rejections.append(f"Rejected full_name '{value}': {reason}")

            elif field == "home_address":
                valid, reason = cls.validate_address(str(value))
                if valid:
                    validated["home_address"] = str(value).strip()
                else:
                    rejections.append(f"Rejected home_address '{value}': {reason}")

            elif field == "covers_worldwide_assets":
                if isinstance(value, bool):
                    validated["covers_worldwide_assets"] = value
                elif isinstance(value, str) and value.lower() in ["true", "false", "worldwide", "domestic"]:
                    validated["covers_worldwide_assets"] = value.lower() in ["true", "worldwide"]
                else:
                    rejections.append(f"Rejected covers_worldwide_assets '{value}': Must be boolean true/false")

            elif field == "has_children":
                if isinstance(value, bool):
                    validated["has_children"] = value
                elif isinstance(value, str) and value.lower() in ["true", "false", "yes", "no"]:
                    validated["has_children"] = value.lower() in ["true", "yes"]
                else:
                    rejections.append(f"Rejected has_children '{value}': Must be boolean")

            elif field == "children":
                if isinstance(value, list):
                    valid_kids = []
                    for k in value:
                        k_str = str(k).strip()
                        k_valid, k_reason = cls.validate_name(k_str)
                        if k_valid:
                            valid_kids.append(k_str)
                        else:
                            rejections.append(f"Rejected child name '{k_str}': {k_reason}")
                    if valid_kids or not value:
                        validated["children"] = valid_kids
                else:
                    rejections.append("Children must be a list of names")

            elif field == "executor":
                if isinstance(value, dict):
                    valid_exec: Dict[str, Any] = {}
                    if "name" in value:
                        if value["name"]:
                            n_str = str(value["name"]).strip()
                            n_valid, n_reason = cls.validate_name(n_str)
                            if n_valid:
                                valid_exec["name"] = n_str
                            else:
                                rejections.append(f"Rejected executor name '{n_str}': {n_reason}")
                                valid_exec["name"] = None
                        else:
                            valid_exec["name"] = None

                    if "relationship" in value:
                        if value["relationship"]:
                            r_str = str(value["relationship"]).strip()
                            r_valid, r_reason = cls.validate_relationship(r_str)
                            if r_valid:
                                valid_exec["relationship"] = r_str
                            else:
                                rejections.append(f"Rejected executor relationship '{r_str}': {r_reason}")
                                valid_exec["relationship"] = None
                        else:
                            valid_exec["relationship"] = None

                    if valid_exec:
                        validated["executor"] = valid_exec
                else:
                    rejections.append("Executor must be an object with name and relationship")

            elif field == "specific_gifts":
                if isinstance(value, list):
                    valid_gifts = []
                    for g in value:
                        if isinstance(g, dict) and "item" in g and "recipient" in g:
                            item_str = str(g["item"]).strip()
                            recip_str = str(g["recipient"]).strip()
                            item_gib, _ = cls.is_gibberish(item_str)
                            recip_gib, _ = cls.is_gibberish(recip_str)
                            if not item_gib and not recip_gib and len(item_str) >= 2 and len(recip_str) >= 2:
                                valid_gifts.append({"item": item_str, "recipient": recip_str})
                            else:
                                rejections.append(f"Rejected specific gift '{item_str}' to '{recip_str}': item or recipient appears invalid")
                    validated["specific_gifts"] = valid_gifts
                else:
                    rejections.append("specific_gifts must be a list")

            elif field == "additional_wishes":
                if isinstance(value, list):
                    valid_wishes = []
                    for w in value:
                        w_str = str(w).strip()
                        w_gib, _ = cls.is_gibberish(w_str)
                        if not w_gib and len(w_str) >= 3:
                            valid_wishes.append(w_str)
                        else:
                            rejections.append(f"Rejected additional wish '{w_str}': appears invalid or gibberish")
                    validated["additional_wishes"] = valid_wishes
                elif isinstance(value, str):
                    w_str = value.strip()
                    w_gib, _ = cls.is_gibberish(w_str)
                    if not w_gib and len(w_str) >= 3:
                        validated["additional_wishes"] = [w_str]
                    else:
                        rejections.append(f"Rejected additional wish '{w_str}': appears invalid or gibberish")

        return validated, rejections
