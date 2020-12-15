# Generated by Django 3.1 on 2020-12-08 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_remove_post_likes_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='likes',
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liked_post', to='network.post')),
                ('liking_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='liking_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='likes',
            constraint=models.UniqueConstraint(fields=('liking_user', 'liked_post'), name='only_like_once'),
        ),
    ]