from django.db import models


class Lit(models.Model):
    code_uf = models.IntegerField(db_column='code_UF')
    semaine = models.IntegerField(null=True, blank=True)
    lits_installes = models.IntegerField(null=True, blank=True)
    lits_fermes_moyen = models.FloatField(null=True, blank=True)
    lits_fermes_max_prov = models.FloatField(null=True, blank=True)
    journees_fermeture = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'Lits_2024'

    def __str__(self):
        return f"Lit UF {self.code_uf} semaine {self.semaine}"


class RH(models.Model):
    code_uf = models.IntegerField(db_column='code_UF', null=True, blank=True)
    semaine = models.IntegerField(null=True, blank=True)
    metier = models.TextField(null=True, blank=True)
    agents_presents = models.IntegerField(null=True, blank=True)
    agents_abs_imprevu = models.IntegerField(null=True, blank=True)
    agents_abs_prevu = models.IntegerField(null=True, blank=True)
    effectif_total = models.IntegerField(null=True, blank=True)
    abs_total = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'rh_croise'

    def __str__(self):
        return f"Effectif UF {self.code_uf} semaine {self.semaine} métier {self.metier}"



