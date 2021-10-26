from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify

User = get_user_model()

CATEGORY_TYPE = (
    ("FinTech", "FinTech"),
    ("HealthTech", "HealthTech"),
    ("InsuranceTech", "InsuranceTech"),
    ("AutomobileTech", "AutomobileTech"),
    ("Internet", "Internet"),
    ("EduTech", "EduTech"),
    ("Gaming", "Gaming"),
    ("Wearables", "Wearables"),
    ("OpenSource", "OpenSource"),
    ("Others", "Others")
)


class Discussion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=130)
    slug = models.SlugField(unique=True, null=True, blank=True, editable=False)
    content = models.TextField()
    img = models.ImageField(upload_to="images/discussion/%Y/%m/%d/", null=True, blank=True)
    category = models.CharField(max_length=25, blank=True, default="Others", choices=CATEGORY_TYPE)
    tags = models.CharField(max_length=70, blank=True, help_text="Separate tags with comma")
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_likes_count(self):
        return self.likes.count()

    def _get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while Discussion.objects.filter(slug=unique_slug).exists():
            unique_slug = "{}-{}".format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._get_unique_slug()
        super().save(*args, **kwargs)

    def get_tags(self):
        return self.tags.split(",")

    def delete(self, *args, **kwargs):
        if self.img:
            self.img.delete()
        super().delete(*args, **kwargs)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey("Discussion", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

    def comment_count(self):
        return self.content.count()
