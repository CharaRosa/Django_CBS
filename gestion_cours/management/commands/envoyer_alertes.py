"""
Management Command: envoyer_alertes
Commande Django pour vérifier et envoyer les alertes de retard.

Usage:
    python manage.py envoyer_alertes
    
Configuration CRON (exemple - tous les jours à 8h00):
    0 8 * * * cd /chemin/vers/projet && python manage.py envoyer_alertes >> /var/log/cbs_alertes.log 2>&1
"""

from django.core.management.base import BaseCommand
from gestion_cours.email_alerts import verifier_et_envoyer_alertes


class Command(BaseCommand):
    help = 'Vérifie les cours en retard et envoie des alertes par email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Mode test: affiche les cours en alerte sans envoyer d\'emails',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🚀 Système d\'Alertes CBS - Démarrage'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        if options['test']:
            self.stdout.write(self.style.WARNING('⚠️  MODE TEST ACTIVÉ - Aucun email ne sera envoyé'))
            from gestion_cours.email_alerts import verifier_cours_en_alerte
            
            cours_en_alerte = verifier_cours_en_alerte()
            
            if cours_en_alerte:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  {len(cours_en_alerte)} cours en alerte détecté(s):')
                )
                
                for alerte in cours_en_alerte:
                    cours = alerte['cours']
                    self.stdout.write(
                        f"  - {cours.matiere.libelle} "
                        f"({alerte['progression']:.1f}%, {alerte['jours_restants']}j restants)"
                    )
                    self.stdout.write(
                        f"    Professeur: {cours.professeur.nom} {cours.professeur.prenoms} "
                        f"({cours.professeur.email})"
                    )
            else:
                self.stdout.write(self.style.SUCCESS('✅ Aucun cours en alerte'))
        
        else:
            # Mode normal: envoi des emails
            cours_en_alerte = verifier_et_envoyer_alertes()
            
            if cours_en_alerte:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Traitement terminé: {len(cours_en_alerte)} alerte(s) envoyée(s)'
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS('✅ Aucun cours en alerte'))
        
        self.stdout.write(self.style.SUCCESS('=' * 60))