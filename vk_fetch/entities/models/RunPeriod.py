from django.db import models


class RunPeriod(models.Model):
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'run_period'
