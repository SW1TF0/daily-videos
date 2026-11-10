"""ElevenLabs credit budget: how many videos per day we can afford until the monthly reset.

python3 src/budget.py
"""
import datetime as dt, json, subprocess

PER_VIDEO = 750  # measured: voice + sound effects of one 30-45 s video (music comes from assets/music)

d = json.loads(subprocess.run(['curl', '-sS', 'https://api.elevenlabs.io/v1/user/subscription', '-H', 'xi-api-key: proxy-injected'],
                              capture_output=True, text=True).stdout)
used, limit = d.get('character_count', 0), d.get('character_limit', 0)
reset = dt.datetime.fromtimestamp(d.get('next_character_count_reset_unix', 0), dt.timezone.utc)
days = max(1, (reset - dt.datetime.now(dt.timezone.utc)).days + 1)
left = max(0, limit - used)
print(json.dumps({'tier': d.get('tier'), 'used': used, 'limit': limit, 'left': left, 'resets': reset.date().isoformat(),
                  'days_left': days, 'credits_per_day': left // days, 'videos_per_day_affordable': round(left / days / PER_VIDEO, 1)}))
