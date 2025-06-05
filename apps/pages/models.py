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

class Sejour(models.Model):
    num_sequence = models.IntegerField(null=True, db_column='num_sequence')
    code_uf = models.IntegerField(null=True, db_column='code_UF')
    code_em = models.IntegerField(null=True, db_column='code_EM')
    duree_sejour = models.IntegerField(null=True, db_column='duree_sejour')
    type_sejour = models.TextField(null=True, db_column='type_sejour')
    date_sortie = models.DateField(null=True, db_column='date_sortie')
    ghs = models.TextField(null=True, db_column='ghs')
    sexe = models.IntegerField(null=True, db_column='sexe')
    age_entree = models.IntegerField(null=True, db_column='age_entree')
    semaine_entree = models.IntegerField(null=True, db_column='semaine_entree')
    date_entree = models.DateField(null=True, db_column='date_entree')

    class Meta:
        db_table = 'sejours'
        managed = False

    def __str__(self):
        return f"Sejour {self.id}"


class EM(models.Model):
    code_em = models.IntegerField(db_column='code_EM', primary_key=True)
    libelle_standard = models.TextField(null=True, db_column='libelle_EM')
    
    class Meta:
        db_table = 'EM'
        managed = False

    def __str__(self):
        return str(self.code_em)

class Pole(models.Model):
    code_pole = models.BigIntegerField(db_column='code_Pole', primary_key=True)
    libelle_standard = models.TextField(null=True, db_column='libelle_Pole')
    
    class Meta:
        db_table = 'Pole'
        managed = False

    def __str__(self):
        return str(self.code_pole)
    

class ETB(models.Model):
    code_etb = models.BigIntegerField(db_column='code_ETB', primary_key=True)
    libelle_standard = models.TextField(null=True, db_column='libelle_ETB')
    
    class Meta:
        db_table = 'ETB'
        managed = False

    def __str__(self):
        return str(self.code_etb)







