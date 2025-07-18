from django.db import models
from django.db.models import Count, Avg, Sum

# Create your models here.

class Hospitalisation(models.Model):
    id = models.AutoField(primary_key=True, db_column='id')    
    num_sequence = models.IntegerField(null=True, blank=True, help_text="Numéro de séquence")
    code_uf = models.IntegerField(db_column='code_UF', null=True, blank=True, help_text="Code de l'unité fonctionnelle")
    code_em = models.IntegerField(db_column='code_EM', null=True, blank=True, help_text="Code EM")
    duree_sejour = models.IntegerField(null=True, blank=True, help_text="Durée du séjour en jours")
    type_sejour = models.TextField(null=True, blank=True, help_text="Type de séjour")
    date_sortie = models.DateField(null=True, blank=True, help_text="Date de sortie")
    ghs = models.TextField(null=True, blank=True, help_text="Groupe homogène de séjours")
    semaine_entree = models.IntegerField(null=True, blank=True, help_text="Semaine d'entrée")
    date_entree = models.DateField(null=True, blank=True, help_text="Date d'entrée")
    
    class Meta:
        db_table = 'sejours'
    def __str__(self):
        return f"Séjour {self.num_sequence} - UF {self.code_uf} - {self.date_entree}"
    
    
    @classmethod
    def get_stats(cls, code_uf=None, start_date=None, end_date=None):
        """Get hospitalisation statistics with optional filtering"""
        queryset = cls.objects.all()
        
        # Apply filters if provided
        if code_uf:
            queryset = queryset.filter(code_uf=code_uf)
        if start_date:
            queryset = queryset.filter(date_entree__gte=start_date)
        if end_date:
            queryset = queryset.filter(date_entree__lte=end_date)
        
        # Basic statistics
        basic_stats = queryset.aggregate(
            total_sejours=Count('num_sequence'),
            duree_moyenne=Avg('duree_sejour'),
            patients_uniques=Count('num_sequence', filter=models.Q(num_sequence=1)),
        )
        
        
        
        

        type_sejour_top5 = list(queryset.values('type_sejour').annotate(
            count=Count('num_sequence')
        ).filter(type_sejour__isnull=False).order_by('-count'))
        
        return {
            **basic_stats,
            'type_sejour_top5': type_sejour_top5
        }

class Lits_occupes(models.Model):
    code_uf = models.IntegerField(db_column='code_uf', null=True, blank=True, help_text="Code de l'unité fonctionnelle")
    lits_occupes = models.IntegerField(null=True, blank=True, help_text="Nombre de lits occupés")
    date = models.DateField(null=True, blank=True, help_text="Date")

    class Meta:
        db_table = 'lits_occupes'
        managed = False  
    
    def __str__(self):
        return f"UF {self.code_uf} - Lits occupés: {self.lits_occupes}, Date: {self.date}"
    
class Besoins(models.Model):
    code_uf = models.BigIntegerField(db_column='code_UF',null=True, blank=True, help_text="Code de l'unité fonctionnelle")
    date = models.DateTimeField(primary_key=True, help_text="Date de la mesure")
    max = models.BigIntegerField(null=True, blank=True, help_text="Valeur maximale")
    min = models.BigIntegerField(null=True, blank=True, help_text="Valeur minimale")
    mediane = models.FloatField(null=True, blank=True, help_text="Médiane")
    class Meta:
        db_table = 'besoin_reel'
        managed = False
        unique_together = (('code_uf', 'date'),)
        
    def __str__(self):
        return f"UF {self.code_uf} - {self.date} : max={self.max}, min={self.min}, mediane={self.mediane}"