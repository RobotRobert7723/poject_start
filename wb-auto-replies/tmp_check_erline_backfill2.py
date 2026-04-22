from sqlalchemy import create_engine, text
engine = create_engine('postgresql+psycopg://n8n:0629ba28a4864e2b95443a52@193.233.131.8:5432/n8n')
with engine.connect() as conn:
    print('feedbacks_raw_shop2', conn.execute(text("select count(*) from feedbacks_raw where shop_id = 2")).scalar())
    print('feedbacks_shop2', conn.execute(text("select count(*) from feedbacks where shop_id = 2")).scalar())
    print('sync_state_shop2', conn.execute(text("select source_api, last_success_at, last_error_text, stats_json from sync_state where shop_id = 2 order by source_api")).fetchall())
