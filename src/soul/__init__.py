"""Soul system for personality, identity, and memory."""

from src.soul.bootstrap import (
    BootstrapManager,
    OnboardingStep,
    UserOnboarding,
    get_bootstrap_manager,
    get_onboarding,
)
from src.soul.flush import MemoryFlusher, save_to_memory
from src.soul.init import SoulInitializer
from src.soul.loader import SoulContext, SoulLoader
from src.soul.memory import MemoryManager, get_memory_manager
from src.soul.skills import Skill, SkillRegistry, SkillSelector, get_skill_registry

__all__ = [
    "SoulLoader",
    "SoulContext",
    "SoulInitializer",
    "MemoryManager",
    "get_memory_manager",
    "MemoryFlusher",
    "save_to_memory",
    "SkillRegistry",
    "SkillSelector",
    "Skill",
    "get_skill_registry",
    "BootstrapManager",
    "UserOnboarding",
    "OnboardingStep",
    "get_bootstrap_manager",
    "get_onboarding",
]
