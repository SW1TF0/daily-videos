"""Render a carousel post (photo slides) from a post JSON.

python3 src/build_post.py posts/<name>.json   -> out/<id>/slide_*.jpg + out/<id>/meta.json
Post JSON: id, bg, mascot, slides: [{type: cover|point|cta, ...}], caption, hashtags, service, format
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    post_path = sys.argv[1]
    post = json.load(open(post_path, encoding='utf-8'))
    work = os.path.join(ROOT, 'out', post['id'])
    r = subprocess.run(['node', os.path.join(ROOT, 'src', 'render_slides.js'), post_path, work], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit('slide render failed')
    files = json.loads(r.stdout.strip().splitlines()[-1])
    cover = next((s for s in post['slides'] if s.get('type') == 'cover'), {})
    meta = {k: post.get(k) for k in ('id', 'caption', 'hashtags', 'service', 'format')}
    meta.update({'kind': 'carousel', 'hook': cover.get('hook', ''), 'photos': files})
    json.dump(meta, open(os.path.join(work, 'meta.json'), 'w'), ensure_ascii=False, indent=2)
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == '__main__':
    main()
