from django.db import models

class UF(models.Model):
    code_uf = models.BigIntegerField(db_column='code_UF', primary_key=True)
    libelle_standard = models.TextField(null=True, db_column='libelle_standard')
    code_etb = models.BigIntegerField(null=True, db_column='code_ETB')
    code_pole = models.BigIntegerField(null=True, db_column='code_Pole')
    heb= models.BigIntegerField(null=True, db_column='heb')
    type_uf = models.TextField(null=True, db_column='type_UF')
    libelle_type_uf = models.TextField(null=True, db_column='Libelle_type_UF')
    type_activite = models.TextField(null=True, db_column='type_activite')
    libelle_type_activite = models.TextField(null=True, db_column='libelle_type_activite')
    class Meta:
        db_table = 'UF'
        managed = False
    def __str__(self):
        return str(self.code_uf)




