from datetime import datetime
from pathlib import Path
import zipfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


class Command(BaseCommand):
    help = 'Gera um backup compactado do banco SQLite local.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--saida',
            default='backups',
            help='Pasta onde o backup será salvo. Padrão: backups',
        )

    def handle(self, *args, **options):
        db_path = Path(settings.DATABASES['default'].get('NAME', ''))
        if not db_path.exists():
            raise CommandError('Banco de dados local não encontrado.')

        pasta_saida = Path(options['saida'])
        pasta_saida.mkdir(parents=True, exist_ok=True)

        agora = timezone.localtime(timezone.now())
        nome_arquivo = pasta_saida / f'backup-riko-barbearia-{agora:%Y-%m-%d-%H-%M}.zip'

        with zipfile.ZipFile(nome_arquivo, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(db_path, arcname='db.sqlite3')
            zip_file.writestr(
                'LEIA-ME.txt',
                'Backup do sistema Dívidas da Barbearia\n'
                f'Gerado em: {agora:%d/%m/%Y %H:%M}\n\n'
                'Para restaurar, substitua o arquivo db.sqlite3 do projeto por este arquivo.\n'
            )

        self.stdout.write(self.style.SUCCESS(f'Backup criado em: {nome_arquivo}'))
