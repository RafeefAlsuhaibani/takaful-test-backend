# users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        # default active=True for normal signups (can change if you want email verify)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # we don’t want username login, so we keep a dummy/blank username field
    # (because AbstractUser expects it), but we won’t use it
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        help_text=_("Not used. Login is by email."),
    )
    email = models.EmailField(_("email address"), unique=True, db_index=True)

    # this tells Django: “use email instead of username”
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []   # when creating superuser, it won’t ask for username

    objects = UserManager()

    def __str__(self):
        return self.email
