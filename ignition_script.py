import utils.db as dbcon

dbcon.init_db(ignitive_run=True)


# 어드민 계정 추가
# dbcon.add_user(
#     user_id="admin",
#     pwd="(password)",
#     email="(email)",
#     user_type="ADM"
# )