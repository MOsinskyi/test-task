from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Review, Location

@receiver(post_save, sender=Review)
def handle_new_review(sender, instance, created, **kwargs):
    if created:
        instance.location.update_popularity()

        subscribers = instance.location.subscribers.select_related('user')
        recipient_list = [sub.user.email for sub in subscribers if sub.user.email]
        
        if recipient_list:
            send_mail(
                subject=f"New review for {instance.location.name}",
                message=f"Новий відгук, надісланий користувачем {instance.user.username}:\n\n{instance.text}",
                from_email=None,
                recipient_list=recipient_list,
                fail_silently=True,
            )
