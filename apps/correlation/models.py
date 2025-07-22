from django.db import models

# Create your models here.
class Lit(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')
    code_uf = models.IntegerField(db_column='Code UF')
    semaine = models.IntegerField(null=True, blank=True,db_column='Semaine')
    lits_installes = models.IntegerField(null=True, blank=True,db_column='LITS INSTALLES')
    lits_fermes_moyen = models.FloatField(null=True, blank=True,db_column='Lits fermés moyens')
    journees_fermeture = models.FloatField(null=True, blank=True,db_column='Journées lits fermées 2024')

    class Meta:
        db_table = 'Lits_total'
        managed = False
        unique_together = (('code_uf', 'semaine'),)

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
    code_metier = models.TextField(null=True, blank=True)
    code_famille = models.TextField(null=True, blank=True)
    famille_metier = models.TextField(db_column='Famille Métier' ,null=True, blank=True)
    sous_famille_code = models.TextField(db_column='Sous-Famille Code' ,null=True, blank=True)
    sous_famille_metier = models.TextField(db_column='Sous-Famille' ,null=True, blank=True)

    class Meta:
        db_table = 'rh_croise'

    def __str__(self):
        return f"Effectif UF {self.code_uf} semaine {self.semaine} métier {self.metier}"