from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress = models.FloatField(default=0.0)  # 0.0 - 100.0

    class Meta:
        unique_together = ("user", "course")

    def advance(self, percent):
        """Advance progress by percent (clamped 0-100)."""
        new = min(100.0, max(0.0, self.progress + percent))
        self.progress = new
        self.save()
        return self.progress