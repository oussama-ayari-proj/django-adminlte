from django.db import models



class ChargeEM(models.Model):
    """
    Model to store the charge of medical teams (EM).
    """
    code_em = models.IntegerField(db_column="Equipe médicale", verbose_name="Nom de l'Équipe Médicale")
    charge = models.IntegerField(db_column="Value",verbose_name="Charge de l'Équipe Médicale")
    date = models.DateField(verbose_name="Date de la Charge",db_column="Date")
    code_uf = models.IntegerField(db_column="Code UF", null=True, blank=True, verbose_name="Code de l'Unité Fonctionnelle")
    class Meta:
        db_table = "charge_em_uf"
        managed = False

    def __str__(self):
        return f"{self.em_name} - {self.charge} ({self.date})"