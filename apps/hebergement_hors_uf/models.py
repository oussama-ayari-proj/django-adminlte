from django.db import models

# Create your models here.


class EM(models.Model):
    code_em = models.IntegerField(db_column='code_EM', primary_key=True)
    libelle_em = models.TextField(db_column='libelle_EM', null=True, blank=True, help_text="Libellé de l'EM")

    class Meta:
        db_table = 'EM'
        managed = False  
    
    def __str__(self):
        return f"EM {self.code_em} - {self.libelle_em}"

class Matrice_EM_UF(models.Model):
    code_em = models.IntegerField(db_column='code_EM', null=True, blank=True, help_text="Code de l'EM")
    code_uf = models.IntegerField(db_column='code_UF', null=True, blank=True, help_text="Code de l'UF")
    code_pole = models.TextField(db_column='num_Pole', null=True, blank=True, help_text="Code du pôle")
    class Meta:
        db_table = 'matrice_EM'
        managed = False
        # If your table has a composite primary key, use this:
        unique_together = [['code_em', 'code_uf']]
    
    def __str__(self):
        return f"EM {self.code_em} - UF {self.code_uf}"
    

class export_UF(models.Model):
    code_uf = models.IntegerField(db_column='code_UF', primary_key=True, help_text="Code de l'UF")
    libelle_standard = models.TextField(db_column='libelle_standard', null=True, blank=True, help_text="Libellé standard de l'UF")

    class Meta:
        db_table = 'export_UF'
        managed = False
    
    def __str__(self):
        return f"UF {self.code_uf} - {self.libelle_standard}"