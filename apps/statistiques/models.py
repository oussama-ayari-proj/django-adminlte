from django.db import models



class ChargeEM(models.Model):
    """
    Model to store the charge of medical teams (EM).
    """
    code_em = models.IntegerField(db_column="Equipe médicale", verbose_name="Nom de l'Équipe Médicale")
    charge = models.IntegerField(verbose_name="Charge de l'Équipe Médicale")
    date = models.DateField(auto_now_add=True, verbose_name="Date de la Charge")

    class Meta:
        db_table = "charge_em"
        managed = False

    def __str__(self):
        return f"{self.em_name} - {self.charge} ({self.date})"