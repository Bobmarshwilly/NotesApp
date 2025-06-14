#!/bin/bash

# Запуск воркера для обработки задач
celery -A notes_app.infrastructure.scheduler.celery_app:celery_app worker \
    -l INFO \
    -Q scheduler,default \
    --without-mingle \
    --without-gossip \
    --pool=solo &

# Запуск планировщика
celery -A notes_app.infrastructure.scheduler.celery_app:celery_app beat \
    -l INFO