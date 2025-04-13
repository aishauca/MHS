from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test sending email'

    def handle(self, *args, **options):
        try:
            send_mail(
                'Test email from UCA Mental Health',
                'This is a test email to verify SMTP settings.',
                settings.DEFAULT_FROM_EMAIL,
                ['your-test-email@ucentralasia.org'],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Test email sent successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))