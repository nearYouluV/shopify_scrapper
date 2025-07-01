# import sqlite3

# # Connect to the old and new SQLite databases
# old_db_conn = sqlite3.connect('shopify_apps.db')
# old_cursor = old_db_conn.cursor()

# new_db_conn = sqlite3.connect('shopify_app.db')
# new_cursor = new_db_conn.cursor()

# # Helper function to fetch data from the old database and insert it into the new one
# def migrate_table(old_table, new_table, columns):
#     # Fetch data from the old table
#     old_cursor.execute(f"SELECT {', '.join(columns)} FROM {old_table}")
#     rows = old_cursor.fetchall()

#     # Insert data into the new table
#     for row in rows:
#         placeholders = ', '.join(['?' for _ in columns])
#         insert_query = f"INSERT INTO {new_table} ({', '.join(columns)}) VALUES ({placeholders})"
#         new_cursor.executemany(insert_query, [row])

# # Migrate categories
# migrate_table('categories', 'categories', ['id', 'link', 'created_at', 'updated_at'])

# # Migrate developers

# # Migrate apps

# # Migrate app_versions

# # Migrate pricing

# # Commit changes and close connections
# new_db_conn.commit()
# old_db_conn.close()
# new_db_conn.close()

# print("Data migration completed successfully!")
from models import App, Session, Category, Pricing


# with Session() as session: 
#     for cat in session.query(Category).all():
#         print(cat.id)
        
#         # cat.link = cat.link.replace('surface_detail=endear', '').replace('&', '').replace('surface_type=app_details', '')#surface_detail=endear&surface_type=app_details
#         cat.link = f"{cat.link.split('all')[0]}all/"
#         session.commit()

# #delete where category.id == 'categories

# with Session() as session: 
#     session.query(Category).filter(Category.id == 'categories').delete()
#     session.commit()
with Session() as session: 
    session.query(App).filter_by(id='shopify-pos').first().hash = ''
    pricing_data = session.query(Pricing).filter_by(app_id='shopify-pos').all()
    for price_obj in pricing_data:
        price_obj.price = 22
        # session.add(price_obj)
        session.commit()