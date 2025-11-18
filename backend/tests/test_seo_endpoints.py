import os
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

def test_robots_txt_contains_canonical_and_sitemap():
    os.environ['CANONICAL_HOST'] = 'topdog-ide.com'
    os.environ['SITEMAP_HOSTS'] = 'www.topdog-ide.com'
    r = client.get('/robots.txt')
    assert r.status_code == 200
    body = r.text.strip().splitlines()
    # Basic structure
    assert any(line.startswith('User-agent:') for line in body)
    assert any('topdog-ide.com' in line for line in body), 'Canonical host missing'
    # Should not reference q-ide.com anymore
    assert all('q-ide.com' not in line for line in body), 'Legacy domain still present'


def test_sitemap_xml_has_topdog_urls():
    os.environ['CANONICAL_HOST'] = 'topdog-ide.com'
    os.environ['SITEMAP_HOSTS'] = 'www.topdog-ide.com'
    r = client.get('/sitemap.xml')
    assert r.status_code == 200
    text = r.text
    assert 'https://topdog-ide.com/' in text
    assert 'https://www.topdog-ide.com/' in text or 'www.topdog-ide.com' in text
    # No legacy brand main host
    assert 'https://q-ide.com/' not in text
