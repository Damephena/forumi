from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    use_in_migration = True

    def _create_user(self, email, password, **extra_fields):

        """Creates and saves a User with the given email and password."""
        if not email or not password:
            raise ValueError("Users must have an email address and password")

        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):

        """Creates and saves a superuser with the given email and password."""
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        return self._create_user(email, password, **extra_fields)
