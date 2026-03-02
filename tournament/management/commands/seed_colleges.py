from django.core.management.base import BaseCommand
from tournament.models import College

class Command(BaseCommand):
    help = 'Seeds the database with initial college data'

    def handle(self, *args, **kwargs):
        college_names = [
            "Theyagaraja polytechnic, amballur",
            "Sree rama polytechnic, thriprayar",
            "Govt. Polytechnic, kunnakulam",
            "Model polytechnic, vadakara",
            "Kkmmptc, kallettumkara",
            "Holy grace polytechnic, mala",
            "Mets polytechnic, mala",
            "Iccs polytechnic, mupliyam"
        ]
        # Reverse map for credentials setup
        CRED_MAP = {
            "Theyagaraja polytechnic, amballur": ("theyagarajapolytechnicamballur", "TPA@bcd"),
            "Sree rama polytechnic, thriprayar": ("sreeramapolytechnicthriprayar", "SRPT@uv"),
            "Govt. Polytechnic, kunnakulam": ("govtpolytechnickunnakulam", "GPK@asd"),
            "Model polytechnic, vadakara": ("modelpolytechnicvadakara", "MPV@wxy"),
            "Kkmmptc, kallettumkara": ("kkmmptckallettumkara", "RAjesh"),
            "Holy grace polytechnic, mala": ("holygracepolytechnicmala", "HGPM@hij"),
            "Mets polytechnic, mala": ("metspolytechnicmala", "MPM@lmn"),
            "Iccs polytechnic, mupliyam": ("iccspolytechnicmupliyam", "IPM@xyz")
        }

        count = 0
        for name in college_names:
            college, created = College.objects.get_or_create(name=name)
            if created and name in CRED_MAP:
                username, password = CRED_MAP[name]
                college.username = username
                college.password = password  # Model save() will hash it
                college.save()
                count += 1
            elif not created and name in CRED_MAP:
                # Update existing if they don't have username/password (optional but good for testing)
                username, password = CRED_MAP[name]
                if not college.username or not college.password:
                    college.username = username
                    college.password = password
                    college.save()
                    count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded/updated {count} colleges.'))
