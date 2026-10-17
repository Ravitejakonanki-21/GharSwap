def users_are_blocked(user_a, user_b) -> bool:
    if user_a is None or user_b is None or user_a == user_b:
        return False
    from .models import Block

    return Block.objects.filter(blocker=user_a, blocked_user=user_b).exists() or Block.objects.filter(
        blocker=user_b, blocked_user=user_a
    ).exists()
