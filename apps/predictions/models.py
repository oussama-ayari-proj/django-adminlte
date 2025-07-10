from django.db import models


class Prediction(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    code_uf = models.BigIntegerField(null=True, blank=True)
    pred = models.FloatField(null=True, blank=True)
    pred_exog = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'uf_pred'
        managed = False
        unique_together = (('date', 'code_uf'),)

    def __str__(self):
        return f"UF {self.code_uf} - {self.date}: pred={self.pred}, pred_exog={self.pred_exog}"
