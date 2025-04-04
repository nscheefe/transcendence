# Generated by Django 4.2.18 on 2025-01-23 03:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('game_id', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoomUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='chat.chatroom')),
            ],
        ),
        migrations.CreateModel(
            name='ChatRoomMessage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('sender_id', models.IntegerField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('chat_room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatroom')),
            ],
        ),
    ]
