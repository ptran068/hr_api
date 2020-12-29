from django.db import models


class Titles(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        db_table = 'hr_titles'

    def __repr__(self):
        return self.title

