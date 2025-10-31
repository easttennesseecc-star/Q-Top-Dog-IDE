import sqlite3

conn = sqlite3.connect('q_ide.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute('''
    SELECT 
        tier_id, name, price, 
        code_execution, custom_llms, webhooks,
        team_members, hipaa_ready, sso_saml, 
        on_premise_deploy, api_keys_limit,
        daily_call_limit, daily_llm_requests
    FROM membership_tiers 
    ORDER BY price
''')

rows = cur.fetchall()

print("\n" + "="*140)
print("CURRENT DATABASE TIER CONFIGURATION")
print("="*140)
print(f"{'TIER':<20s} | {'PRICE':<8s} | {'CODE':<6s} | {'LLM':<6s} | {'HOOK':<6s} | {'TEAMS':<8s} | {'CALLS':<8s} | {'HIPAA':<6s} | {'SSO':<6s} | {'ON-PREM':<8s}")
print("-"*140)

for row in rows:
    print(f"{row['tier_id']:<20s} | ${row['price']:<7.0f} | {'✅' if row['code_execution'] else '❌':<6s} | {'✅' if row['custom_llms'] else '❌':<6s} | {'✅' if row['webhooks'] else '❌':<6s} | {str(row['team_members']):<8s} | {row['daily_call_limit']:<8d} | {'✅' if row['hipaa_ready'] else '❌':<6s} | {'✅' if row['sso_saml'] else '❌':<6s} | {'✅' if row['on_premise_deploy'] else '❌':<8s}")

print("="*140)

conn.close()
