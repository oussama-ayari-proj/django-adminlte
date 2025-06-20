from django.db import models
from django.db.models import Count, Avg, Sum

# Create your models here.

class Hospitalisation(models.Model):    
    num_sequence = models.IntegerField(null=True, blank=True, help_text="Numéro de séquence")
    code_uf = models.IntegerField(db_column='code_UF', null=True, blank=True, help_text="Code de l'unité fonctionnelle")
    code_em = models.IntegerField(db_column='code_EM', null=True, blank=True, help_text="Code EM")
    duree_sejour = models.IntegerField(null=True, blank=True, help_text="Durée du séjour en jours")
    type_sejour = models.TextField(null=True, blank=True, help_text="Type de séjour")
    date_sortie = models.DateField(null=True, blank=True, help_text="Date de sortie")
    ghs = models.TextField(null=True, blank=True, help_text="Groupe homogène de séjours")
    sexe = models.IntegerField(null=True, blank=True, help_text="Sexe du patient (1=M, 2=F)")
    age_entree = models.IntegerField(null=True, blank=True, help_text="Âge à l'entrée")
    semaine_entree = models.IntegerField(null=True, blank=True, help_text="Semaine d'entrée")
    date_entree = models.DateField(null=True, blank=True, help_text="Date d'entrée")
    
    class Meta:
        db_table = 'sejours'
    def __str__(self):
        return f"Séjour {self.num_sequence} - UF {self.code_uf} - {self.date_entree}"
    @property
    def sexe_display(self):
        """Return human-readable gender"""
        if self.sexe == 1:
            return "Masculin"
        elif self.sexe == 2:
            return "Féminin"
        return "Non spécifié"
    
    @property
    def is_long_stay(self):
        """Check if it's a long stay (more than 7 days)"""
        return self.duree_sejour and self.duree_sejour > 7
    
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
        
        # Age statistics
        age_stats = queryset.aggregate(
            age_avg=Avg('age_entree'),
            age_min=models.Min('age_entree'),
            age_max=models.Max('age_entree')
        )
        
        # Gender distribution
        gender_distribution = list(queryset.values('sexe').annotate(
            count=Count('num_sequence', filter=models.Q(num_sequence=1))
        ).order_by('sexe'))
        
        # Convert gender codes to labels
        for item in gender_distribution:
            if item['sexe'] == 1:
                item['sexe'] = 'Masculin'
            elif item['sexe'] == 2:
                item['sexe'] = 'Féminin'
            else:
                item['sexe'] = 'Non spécifié'

        type_sejour_top5 = list(queryset.values('type_sejour').annotate(
            count=Count('num_sequence')
        ).filter(type_sejour__isnull=False).order_by('-count'))
        
        return {
            **basic_stats,
            'age_stats': age_stats,
            'gender_distribution': gender_distribution,
            'type_sejour_top5': type_sejour_top5
        }



