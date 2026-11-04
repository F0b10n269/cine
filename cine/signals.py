from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate, dispatch_uid="cine.configure_programming_group")
def configure_programming_group(sender, using, **kwargs):
    if sender.label != "cine":
        return

    permission_codenames = (
        "add_genre",
        "change_genre",
        "view_genre",
        "add_movie",
        "change_movie",
        "view_movie",
        "view_ticket",
    )
    permissions = Permission.objects.using(using).filter(
        content_type__app_label="cine",
        codename__in=permission_codenames,
    )
    group, _ = Group.objects.using(using).get_or_create(name="Programación")
    group.permissions.set(permissions)
