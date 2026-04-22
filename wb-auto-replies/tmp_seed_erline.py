from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from wb_auto_replies.app.config.seeds import SeedService

TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjYwMzAydjEiLCJ0eXAiOiJKV1QifQ.eyJhY2MiOjMsImVudCI6MSwiZXhwIjoxNzkyNjQ0ODEzLCJmb3IiOiJzZWxmIiwiaWQiOiIwMTlkYjYxYy03YzJmLTdiYmQtYjU3ZC1hMzdmZjZjZjFkNzkiLCJpaWQiOjMwMTAwNjYzMCwib2lkIjoyNTAwMzQzNDcsInMiOjY0MCwic2lkIjoiYzkzNTk4N2YtNGE2Zi00NzA5LTg4NjUtODA5ZjE1ZjVjZGYwIiwidCI6ZmFsc2UsInVpZCI6MzAxMDA2NjMwfQ.6WTPY1jUcFFnfm55S97ClJtiRJuK1Jtz9BCytXibI1z_wZVLxK4Agm65SgMaT8NR6AlQAyM7rlBTJwMk7ZN59g"
engine = create_engine('postgresql+psycopg://n8n:0629ba28a4864e2b95443a52@193.233.131.8:5432/n8n')
service = SeedService()
with Session(engine) as db:
    shop = service.upsert_shop(db, shop_name='ErLine', wb_token=TOKEN, mode='backfill', gpt_model='gpt-4.1-mini')
    service.seed_karmic_rules(db, shop)
    service.seed_semantic_templates(db, shop)
    db.commit()
    print({'shop_id': shop.shop_id, 'shop_name': shop.shop_name, 'mode': shop.mode})
